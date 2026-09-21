<script lang="ts">
  import type { Run, RunStatus } from "$lib/types";

  let {
    runs,
    selectedId,
    onselect,
    onnewrun,
    ondelete,
  }: {
    runs: Run[];
    selectedId?: string | null;
    onselect?: (id: string) => void;
    onnewrun?: () => void;
    ondelete?: (id: string) => void;
  } = $props();

  const statusDot: Record<RunStatus, string> = {
    running: "bg-amber",
    completed: "bg-green",
    failed: "bg-red",
    pending: "bg-faint",
    cancelled: "bg-muted",
  };
</script>

<aside class="flex flex-col border-r border-border bg-bg h-full overflow-hidden">
  <div class="px-3 py-2.5 border-b border-border flex items-center justify-between flex-shrink-0">
    <span class="text-[12px] font-semibold uppercase tracking-widest text-muted">runs</span>
    <button
      class="text-[12px] font-semibold uppercase tracking-widest text-green hover:text-text px-1.5 py-0.5 rounded border border-green/30 hover:border-green/60 transition-colors"
      onclick={() => onnewrun?.()}
    >
      + new
    </button>
  </div>

  <ul class="flex-1 overflow-y-auto">
    {#each runs as run (run.run_id)}
      <li class="relative group">
        <button
          class="w-full flex flex-col gap-0.5 px-3 py-2.5 pr-7 text-left hover:bg-bg-elevated border-b border-border-subtle transition-colors"
          class:bg-bg-elevated={selectedId === run.run_id}
          class:border-l-2={selectedId === run.run_id}
          class:border-l-green={selectedId === run.run_id}
          onclick={() => onselect?.(run.run_id)}
        >
          <div class="flex items-center gap-1.5 min-w-0">
            <span class="w-1.5 h-1.5 rounded-full flex-shrink-0 {statusDot[run.status]}"></span>
            <span class="text-[13px] font-semibold text-text truncate">{run.target}</span>
          </div>
          <div class="flex flex-col pl-3">
            <span class="text-[12px] text-muted font-mono">{run.name}</span>
            <span class="text-[12px] text-muted">
              {new Date(run.started_at).toLocaleString("sv-SE", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" }).replaceAll("-", "/")}
            </span>
          </div>
        </button>
        <button
          class="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity text-muted hover:text-red text-[15px] w-5 h-5 flex items-center justify-center leading-none"
          title="Delete run"
          onclick={(e) => { e.stopPropagation(); ondelete?.(run.run_id); }}
        >×</button>
      </li>
    {/each}
  </ul>
</aside>
