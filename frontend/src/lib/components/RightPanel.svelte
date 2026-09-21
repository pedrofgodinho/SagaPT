<script lang="ts">
  import * as api from "$lib/api";
  import mermaid from "mermaid";
  import { onMount } from "svelte";

  let {
    mermaid: diagram = "",
    kbKeys = [],
    runId = null,
    activeAgent = null,
  }: { mermaid?: string; kbKeys?: string[]; runId?: string | null; activeAgent?: string | null } = $props();

  // ── KB file tree ──────────────────────────────────────────────────────────

  interface TreeNode {
    name: string;
    path: string;
    type: "dir" | "file";
    children?: TreeNode[];
  }

  function buildTree(paths: string[]): TreeNode[] {
    const root: TreeNode[] = [];
    for (const path of [...paths].sort()) {
      const parts = path.split("/");
      let nodes = root;
      for (let i = 0; i < parts.length; i++) {
        const name = parts[i];
        const isFile = i === parts.length - 1;
        const fullPath = parts.slice(0, i + 1).join("/");
        let node = nodes.find((n) => n.name === name);
        if (!node) {
          node = {
            name,
            path: fullPath,
            type: isFile ? "file" : "dir",
            children: isFile ? undefined : [],
          };
          nodes.push(node);
          nodes.sort((a, b) => {
            if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
            return a.name.localeCompare(b.name);
          });
        }
        if (!isFile) nodes = node.children!;
      }
    }
    return root;
  }

  function allDirPaths(nodes: TreeNode[]): string[] {
    const out: string[] = [];
    for (const n of nodes) {
      if (n.type === "dir") {
        out.push(n.path);
        if (n.children) out.push(...allDirPaths(n.children));
      }
    }
    return out;
  }

  let tree = $derived(buildTree(kbKeys));
  let expandedDirs = $state(new Set<string>());
  let expandedFiles = $state(new Set<string>());
  let fileContents = $state(new Map<string, string>());
  let loadingFiles = $state(new Set<string>());

  // Reset tree state whenever the selected run changes (including initial mount).
  $effect(() => {
    runId; // declare dependency — re-run when the selected run changes
    expandedDirs = new Set();
    expandedFiles = new Set();
    fileContents = new Map();
    loadingFiles = new Set();
  });

  function toggleDir(path: string) {
    const next = new Set(expandedDirs);
    if (next.has(path)) next.delete(path);
    else next.add(path);
    expandedDirs = next;
  }

  async function toggleFile(path: string) {
    const next = new Set(expandedFiles);
    if (next.has(path)) {
      next.delete(path);
      expandedFiles = next;
      return;
    }
    next.add(path);
    expandedFiles = next;
    if (!fileContents.has(path) && runId) {
      loadingFiles = new Set([...loadingFiles, path]);
      try {
        const entry = await api.getKBEntry(runId, path);
        const nc = new Map(fileContents);
        nc.set(path, entry.value);
        fileContents = nc;
      } catch (e) {
        console.error("KB: failed to load", path, e);
        const nc = new Map(fileContents);
        nc.set(path, "[error loading content]");
        fileContents = nc;
      } finally {
        const nf = new Set(loadingFiles);
        nf.delete(path);
        loadingFiles = nf;
      }
    }
  }

  function fileColor(name: string): string {
    if (name.endsWith(".md")) return "text-green";
    if (name.endsWith(".json")) return "text-amber";
    return "text-text";
  }

  // ── Vertical split drag ───────────────────────────────────────────────────

  let containerEl = $state<HTMLElement | null>(null);
  let splitPct = $state(45);

  function onDividerMousedown(e: MouseEvent) {
    e.preventDefault();
    const startY = e.clientY;
    const startPct = splitPct;

    function onMove(ev: MouseEvent) {
      if (!containerEl) return;
      const totalH = containerEl.clientHeight;
      const delta = ((ev.clientY - startY) / totalH) * 100;
      splitPct = Math.max(15, Math.min(85, startPct + delta));
    }

    function onUp() {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    }

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  // ── Mermaid pan/zoom ──────────────────────────────────────────────────────

  let graphContainerEl = $state<HTMLDivElement | null>(null);
  let panX = $state(0);
  let panY = $state(0);
  let zoom = $state(1);
  let isDragging = $state(false);
  // Natural SVG coordinate dimensions (from viewBox), set after each render.
  let svgNaturalW = 0;
  let svgNaturalH = 0;

  // Set SVG pixel size to naturalDim * zoom so the browser re-renders the
  // vector at the actual display resolution instead of scaling a raster bitmap.
  function applySvgSize() {
    if (!graphEl || !svgNaturalW || !svgNaturalH) return;
    const svgEl = graphEl.querySelector("svg");
    if (!svgEl) return;
    (svgEl as SVGElement).style.width = `${svgNaturalW * zoom}px`;
    (svgEl as SVGElement).style.height = `${svgNaturalH * zoom}px`;
    (svgEl as SVGElement).style.maxWidth = "none";
  }

  function fitGraph() {
    if (!graphContainerEl || !svgNaturalW || !svgNaturalH) return;
    const pad = 16;
    const cW = graphContainerEl.clientWidth;
    const cH = graphContainerEl.clientHeight;
    zoom = Math.min((cW - pad * 2) / svgNaturalW, (cH - pad * 2) / svgNaturalH, 1);
    panX = (cW - svgNaturalW * zoom) / 2;
    panY = (cH - svgNaturalH * zoom) / 2;
    applySvgSize();
  }

  function onGraphMousedown(e: MouseEvent) {
    e.preventDefault();
    isDragging = true;
    const startX = e.clientX - panX;
    const startY = e.clientY - panY;
    function onMove(ev: MouseEvent) {
      panX = ev.clientX - startX;
      panY = ev.clientY - startY;
    }
    function onUp() {
      isDragging = false;
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    }
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  function onGraphWheel(e: WheelEvent) {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
    const newZoom = Math.max(0.05, Math.min(10, zoom * factor));
    const rect = graphContainerEl!.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    panX = mx - (mx - panX) * (newZoom / zoom);
    panY = my - (my - panY) * (newZoom / zoom);
    zoom = newZoom;
    applySvgSize();
  }

  $effect(() => {
    if (!graphContainerEl) return;
    const el = graphContainerEl;
    el.addEventListener("wheel", onGraphWheel, { passive: false });
    return () => el.removeEventListener("wheel", onGraphWheel);
  });

  // Highlights the Mermaid cluster whose id matches the currently-active agent.
  function applyActiveNodeHighlight() {
    if (!graphEl) return;
    const svgEl = graphEl.querySelector("svg");
    if (!svgEl) return;
    svgEl.querySelectorAll(".cluster-active-highlight").forEach((el) => {
      el.classList.remove("cluster-active-highlight");
    });
    if (!activeAgent) return;
    svgEl.querySelectorAll(".cluster").forEach((clusterEl) => {
      if (clusterEl.id === activeAgent) clusterEl.classList.add("cluster-active-highlight");
    });
  }

  $effect(() => {
    // Re-run whenever activeAgent or graphEl changes.
    activeAgent;
    graphEl;
    applyActiveNodeHighlight();
  });

  // ── Mermaid rendering ─────────────────────────────────────────────────────

  let graphEl = $state<HTMLDivElement | null>(null);
  let renderError = $state<string | null>(null);

  function retheme(src: string): string {
    return src
      .replace(
        /classDef default [^\n]*/g,
        "classDef default fill:#2a2a2a,color:#d4d4d4,stroke:#303030,line-height:1.2",
      )
      .replace(
        /classDef first [^\n]*/g,
        "classDef first fill-opacity:0,color:#6b6b6b,stroke:#303030",
      )
      .replace(
        /classDef last [^\n]*/g,
        "classDef last fill:#3b2f6e,color:#d4d4d4,stroke:#a78bfa",
      );
  }

  onMount(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      darkMode: true,
      themeVariables: {
        background: "#171717",
        primaryColor: "#2a2a2a",
        primaryTextColor: "#d4d4d4",
        primaryBorderColor: "#303030",
        lineColor: "#6b6b6b",
        secondaryColor: "#222222",
        tertiaryColor: "#171717",
        edgeLabelBackground: "#171717",
        clusterBkg: "#1d1d1d",
        clusterBorder: "#303030",
        titleColor: "#d4d4d4",
        nodeTextColor: "#d4d4d4",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: "13px",
      },
    });
  });

  $effect(() => {
    if (!diagram || !graphEl) return;
    renderError = null;
    panX = 0;
    panY = 0;
    zoom = 1;
    svgNaturalW = 0;
    svgNaturalH = 0;
    mermaid
      .render("mermaid-graph", retheme(diagram))
      .then(({ svg }) => {
        if (graphEl) {
          graphEl.innerHTML = svg;
          const svgEl = graphEl.querySelector("svg");
          if (svgEl) {
            const vb = svgEl.viewBox.baseVal;
            svgNaturalW = vb.width;
            svgNaturalH = vb.height;
          }
          requestAnimationFrame(() => {
            fitGraph();
            applyActiveNodeHighlight();
          });
        }
      })
      .catch((err: unknown) => {
        renderError = err instanceof Error ? err.message : String(err);
      });
  });
