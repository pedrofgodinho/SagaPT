"""Unit tests for the Ollama provider branch of ``model_factory.get_model``.

These construct real ``ChatOllama`` instances but never invoke them, so no
running Ollama daemon is required — construction does not open a connection.
"""

import pytest

from model_factory import ModelParameters, clear_fake_models, get_model


def _params(model_name: str, model_kwargs: dict | None = None) -> ModelParameters:
    return ModelParameters(
        provider="ollama",
        model_name=model_name,
        temperature=0,
        model_kwargs=model_kwargs or {},
    )


@pytest.fixture(autouse=True)
def _clear_caches():
    """Reset the module-global model caches around each test.

    ``get_model`` caches by ``(provider, model_name, temperature, model_kwargs)``
    but *not* by ``OLLAMA_BASE_URL`` (an env knob), so a stale cache entry would
    otherwise leak the base URL of one test into the next.
    """
    clear_fake_models()
    yield
    clear_fake_models()


def test_ollama_branch_builds_chat_ollama_with_default_base_url(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    model = get_model(_params("llama3.1"))
    assert type(model).__name__ == "ChatOllama"
    assert model.model == "llama3.1"
    assert model.base_url == "http://localhost:11434"


def test_ollama_base_url_env_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://gpu-box.local:11434")
    model = get_model(_params("qwen2.5"))
    assert model.base_url == "http://gpu-box.local:11434"


def test_ollama_model_kwargs_passthrough(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    model = get_model(_params("llama3.1", {"num_ctx": 4096}))
    assert model.num_ctx == 4096


def test_ollama_shares_rate_limiter_when_rps_set(monkeypatch):
    """The rate-limiter lift means ``SAGA_LLM_RPS`` applies to Ollama too."""
    monkeypatch.setenv("SAGA_LLM_RPS", "2.0")
    model = get_model(_params("mistral-nemo"))
    assert model.rate_limiter is not None


def _llamacpp_params(model_name: str, model_kwargs: dict | None = None) -> ModelParameters:
    return ModelParameters(
        provider="llamacpp",
        model_name=model_name,
        temperature=0.6,
        model_kwargs=model_kwargs or {},
    )


def test_llamacpp_branch_builds_chat_openai_with_default_base_url(monkeypatch):
    monkeypatch.delenv("LLAMACPP_BASE_URL", raising=False)
    monkeypatch.delenv("LLAMACPP_API_KEY", raising=False)
    model = get_model(_llamacpp_params("unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M"))
    assert type(model).__name__ == "ChatOpenAI"
    assert model.model_name == "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M"
    # ChatOpenAI stores the base under openai_api_base; it defaults to :8081, the
    # non-8080 port (8080 is the Saga API server).
    assert str(model.openai_api_base) == "http://localhost:8081/v1"
    assert model.temperature == 0.6
    # Required for usage_metadata to survive astream_events' streaming path —
    # ChatOpenAI omits it on streamed responses otherwise (see model_factory.py).
    assert model.stream_usage is True


def test_llamacpp_base_url_env_override(monkeypatch):
    monkeypatch.setenv("LLAMACPP_BASE_URL", "http://gpu-box.local:9000/v1")
    model = get_model(_llamacpp_params("foo"))
    assert str(model.openai_api_base) == "http://gpu-box.local:9000/v1"


def test_llamacpp_model_kwargs_passthrough(monkeypatch):
    monkeypatch.delenv("LLAMACPP_BASE_URL", raising=False)
    model = get_model(_llamacpp_params("foo", {"max_tokens": 512}))
    assert model.max_tokens == 512


def test_unknown_provider_still_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_model(
            ModelParameters(
                provider="not-a-provider",
                model_name="x",
                temperature=0,
                model_kwargs={},
            )
        )
