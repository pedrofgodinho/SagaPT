<script lang="ts">
  import type { AIMessagePane } from "$lib/types";
  import { marked } from "marked";
  import DOMPurify from "dompurify";

  let {
    pane,
    expandedAgentCalls = false,
  }: { pane: AIMessagePane; expandedAgentCalls?: boolean } = $props();

  let reasoningOpen = $state(false);

  // Render markdown and sanitize to prevent XSS from LLM-generated HTML
  function md(text: string | undefined): string {
    if (!text) return "";
    return DOMPurify.sanitize(marked(text, { async: false }) as string);
  }
</script>

<div class="flex flex-col gap-2">
  <div class="text-[12px] font-semibold uppercase tracking-widest text-green">{pane.node ?? "assistant"}</div>

  {#if pane.reasoning}
    <div class="border border-border-subtle rounded-sm overflow-hidden">
      <button
        class="flex items-baseline gap-1.5 w-full px-2 py-1 bg-bg-elevated hover:bg-bg-hover text-left"
        onclick={() => (reasoningOpen = !reasoningOpen)}
      >
        <span
          class="text-sm text-muted transition-transform duration-150 inline-block"
          class:rotate-90={reasoningOpen}
        >›</span>
        <span class="text-[12px] font-semibold uppercase tracking-widest text-amber flex-shrink-0">
          reasoning
        </span>
        {#if !reasoningOpen}
          <span class="text-[13px] text-muted truncate">
            {pane.reasoning.slice(0, 80)}{pane.reasoning.length > 80 ? "…" : ""}
          </span>
        {/if}
      </button>
      {#if reasoningOpen}
        <div class="px-2 py-2 bg-bg-raised italic text-[14px] text-dim prose-reasoning">
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html md(pane.reasoning)}
        </div>
      {/if}
    </div>
  {/if}

  {#if pane.content}
    <div class="prose-content text-[15px]">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html md(pane.content)}
    </div>
  {/if}

  {#if pane.tool_calls && pane.tool_calls.length > 0}
    <div class="flex flex-col gap-2">
      {#each pane.tool_calls as tc}
        {#if expandedAgentCalls}
          <div class="border border-border rounded-sm overflow-hidden">
            <div class="flex items-center gap-1.5 px-2 py-1.5 bg-bg-elevated border-l-2 border-cyan">
              <span class="text-cyan text-[13px] flex-shrink-0">⚡</span>
              <span class="text-cyan font-bold text-[14px]">{tc.name}</span>
            </div>
            <div class="px-3 py-2 prose-content text-[14px]">
              {#if typeof tc.args.instructions === "string"}
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html md(tc.args.instructions)}
              {:else}
                <span class="text-muted font-mono text-[13px]">{JSON.stringify(tc.args)}</span>
              {/if}
            </div>
          </div>
        {:else}
          <div class="flex items-baseline gap-1.5 px-2 py-1 bg-bg-elevated rounded-sm border-l-2 border-cyan">
            <span class="text-cyan text-[13px] flex-shrink-0">⚡</span>
            <span class="text-cyan font-semibold text-[14px] flex-shrink-0">{tc.name}</span>
            <span class="text-muted text-[13px] truncate">{JSON.stringify(tc.args)}</span>
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>
