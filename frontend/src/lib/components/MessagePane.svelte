<script lang="ts">
  import type { MessagePane } from "$lib/types";

  let { pane }: { pane: MessagePane } = $props();
</script>

<div class="flex flex-col gap-1">
  <div
    class="text-[12px] font-semibold uppercase tracking-widest"
    class:text-purple={pane.role === "system"}
    class:text-blue={pane.role === "human"}
  >
    {pane.role}
  </div>
  <div class="text-text whitespace-pre-wrap break-words">{pane.content}</div>
</div>
