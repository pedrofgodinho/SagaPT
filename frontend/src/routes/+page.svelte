<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import AppHeader from "$lib/components/AppHeader.svelte";
  import RunList from "$lib/components/RunList.svelte";
  import RightPanel from "$lib/components/RightPanel.svelte";
  import SubgraphPane from "$lib/components/SubgraphPane.svelte";
  import MessagePane from "$lib/components/MessagePane.svelte";
  import AIMessagePane from "$lib/components/AIMessagePane.svelte";
  import {
    store,
    loadRuns,
    loadMermaid,
    selectRun,
    createRun,
    deleteRun,
    cancelRun,
    connectGlobal,
    cleanup,
  } from "$lib/runStore.svelte";
  import * as api from "$lib/api";
  import type { TargetProfile } from "$lib/types";

  // ── Status badge ───────────────────────────────────────────────────────────
  let selectedRun = $derived(store.runs.find((r) => r.run_id === store.selectedRunId));
  // The agent whose subgraph is currently running (for graph node highlighting).
  let activeAgent = $derived(
    store.subgraphs.reduce<string | null>((last, sg) => (sg.status === "running" ? sg.agent : last), null)
  );

  const statusBadge: Record<string, string> = {
    running: "bg-amber/15 text-amber",
    completed: "bg-green/15 text-green",
    failed: "bg-red/15 text-red",
    cancelled: "bg-muted/15 text-muted",
    pending: "bg-faint/15 text-faint",
  };

  // ── New run modal ──────────────────────────────────────────────────────────
  let showModal = $state(false);
  let targets = $state<TargetProfile[]>([]);
  let selectedTargetKey = $state("");
  let defaultHumanPrompt = $state("");
  let newRunName = $state("");
  let newHumanPrompt = $state("");
  let loadingDefaults = $state(false);
  let creating = $state(false);

  function applyTargetPrompt() {
    const t = targets.find((x) => x.key === selectedTargetKey);
    newHumanPrompt = t?.human_prompt ?? defaultHumanPrompt;
  }

  $effect(() => {
    if (!showModal) return;
    loadingDefaults = true;
    Promise.all([api.getDefaultConfig(), api.getTargets()])
      .then(([cfg, ts]) => {
        targets = ts;
        defaultHumanPrompt = cfg.planner.prompts.human;
        if (!selectedTargetKey && ts.length > 0) selectedTargetKey = ts[0].key;
        applyTargetPrompt();
      })
      .finally(() => { loadingDefaults = false; });
  });

  function resetModal() {
    showModal = false;
    selectedTargetKey = "";
    newRunName = "";
    newHumanPrompt = "";
  }

  async function submitNewRun() {
    const target = targets.find((t) => t.key === selectedTargetKey);
    if (!target || creating) return;
    creating = true;
    try {
      await createRun(target, newHumanPrompt, newRunName || undefined);
      resetModal();
    } finally {
      creating = false;
    }
  }

  // ── Collapse/expand all ───────────────────────────────────────────────────
  let collapseSignal = $state(0);
  let expandSignal = $state(0);

  // ── Scroll-lock ───────────────────────────────────────────────────────────
  let mainEl = $state<HTMLElement | null>(null);
  let stickToBottom = $state(true);

  function onMainScroll() {
    if (!mainEl) return;
    const distFromBottom = mainEl.scrollHeight - mainEl.scrollTop - mainEl.clientHeight;
    stickToBottom = distFromBottom < 40;
  }

  $effect(() => {
    // Re-run whenever subgraph list or any pane list changes.
    store.subgraphs.forEach((sg) => sg.panes.length);
    if (stickToBottom && mainEl) {
      mainEl.scrollTop = mainEl.scrollHeight;
    }
  });

  // ── Resize ────────────────────────────────────────────────────────────────
  let rightWidth = $state(288);
  let resizing = $state(false);

  function startResize(e: MouseEvent) {
    resizing = true;
    const startX = e.clientX;
    const startWidth = rightWidth;

    function onMove(e: MouseEvent) {
      rightWidth = Math.max(180, Math.min(600, startWidth - (e.clientX - startX)));
    }
    function onUp() {
      resizing = false;
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    }
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  onMount(async () => {
    connectGlobal();
    await Promise.all([loadRuns(), loadMermaid()]);
    if (store.runs.length > 0) selectRun(store.runs[0].run_id);
  });

  onDestroy(() => cleanup());

  // ── Cancel current run ────────────────────────────────────────────────────
  let cancelling = $state(false);
  async function onCancelSelected() {
    if (!selectedRun || cancelling) return;
    cancelling = true;
    try {
      await cancelRun(selectedRun.run_id);
    } finally {
      cancelling = false;
    }
  }

  // A run has real activity to show once at least one subgraph exists.
  let hasActivity = $derived(store.subgraphs.length > 0);
  let selectedActive = $derived(
    selectedRun && (selectedRun.status === "pending" || selectedRun.status === "running")
  );
</script>

<div class="flex flex-col h-screen overflow-hidden" class:select-none={resizing}>
  <AppHeader>
    {#if selectedRun}
      <span class="text-[13px] text-muted">{selectedRun.target}</span>
      <span
        class="text-[11px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full {statusBadge[selectedRun.status] ?? 'bg-faint/15 text-faint'}"
      >
        {selectedRun.status}
      </span>
      {#if selectedActive}
        <button
          class="text-[11px] font-semibold uppercase tracking-widest text-red px-2 py-0.5 border border-red/30 rounded hover:border-red/60 hover:bg-red/10 transition-colors disabled:opacity-40"
          disabled={cancelling}
          onclick={onCancelSelected}
        >
          {cancelling ? "cancelling…" : "cancel run"}
        </button>
      {/if}
    {/if}
  </AppHeader>

  <div class="flex flex-1 overflow-hidden">
    <!-- Left: run list -->
    <div class="w-56 flex-shrink-0">
      <RunList
        runs={store.runs}
        selectedId={store.selectedRunId}
        onselect={selectRun}
        onnewrun={() => (showModal = true)}
        ondelete={deleteRun}
      />
    </div>

    <!-- Center: subgraph feed -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Toolbar -->
      {#if store.subgraphs.some((sg) => sg.agent !== "planner")}
        <div class="flex items-center gap-2 px-6 py-1.5 border-b border-border flex-shrink-0">
          <button
            class="text-[11px] font-semibold uppercase tracking-widest text-muted hover:text-text transition-colors px-1.5 py-0.5"
            onclick={() => (collapseSignal += 1)}
          >collapse all</button>
          <span class="text-border">·</span>
          <button
            class="text-[11px] font-semibold uppercase tracking-widest text-muted hover:text-text transition-colors px-1.5 py-0.5"
            onclick={() => (expandSignal += 1)}
          >expand all</button>
        </div>
      {/if}
      <main
        bind:this={mainEl}
        onscroll={onMainScroll}
        class="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-2"
      >
        {#if selectedRun && selectedRun.error}
          <div class="border border-red/40 bg-red/10 rounded p-3 flex flex-col gap-1">
            <span class="text-[11px] font-bold uppercase tracking-widest text-red">error</span>
            <pre class="text-[13px] text-text whitespace-pre-wrap font-mono">{selectedRun.error}</pre>
          </div>
        {/if}
        {#if selectedRun && selectedActive && !hasActivity}
          <div class="flex flex-col items-center justify-center gap-3 py-16 text-muted">
            <div class="w-6 h-6 border-2 border-amber/30 border-t-amber rounded-full animate-spin"></div>
            <span class="text-[13px]">Spinning up infrastructure…</span>
            <span class="text-[12px] text-faint">Starting a fresh ZAP container and loading the graph. This can take ~30s.</span>
          </div>
        {/if}
        {#each store.subgraphs as subgraph (subgraph.id)}
          {#if subgraph.agent === "planner"}
            {#each subgraph.panes as pane}
              <div class="py-1 px-1">
                {#if pane.type === "message"}
                  <MessagePane {pane} />
                {:else if pane.type === "ai"}
                  <AIMessagePane {pane} expandedAgentCalls={true} />
                {/if}
              </div>
            {/each}
          {:else}
            <SubgraphPane {subgraph} {collapseSignal} {expandSignal} />
          {/if}
        {/each}
      </main>
    </div>

    <!-- Resize handle -->
    <div
      class="w-1 flex-shrink-0 relative cursor-col-resize group"
      role="separator"
      aria-orientation="vertical"
      tabindex="0"
      onmousedown={startResize}
    >
      <div
        class="absolute inset-y-0 left-0 w-px transition-colors {resizing
          ? 'bg-green/60'
          : 'bg-border group-hover:bg-green/40'}"
      ></div>
    </div>

    <!-- Right: graph + KB (resizable) -->
    <div class="flex-shrink-0 overflow-hidden" style="width: {rightWidth}px">
      <RightPanel mermaid={store.mermaidDiagram} kbKeys={store.kbKeys} runId={store.selectedRunId} {activeAgent} />
    </div>
  </div>
</div>

<!-- New run modal -->
{#if showModal}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
    role="button"
    tabindex="0"
    aria-label="Close modal"
    onclick={resetModal}
    onkeydown={(e) => { if (e.key === "Enter" || e.key === " " || e.key === "Escape") resetModal(); }}
  >
    <div
      class="bg-bg-elevated border border-border rounded p-5 w-[520px] flex flex-col gap-4"
      role="dialog"
      aria-modal="true"
      aria-label="New run"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
    >
      <span class="text-[14px] font-semibold text-text">new run</span>
      <input
        type="text"
        placeholder="Run name (auto-generated if blank)"
        bind:value={newRunName}
        onkeydown={(e) => e.key === "Enter" && submitNewRun()}
        class="bg-bg border border-border rounded px-2 py-1.5 text-[14px] text-text focus:outline-none focus:border-green/60"
      />
      <select
        bind:value={selectedTargetKey}
        onchange={applyTargetPrompt}
        disabled={loadingDefaults}
        class="bg-bg border border-border rounded px-2 py-1.5 text-[14px] text-text focus:outline-none focus:border-green/60 font-mono disabled:opacity-40"
      >
        {#each targets as t (t.key)}
          <option value={t.key}>{t.label} — {t.target}</option>
        {/each}
      </select>
      <span class="text-[11px] text-muted font-semibold uppercase tracking-widest">planner prompt</span>
      <textarea
        rows="6"
        bind:value={newHumanPrompt}
        disabled={loadingDefaults}
        class="bg-bg border border-border rounded px-2 py-1.5 text-[13px] text-text focus:outline-none focus:border-green/60 font-mono resize-y disabled:opacity-40"
      ></textarea>
      <div class="flex gap-2 justify-end">
        <button
          class="text-[13px] text-muted px-3 py-1.5 border border-border rounded hover:text-text transition-colors"
          onclick={resetModal}
        >
          cancel
        </button>
        <button
          class="text-[13px] text-green px-3 py-1.5 border border-green/30 rounded hover:border-green/60 transition-colors disabled:opacity-40"
          disabled={creating || !selectedTargetKey}
          onclick={submitNewRun}
        >
          {creating ? "starting…" : "start"}
        </button>
      </div>
    </div>
  </div>
{/if}
