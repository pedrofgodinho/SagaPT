set shell := ["/usr/bin/bash", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

log_level := env("LOG_LEVEL", "INFO")


# Running `just` without arguments will show available commands
default:
    @just --list


# Start the Hackergram target container attached (Ctrl-C to stop)
hackergram:
    docker compose up hackergram


# Start the DVWA target container attached (Ctrl-C to stop)
dvwa:
    docker compose up dvwa


# Start the OWASP Juice Shop target container attached (Ctrl-C to stop)
juiceshop:
    docker compose up juiceshop


# Run a local model via llama.cpp's llama-server (OpenAI-compatible API on :8081;
# 8080 is taken by `just serve`). --jinja enables the model's chat template so
# OpenAI tool-calling works — Saga's agents/summarizer need it. `offload` and
# `sampling` default to the Qwen3.6-35B-A3B (MoE) tuned set; the dense-model
# wrappers below override them. Ctrl-C to stop.
# Usage: just llama <hf-model> [ctx] [offload] [sampling]   (ctx one of 64000 / 128000 / 256000)
llama model ctx="128000" offload="--n-cpu-moe 25" sampling="--temp 0.6 --top-p 0.95 --top-k 20":
    llama-server -hf {{model}} -c {{ctx}} --port 8081 --jinja -ngl 99 {{offload}} -ctk q4_0 -ctv q4_0 -fa on -b 2048 -ub 2048 --load-mode none --no-context-shift -np 1 {{sampling}}


# Convenience wrappers for the two tested Qwen3.6-35B-A3B models (default ctx 128000).
# MoE (35B total / 3B active): ~25 expert layers stay on CPU (--n-cpu-moe 25) to fit 16 GB VRAM.
llama-hauhau ctx="128000": (llama "HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:Q4_K_M" ctx)

llama-qwen ctx="128000": (llama "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M" ctx)


# Older-than-1y baselines to benchmark against the current Qwen3.6. These run via
# OLLAMA, not llama.cpp: this llama.cpp build's tool-call parser 500-crashes on Llama
# 3.1's multi-tool-call output ("peg-native format" error) and can't parse Gemma 3's
# tool_code blocks, whereas Ollama's per-model tool parsers handle both cleanly (Qwen3.6
# still uses llama.cpp above). The Ollama daemon serves them on :11434; these recipes just
# fetch the models. Point saga.toml's local sections at model_provider="ollama" (see its header).
# Llama 3.1 8B Instruct (Jul 2024), q8_0 (~8.5 GB, near-lossless) — native Ollama tool support.
ollama-llama3:
    ollama pull llama3.1:8b-instruct-q8_0

# Gemma 3 12B Instruct (Mar 2025) — community tool-calling variant (Gemma 3 has no native
# tools role; this Modelfile adds the <tool_call> format Ollama parses).
ollama-gemma3:
    ollama pull PetrosStav/gemma3-tools:12b


# Start the SagaPT API server natively on http://127.0.0.1:8080 (Ctrl-C to stop)
[unix]
serve:
    cd saga && LOG_LEVEL={{log_level}} uv run python src/main.py serve

[windows]
serve:
    Push-Location saga; $env:LOG_LEVEL = "{{log_level}}"; uv run python src/main.py serve; Pop-Location


# Start the API server in single-agent baseline mode (one monolithic agent, no
# multi-agent orchestration). For comparing against the multi-agent architecture.
[unix]
serve-single:
    cd saga && LOG_LEVEL={{log_level}} SAGA_CONFIG=saga_single_agent.toml uv run python src/main.py serve

[windows]
serve-single:
    Push-Location saga; $env:LOG_LEVEL = "{{log_level}}"; $env:SAGA_CONFIG = "saga_single_agent.toml"; uv run python src/main.py serve; Pop-Location



# Launch the same run config N times sequentially for replicability (e.g.
# `just replicate --start 1 --end 10 --name SQLi`). API server must already
# be running (`just serve` in another terminal).
[unix]
replicate *args:
    cd saga && LOG_LEVEL={{log_level}} uv run python src/main.py replicate {{args}}

[windows]
replicate *args:
    Push-Location saga; $env:LOG_LEVEL = "{{log_level}}"; uv run python src/main.py replicate {{args}}; Pop-Location


# Start the frontend dev server on http://localhost:5173 (Ctrl-C to stop)
[unix]
frontend:
    cd frontend && npm run dev

[windows]
frontend:
    Push-Location frontend; npm run dev; Pop-Location


# Start test infra (ZAP + nginx), run the full pytest suite, then tear infra down
[unix]
test:
    docker compose -f docker-compose.test.yml up -d
    until docker compose -f docker-compose.test.yml exec zaproxy curl -sf http://localhost:8080/JSON/core/view/version/ > /dev/null 2>&1; do sleep 2; done
    cd saga && uv run pytest -v; \
        status=$?; \
        docker compose -f docker-compose.test.yml down; \
        exit $status

[windows]
test:
    docker compose -f docker-compose.test.yml up -d
    $r=$false; while(-not $r){try{Invoke-RestMethod 'http://localhost:8080/JSON/core/view/version/' | Out-Null; $r=$true}catch{Start-Sleep 2}}
    Push-Location saga; uv run pytest -v; $code = $LASTEXITCODE; Pop-Location; docker compose -f docker-compose.test.yml down; exit $code