</script>

<aside bind:this={containerEl} class="flex flex-col border-l border-border bg-bg h-full overflow-hidden">

  <!-- ── Graph pane ───────────────────────────────────────────────────────── -->
  <div class="flex flex-col overflow-hidden" style="height: {splitPct}%">
    <div class="px-3 py-2 text-[12px] font-semibold uppercase tracking-widest text-muted border-b border-border flex-shrink-0 flex items-center">
      <span class="flex-1">graph</span>
      {#if diagram && !renderError}
        <button
          class="text-[11px] font-semibold text-muted hover:text-text transition-colors px-1"
          title="Fit to view"
          onclick={fitGraph}
        >⊡</button>
      {/if}
    </div>
    <div
      bind:this={graphContainerEl}
      class="flex-1 overflow-hidden relative"
      style="cursor: {isDragging ? 'grabbing' : diagram && !renderError ? 'grab' : 'default'}"
      onmousedown={diagram && !renderError ? onGraphMousedown : undefined}
    >
      {#if diagram}
        {#if renderError}
          <div class="text-red text-[13px] whitespace-pre-wrap break-words p-3">{renderError}</div>
        {:else}
          <div
            bind:this={graphEl}
            class="mermaid-output"
            style="transform: translate({panX}px, {panY}px); will-change: transform;"
          ></div>
        {/if}
      {:else}
        <div class="flex items-center justify-center h-full text-faint text-[13px]">
          no graph available
        </div>
      {/if}
    </div>
  </div>

  <!-- ── Divider ──────────────────────────────────────────────────────────── -->
  <div
    class="h-1 flex-shrink-0 bg-border hover:bg-green/40 cursor-row-resize transition-colors"
    role="separator"
    aria-orientation="horizontal"
    tabindex="0"
    onmousedown={onDividerMousedown}
  ></div>

  <!-- ── Knowledge base pane ─────────────────────────────────────────────── -->
  <div class="flex flex-col overflow-hidden flex-1">
    <div class="flex items-center gap-2 px-3 py-2 border-b border-border flex-shrink-0">
      <span class="text-[12px] font-semibold uppercase tracking-widest text-muted flex-1">knowledge base</span>
      {#if kbKeys.length > 0}
        <button
          class="text-[11px] font-semibold uppercase tracking-widest text-muted hover:text-text transition-colors px-1 py-0.5"
          title="Expand all folders"
          onclick={() => (expandedDirs = new Set(allDirPaths(tree)))}
        >+</button>
        <button
          class="text-[11px] font-semibold uppercase tracking-widest text-muted hover:text-text transition-colors px-1 py-0.5"
          title="Collapse all folders"
          onclick={() => (expandedDirs = new Set())}
        >−</button>
      {/if}
    </div>
    <div class="flex-1 overflow-y-auto py-1">
      {#if kbKeys.length === 0}
        <div class="flex items-center justify-center h-full text-faint text-[13px]">
          knowledge base is empty
        </div>
      {:else}
        {#each tree as node}
          {@render treeNode(node, 0)}
        {/each}
      {/if}
    </div>
  </div>

</aside>

{#snippet treeNode(node: TreeNode, depth: number)}
  {#if node.type === "dir"}
    <div>
      <button
        class="w-full flex items-center gap-1.5 text-left hover:bg-bg-elevated transition-colors py-0.5"
        style="padding-left: {depth * 14 + 8}px; padding-right: 8px"
        onclick={() => toggleDir(node.path)}
      >
        <span class="text-muted text-[10px] w-2.5 flex-shrink-0 transition-transform duration-150"
          class:rotate-90={expandedDirs.has(node.path)}
        >▸</span>
        <span class="text-[12px] text-muted">{node.name}/</span>
      </button>
      {#if expandedDirs.has(node.path)}
        {#each node.children ?? [] as child}
          {@render treeNode(child, depth + 1)}
        {/each}
      {/if}
    </div>
  {:else}
    <div>
      <button
        class="w-full flex items-center gap-1.5 text-left hover:bg-bg-elevated transition-colors py-0.5"
        style="padding-left: {depth * 14 + 22}px; padding-right: 8px"
        onclick={() => toggleFile(node.path)}
      >
        <span class="text-[10px] w-2.5 flex-shrink-0 transition-transform duration-150 {fileColor(node.name)}"
          class:rotate-90={expandedFiles.has(node.path)}
        >▸</span>
        <span class="text-[12px] {fileColor(node.name)} truncate">{node.name}</span>
      </button>
      {#if expandedFiles.has(node.path)}
        <div
          class="pb-2 border-l border-border-subtle"
          style="margin-left: {depth * 14 + 26}px; padding-left: 8px; padding-right: 8px"
        >
          {#if loadingFiles.has(node.path)}
            <span class="text-[12px] text-faint italic">loading…</span>
          {:else}
            <span class="text-[12px] text-muted leading-snug whitespace-pre-wrap break-words"
              >{fileContents.get(node.path) ?? ""}</span>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
{/snippet}

<style>
  .mermaid-output :global(svg) {
    font-family: 'JetBrains Mono', monospace;
  }
  /* Highlight the currently-executing agent's cluster frame. */
  .mermaid-output :global(.cluster-active-highlight rect),
  .mermaid-output :global(.cluster-active-highlight path) {
    fill: rgba(251, 191, 36, 0.10) !important;
    stroke: #fbbf24 !important;
    stroke-width: 2px !important;
  }
</style>
