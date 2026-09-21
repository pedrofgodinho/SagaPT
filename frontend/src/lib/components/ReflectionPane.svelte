<script lang="ts">
  import type { ReflectionPane } from "$lib/types";
  import { marked } from "marked";
  import DOMPurify from "dompurify";

  let { pane }: { pane: ReflectionPane } = $props();

  let reasoningOpen = $state(false);

  // Render markdown and sanitize to prevent XSS from LLM-generated HTML
  function md(text: string | undefined): string {
    if (!text) return "";
    return DOMPurify.sanitize(marked(text, { async: false }) as string);
  }
</script>

<div class="flex flex-col gap-2">
  <div class="flex items-center gap-1.5">
    <span class="text-purple text-[13px]">⏸</span>
    <span class="text-[12px] font-semibold uppercase tracking-widest text-purple">reflection checkpoint</span>
  </div>

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
    <div class="border-l-2 border-purple px-2.5 py-1.5 bg-purple/5 rounded-r-sm prose-content text-[14px] text-purple/90">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html md(pane.content)}
    </div>
  {/if}
</div>
