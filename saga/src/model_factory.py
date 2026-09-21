import json
import os
import logging
from typing import List, Dict, Any, TypedDict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.rate_limiters import BaseRateLimiter, InMemoryRateLimiter
from langchain_core.tools import BaseTool


logger = logging.getLogger(__name__)


# Global caches to avoid redundant initializations
_model_cache: Dict[str, BaseChatModel] = {}
_tool_model_cache: Dict[str, Any] = {}

# Registry for fake models used in tests.
_fake_registry: Dict[str, BaseChatModel] = {}

# One shared rate limiter per model_name. Concurrent runs that use the same
# model share a single limiter automatically because the underlying model
# instance is cached by (provider, model_name, ...) — so the process-wide
# request rate for that model is what gets capped, not per-run.
_rate_limiter_cache: Dict[str, BaseRateLimiter] = {}


def _get_rate_limiter(model_name: str) -> BaseRateLimiter | None:
    """Return a shared ``InMemoryRateLimiter`` for *model_name* if enabled.

    Activated only when ``SAGA_LLM_RPS`` is set to a positive number
    (interpreted as requests-per-second, shared across all concurrent
    runs using this same model). Returns ``None`` when unset or ``0`` so
    the model runs with no client-side throttling.
    """
    try:
        rps = float(os.getenv("SAGA_LLM_RPS", "0"))
    except ValueError:
        logger.warning("SAGA_LLM_RPS is not a valid float; ignoring.")
        return None
    if rps <= 0:
        return None
    if model_name not in _rate_limiter_cache:
        # max_bucket_size allows small bursts to pass through unthrottled;
        # sustained load then converges to `rps`. Three seconds' worth is
        # roomy enough for start-of-run bursts without blowing quota.
        _rate_limiter_cache[model_name] = InMemoryRateLimiter(
            requests_per_second=rps,
            check_every_n_seconds=0.1,
            max_bucket_size=max(1, int(rps * 3)),
        )
        logger.info(
            "Rate limiter engaged for model '%s': %.2f req/s (shared across concurrent runs).",
            model_name, rps,
        )
    return _rate_limiter_cache[model_name]


def register_fake_model(name: str, model: BaseChatModel) -> None:
    """Register a fake model under *name* for use with ``provider="fake"``.

    Clears both model caches so subsequent ``get_model`` / ``get_tool_model``
    calls pick up the new registration.
    """
    _fake_registry[name] = model
    _model_cache.clear()
    _tool_model_cache.clear()


def clear_fake_models() -> None:
    """Remove all registered fake models and clear both caches."""
    _fake_registry.clear()
    _model_cache.clear()
    _tool_model_cache.clear()


class ModelParameters(TypedDict):
    """Typed configuration for a chat model."""

    provider: str
    model_name: str
    temperature: float
    model_kwargs: Dict[str, Any]
    """Provider-specific kwargs passed straight through to the underlying
    LangChain chat model constructor (e.g. ``{"thinking_level": "low"}`` for
    Gemini 3+ via ``google``). Not validated here — invalid keys/values
    surface as errors from the provider's own constructor, since the set of
    supported kwargs varies by provider and even by model version."""


