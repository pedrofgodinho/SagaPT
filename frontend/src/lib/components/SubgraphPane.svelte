<script lang="ts">
  import type { Subgraph } from "$lib/types";
  import MessagePane from "./MessagePane.svelte";
  import AIMessagePane from "./AIMessagePane.svelte";
  import ToolCallPane from "./ToolCallPane.svelte";
  import SummarizerPane from "./SummarizerPane.svelte";
  import ReflectionPane from "./ReflectionPane.svelte";

  let {
    subgraph,
    collapseSignal = 0,
    expandSignal = 0,
  }: { subgraph: Subgraph; collapseSignal?: number; expandSignal?: number } = $props();

  let collapsed = $state(false);

  // Auto-collapse when the subgraph reaches a terminal state.
  $effect(() => {
    if (
      subgraph.status === "completed" ||
      subgraph.status === "failed" ||
      subgraph.status === "cancelled"
    ) {
      collapsed = true;
    }
  });

  // Respond to external collapse/expand all signals (ignore initial zero value).
  $effect(() => { if (collapseSignal > 0) collapsed = true; });
  $effect(() => { if (expandSignal > 0) collapsed = false; });

  const borderColor: Record<string, string> = {
    running: "border-l-amber",
    completed: "border-l-green",
    failed: "border-l-red",
    pending: "border-l-faint",
    cancelled: "border-l-muted",
  };

  const badgeStyle: Record<string, string> = {
    running: "bg-amber/15 text-amber",
    completed: "bg-green/15 text-green",
    failed: "bg-red/15 text-red",
    pending: "bg-bg text-muted",
    cancelled: "bg-bg text-muted",
  };

  let lastPane = $derived(
    [...subgraph.panes].reverse().find((p) => !(p.type === "message" && p.role === "system"))
  );

  // Outer alignment: right-aligned cards sit on the right with a left margin
  let align = $derived(subgraph.align ?? "left");
</script>

<div class="flex" class:justify-end={align === "right"}>
  <div
    class="w-full border border-border rounded-md overflow-hidden {subgraph.status === 'running' ? 'bg-amber/10 border-l-4' : 'bg-bg-raised border-l-2'} {borderColor[subgraph.status]}"
    class:ml-auto={align === "right"}
  >
    <!-- Header -->
    <button
      class="flex items-baseline gap-2 w-full px-3 py-2 bg-bg-elevated hover:bg-bg-hover text-left"
      class:border-b={!collapsed}
      class:border-border-subtle={!collapsed}
      onclick={() => (collapsed = !collapsed)}
    >
      <span
        class="text-base text-muted transition-transform duration-150 inline-block leading-none"
        class:rotate-90={!collapsed}
      >›</span>
      <span class="font-bold text-[14px] text-text flex-shrink-0">{subgraph.agent}</span>
      <span
        class="text-[11px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded-full flex-shrink-0 {badgeStyle[subgraph.status]}"
        class:animate-pulse={subgraph.status === 'running'}
      >
        {subgraph.status}
      </span>
      <span class="text-[13px] text-muted truncate flex-1">{subgraph.instructions}</span>
    </button>

    <!-- Expanded body -->
    {#if !collapsed}
      <div class="p-3 flex flex-col">
        {#each subgraph.panes as pane, i}
          <div
            class="flex gap-2.5"
            class:flex-row-reverse={pane.align === "right"}
          >
            <div class="w-0.5 bg-border rounded-full flex-shrink-0"></div>
            <div class="flex-1 min-w-0" class:text-right={pane.align === "right"}>
              {#if pane.type === "message"}
                <MessagePane {pane} />
              {:else if pane.type === "ai"}
                <AIMessagePane {pane} />
              {:else if pane.type === "tool_call"}
                <ToolCallPane {pane} />
              {:else if pane.type === "summarizer"}
                <SummarizerPane {pane} />
              {:else if pane.type === "reflection"}
                <ReflectionPane {pane} />
              {/if}
            </div>
          </div>
          {#if i < subgraph.panes.length - 1}
            <div class="h-px bg-border-subtle my-2 ml-3"></div>
          {/if}
        {/each}
      </div>

    <!-- Collapsed: show full last pane, no clipping -->
    {:else if lastPane}
      <div class="px-3 py-2">
        {#if lastPane.type === "message"}
          <MessagePane pane={lastPane} />
        {:else if lastPane.type === "ai"}
          <AIMessagePane pane={lastPane} />
        {:else if lastPane.type === "tool_call"}
          <ToolCallPane pane={lastPane} />
        {:else if lastPane.type === "summarizer"}
          <SummarizerPane pane={lastPane} />
        {:else if lastPane.type === "reflection"}
          <ReflectionPane pane={lastPane} />
        {/if}
      </div>
    {/if}
  </div>
</div>
