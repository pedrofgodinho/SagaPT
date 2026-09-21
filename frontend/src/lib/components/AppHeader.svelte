<script lang="ts">
  // Slot for future actions/controls in the header
  let { children }: { children?: import("svelte").Snippet } = $props();
</script>

<header class="h-11 flex items-center justify-between px-4 border-b border-border bg-bg-elevated flex-shrink-0">
  <div class="flex items-center gap-2">
    <span class="text-green font-bold text-[15px] tracking-tight">saga</span>
    <span class="text-faint text-[15px]">/</span>
    <span class="text-muted text-[15px]">pentest automation</span>
  </div>

  <div class="flex items-center gap-3">
    {@render children?.()}
  </div>
</header>
