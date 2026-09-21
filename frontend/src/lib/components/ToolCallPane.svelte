<script lang="ts">
  import type { ToolCallPane } from "$lib/types";

  let { pane }: { pane: ToolCallPane } = $props();

  let resultOpen = $state(false);
</script>

<div class="flex flex-col gap-2">
  <!-- Header -->
  <div class="flex items-center gap-1.5">
    <span class="text-cyan text-[14px]">⚙</span>
    <span class="text-cyan font-semibold text-[14px]">{pane.tool_name}</span>
  </div>

  <!-- Args -->
  <div class="flex flex-col gap-1">
    <div class="text-[12px] font-semibold uppercase tracking-widest text-muted">args</div>
    <pre
      class="bg-bg border border-border-subtle rounded-sm px-2 py-1.5 text-[13px] text-muted whitespace-pre-wrap break-all"
    >{JSON.stringify(pane.args, null, 2)}</pre>
  </div>

  <!-- Result (collapsible) -->
  {#if pane.result !== undefined}
    <div class="flex flex-col gap-1">
      <button
        class="flex items-baseline gap-1.5 text-left text-muted hover:text-text"
        onclick={() => (resultOpen = !resultOpen)}
      >
        <span
          class="text-sm transition-transform duration-150 inline-block"
          class:rotate-90={resultOpen}
        >›</span>
        <span class="text-[12px] font-semibold uppercase tracking-widest flex-shrink-0">result</span>
        {#if !resultOpen}
          <span class="text-[13px] text-faint truncate">
            {pane.result.slice(0, 100)}{pane.result.length > 100 ? "…" : ""}
          </span>
        {/if}
      </button>
      {#if resultOpen}
        <pre
          class="bg-bg border border-border-subtle rounded-sm px-2 py-1.5 text-[13px] text-muted whitespace-pre-wrap break-all max-h-48 overflow-y-auto"
        >{pane.result}</pre>
      {/if}
    </div>
  {/if}

</div>
