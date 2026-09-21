# SagaPT

An LLM-driven web-application penetration-testing tool, built for a master's
thesis. A **Planner** LLM orchestrates specialised security agents (Recon, DAST,
Exploitation) in a two-level [LangGraph](https://langchain-ai.github.io/langgraph/),
driving OWASP ZAP against a target web app and recording findings in a shared
knowledge base.

This is a self-contained sample: the tool, the vulnerable targets, and a set of
20 recorded runs.

## Components

- **`saga/`** — the tool itself (Python 3.14, managed with [`uv`](https://docs.astral.sh/uv/)).
  FastAPI backend, the LangGraph agent graph, ZAP tooling, and a CLI. Each run
  spawns its own ephemeral ZAP container, so runs never share scanner state.
- **`frontend/`** — a SvelteKit web UI that streams a run live over SSE (agent
  turns, tool calls, the knowledge base). Optional — the tool runs headless too.
- **Targets** (`docker-compose.yml`) — three deliberately vulnerable apps to
  scan: **Hackergram** (custom), **DVWA**, and **OWASP Juice Shop**.
- **Recorded runs** — full traces, knowledge bases, and CSV exports, browsable
  without running anything: `saga/saga_runs_sample/` (20 runs against Hackergram)
  and `saga/saga_runs_juice_shop/` (14 runs against OWASP Juice Shop).

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/), [`just`](https://github.com/casey/just),
  Docker, and Node.js (only for the frontend).
- The default LLM is **Qwen3.6-35B-A3B served locally via
  [llama.cpp](https://github.com/ggml-org/llama.cpp)** — the same model used for
  the sample runs. You need `llama-server` on your `PATH`; the `just llama-qwen`
  recipe launches it (with `--jinja`, required for tool calling).
- `cp saga.secrets.env.example saga.secrets.env`. No API keys are required for
  the local model; fill in `LANGCHAIN_API_KEY` only if you want LangSmith tracing.

To use a cloud model (Vertex AI Gemini) or Ollama instead, change
`model_provider`/`model_name` in `saga/saga.toml` — see the provider notes at the
top of that file.

## Run it

Each `just` recipe runs attached, so start each in its own terminal:

```bash
just llama-qwen   # serve the Qwen model via llama.cpp on http://localhost:8081
just hackergram   # start a target (or: just dvwa / just juiceshop)
just serve        # API server on http://127.0.0.1:8080
just frontend     # optional web UI on http://localhost:5173
```

Then open the frontend and start a run, or drive the API directly
(`POST /api/v1/runs`). The default target is Hackergram (`saga/saga.toml`).

## CLI

Some commands need no server or infrastructure:

```bash
cd saga
uv run python src/main.py graph                                        # print the agent graph
uv run python src/main.py export --all --runs-dir saga_runs_sample     # Hackergram runs -> CSVs
uv run python src/main.py export --all --runs-dir saga_runs_juice_shop # Juice Shop run -> CSVs
```

`export` writes `invocations.csv`, `llm_calls.csv`, `findings.csv`, and
`run_summary.csv` under the run-set's `export/` directory for offline analysis.

## The sample runs

Each recorded run — under `saga/saga_runs_sample/<run>/` (Hackergram) or
`saga/saga_runs_juice_shop/<run>/` (Juice Shop) — contains `trace.json` (the full
event log plus parsed findings) and `knowledge_base/` (the agents' findings,
mirroring the agent hierarchy). No server or Docker needed to inspect them.
