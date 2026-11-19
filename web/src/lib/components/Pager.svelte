<script lang="ts">
  // Page controls. `page` is the API's {page, per_page, total, pages}; onpage(n) is called to change page.
  let { page, onpage }: { page: { page: number; per_page: number; total: number; pages: number }; onpage: (n: number) => void } = $props();
  let first = $derived(page.total ? (page.page - 1) * page.per_page + 1 : 0);
  let last = $derived(Math.min(page.page * page.per_page, page.total));
  // compact list of page numbers: 1 … p-1 p p+1 … last
  let nums = $derived.by(() => {
    const out: (number | '…')[] = []; const n = page.pages, p = page.page;
    for (let i = 1; i <= n; i++) {
      if (i === 1 || i === n || Math.abs(i - p) <= 1) out.push(i);
      else if (out[out.length - 1] !== '…') out.push('…');
    }
    return out;
  });
</script>

<nav class="pager" aria-label="Pages">
  <span class="muted small">{first}-{last} of {page.total}</span>
  {#if page.pages > 1}
    <button disabled={page.page <= 1} onclick={() => onpage(page.page - 1)} aria-label="Previous page">‹ Prev</button>
    {#each nums as n}
      {#if n === '…'}<span class="muted">…</span>
      {:else}<button class:on={n === page.page} aria-current={n === page.page ? 'page' : undefined} onclick={() => onpage(n as number)}>{n}</button>{/if}
    {/each}
    <button disabled={page.page >= page.pages} onclick={() => onpage(page.page + 1)} aria-label="Next page">Next ›</button>
  {/if}
</nav>

<style>
  .pager { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin: 10px 0; }
  button { font: inherit; font-size: .85rem; min-width: 2.2em; padding: 4px 8px; border-radius: 6px; border: 1px solid var(--line); background: var(--panel); color: var(--fg); cursor: pointer; }
  button.on { background: var(--accent); border-color: var(--accent); color: #fff; }
  button:disabled { opacity: .4; cursor: default; }
  span.muted.small { margin-right: 6px; }
</style>
