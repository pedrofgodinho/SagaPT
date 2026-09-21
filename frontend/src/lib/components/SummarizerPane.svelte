<script lang="ts">
  import type { SummarizerPane } from "$lib/types";
  import { marked } from "marked";
  import DOMPurify from "dompurify";

  let { pane }: { pane: SummarizerPane } = $props();

  // Render markdown and sanitize to prevent XSS from LLM-generated HTML
  function md(text: string): string {
    return DOMPurify.sanitize(marked(text, { async: false }) as string);
  }
</script>

<div class="flex flex-col gap-1.5">
  <div class="flex items-center gap-1.5">
    <span class="text-[12px] font-semibold uppercase tracking-widest text-amber">summarizer</span>
    {#if pane.kb_key}
      <span class="text-[11px] text-faint truncate font-mono">{pane.kb_key}</span>
    {/if}
  </div>
  <div
    class="border-l-2 border-amber px-2.5 py-1.5 bg-amber/5 rounded-r-sm prose-content text-[14px] text-amber/90"
  >
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html md(pane.summary)}
  </div>
</div>
