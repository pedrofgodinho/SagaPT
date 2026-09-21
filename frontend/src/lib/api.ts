/**
 * Typed API client for the SagaPT backend.
 *
 * All paths are relative — Vite's dev proxy forwards /api/* to localhost:8080.
 */

import type { Run, KBEntry, RunConfig, TargetProfile } from "./types";

const BASE = "/api/v1";

async function _json<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, init);
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function listRuns(): Promise<Run[]> {
  return _json<Run[]>(`${BASE}/runs`);
}

export async function createRun(config: RunConfig): Promise<Run> {
  return _json<Run>(`${BASE}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
}

export async function deleteRun(runId: string): Promise<void> {
  const res = await fetch(`${BASE}/runs/${runId}`, { method: "DELETE" });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
}

export async function cancelRun(runId: string): Promise<void> {
  const res = await fetch(`${BASE}/runs/${runId}/cancel`, { method: "POST" });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
}

export async function getDefaultConfig(): Promise<RunConfig> {
  return _json<RunConfig>(`${BASE}/config`);
}

export async function getTargets(): Promise<TargetProfile[]> {
  return _json<TargetProfile[]>(`${BASE}/targets`);
}

export async function getKBEntry(runId: string, key: string): Promise<KBEntry> {
  // Keys may contain slashes; {key:path} on the backend captures them literally,
  // so only encode non-slash characters.
  const encodedKey = key.split("/").map(encodeURIComponent).join("/");
  const r = await _json<{ run_id: string; key: string; value: string }>(
    `${BASE}/runs/${runId}/kb/entries/${encodedKey}`,
  );
  return { key: r.key, value: r.value };
}

export async function getMermaid(): Promise<string> {
  const r = await _json<{ mermaid: string }>(`${BASE}/graph/mermaid`);
  return r.mermaid;
}