def get_model(
    params: ModelParameters
) -> BaseChatModel:
    """
    Factory for language models. Abstracts provider-specific configurations.
    """
    global _model_cache

    # The cache key includes all configuration parameters to ensure a call
    # site requesting different model_kwargs never gets a stale cached model.
    kwargs_key = json.dumps(params.get('model_kwargs') or {}, sort_keys=True)
    cache_key = f"{params['provider']}:{params['model_name']}:t={params['temperature']}:kwargs={kwargs_key}"

    if cache_key in _model_cache:
        logger.debug("Cache hit for model '%s'.", cache_key)
        return _model_cache[cache_key]

    logger.info(
        "Initializing model: %s/%s (temperature=%s, model_kwargs=%s).",
        params['provider'],
        params['model_name'],
        params['temperature'],
        params.get('model_kwargs'),
    )

    model_kwargs: dict = dict(params.get('model_kwargs') or {})

    if params['provider'] == "fake":
        model_name = params['model_name']
        if model_name not in _fake_registry:
            raise ValueError(
                f"No fake model registered as '{model_name}'. "
                "Call register_fake_model() before building the graph."
            )
        model = _fake_registry[model_name]
        _model_cache[cache_key] = model
        return model

    # Shared client-side throttle for all real providers (google, ollama,
    # llamacpp). ChatGoogleGenerativeAI, ChatOllama and ChatOpenAI all accept a
    # ``rate_limiter`` constructor kwarg via BaseChatModel, so attach it once
    # here instead of per-branch.
    rate_limiter = _get_rate_limiter(params['model_name'])
    if rate_limiter is not None:
        model_kwargs["rate_limiter"] = rate_limiter

    if params['provider'] == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Vertex AI via Application Default Credentials — no API key. Requires
        # GOOGLE_APPLICATION_CREDENTIALS (path to an ADC/service-account JSON,
        # read by the google-auth library) and GOOGLE_CLOUD_PROJECT. Location
        # is required by Vertex AI and has no safe default (model availability
        # varies by region), so it must be set explicitly too.
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            logger.error("GOOGLE_APPLICATION_CREDENTIALS is not set.")
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set.")
        if not project:
            logger.error("GOOGLE_CLOUD_PROJECT is not set.")
            raise ValueError("GOOGLE_CLOUD_PROJECT is not set.")
        if not location:
            logger.error("GOOGLE_CLOUD_LOCATION is not set.")
            raise ValueError("GOOGLE_CLOUD_LOCATION is not set.")

        # SDK-level retry with exponential backoff — absorbs 429 bursts from
        # concurrent runs that briefly exceed per-minute quota, then settles.
        # Overridable via env for lower-quota tiers or debugging.
        try:
            max_retries = int(os.getenv("SAGA_LLM_MAX_RETRIES", "6"))
        except ValueError:
            max_retries = 6
            logger.warning("SAGA_LLM_MAX_RETRIES is not an integer; using default 6.")

        model = ChatGoogleGenerativeAI(
            model=params['model_name'],
            temperature=params['temperature'],
            vertexai=True,
            project=project,
            location=location,
            max_retries=max_retries,
            **model_kwargs
        )

    elif params['provider'] == "ollama":
        # Local models served by an Ollama daemon (native ChatOllama, not Vertex).
        # Base URL comes from OLLAMA_BASE_URL, defaulting to Ollama's own default.
        # Unlike the google branch there is no hard env validation: the local
        # default is safe, and a missing/unreachable server surfaces at invoke
        # time rather than at construction. Only tool-capable models (e.g.
        # llama3.1, qwen2.5) work here, since agents rely on bind_tools and the
        # summarizer on with_structured_output.
        from langchain_ollama import ChatOllama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        logger.info("Using Ollama server at %s.", base_url)
        model = ChatOllama(
            model=params['model_name'],
            temperature=params['temperature'],
            base_url=base_url,
            **model_kwargs,
        )

    elif params['provider'] == "llamacpp":
        # llama.cpp's llama-server exposes an OpenAI-compatible API, so we drive it
        # through langchain_openai.ChatOpenAI pointed at its /v1 endpoint rather
        # than a bespoke client. Base URL from LLAMACPP_BASE_URL (default
        # http://localhost:8081/v1 — note :8081; :8080 is the Saga API server).
        # llama-server ignores the API key unless started with --api-key, so a
        # placeholder satisfies ChatOpenAI's required-key field. As with ollama
        # there is no hard env validation — an unreachable/not-yet-loaded server
        # surfaces at invoke time. Tool calling only works when llama-server is
        # launched with --jinja (the `just llama` recipe passes it) so the model's
        # own chat template formats tool calls; agents rely on bind_tools and the
        # summarizer on with_structured_output. Per-request `temperature` here
        # overrides llama-server's --temp, so set it in saga.toml to the value the
        # model wants (e.g. 0.6 for Qwen3), not 0. `stream_usage=True` is required
        # because the graph drives the model via astream_events (token-level
        # streaming): unlike ChatGoogleGenerativeAI/ChatOllama, ChatOpenAI omits
        # usage_metadata on streamed responses unless this is set — confirmed by
        # comparing astream() with/without it against a live llama-server, this
        # was the cause of every llamacpp run reporting 0 tokens/null model_name.
        from langchain_openai import ChatOpenAI
        base_url = os.getenv("LLAMACPP_BASE_URL", "http://localhost:8081/v1")
        api_key = os.getenv("LLAMACPP_API_KEY", "sk-no-key-required")
        logger.info("Using llama.cpp (OpenAI-compatible) server at %s.", base_url)
        model = ChatOpenAI(
            model=params['model_name'],
            temperature=params['temperature'],
            base_url=base_url,
            api_key=api_key,
            stream_usage=True,
            **model_kwargs,
        )

    else:
        logger.error("Unknown model provider: '%s'.", params['provider'])
        raise ValueError(f"Unknown provider: {params['provider']}")

    logger.debug("Model kwargs applied: %s", model_kwargs)
    _model_cache[cache_key] = model
    logger.debug("Model cached under key '%s'.", cache_key)
    return model


def get_tool_model(
    params: ModelParameters,
    tools: List[BaseTool] = [],
) -> Any:
    """
    Factory for language models bound with tools.
    Separate cache allows the same base model to be bound to different toolsets.
    """
    global _tool_model_cache

    # We use the tool names in the key because tool objects themselves are not easily hashable
    tool_names = sorted([t.name for t in tools]) if tools else []
    kwargs_key = json.dumps(params.get('model_kwargs') or {}, sort_keys=True)
    cache_key = f"{params['provider']}:{params['model_name']}:kwargs={kwargs_key}:tools={','.join(tool_names)}"

    if cache_key in _tool_model_cache:
        logger.debug("Cache hit for tool-bound model '%s'.", cache_key)
        return _tool_model_cache[cache_key]

    logger.debug("Creating tool-bound model for key '%s'.", cache_key)

    # Get the base model from our primary factory
    base_model = get_model(params=params)

    if tools:
        logger.info(
            "Binding %d tool(s) to model '%s/%s': [%s].",
            len(tools),
            params['provider'],
            params['model_name'],
            ", ".join(tool_names),
        )
        model = base_model.bind_tools(tools)
    else:
        logger.debug("No tools to bind for model '%s/%s'.", params['provider'], params['model_name'])
        model = base_model

    _tool_model_cache[cache_key] = model
    logger.debug("Tool-bound model cached under key '%s'.", cache_key)
    return model
