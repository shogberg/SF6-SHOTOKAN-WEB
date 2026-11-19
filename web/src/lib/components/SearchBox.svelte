<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { parseJSON } from '$lib/format';
  let { compact = false } = $props();
  let q = $state('');
  let results: any[] = $state([]);
  let timer: ReturnType<typeof setTimeout>;

  function onInput() {
    clearTimeout(timer);
    const v = q.trim();
    if (!v) { results = []; return; }
    timer = setTimeout(async () => {
      // "a vs b" opens head to head
      const m = v.match(/^(.+?)\s+vs\.?\s+(.+)$/i);
      if (m) {
        const [a, b] = await Promise.all([api('/search', { q: m[1], limit: 1 }), api('/search', { q: m[2], limit: 1 })]);
        results = a.data[0] && b.data[0] ? [{ h2h: true, a: a.data[0], b: b.data[0] }] : [];
        return;
      }
      results = (await api('/search', { q: v, limit: 8 })).data;
    }, 150);
  }
  function go(r: any) {
    q = ''; results = [];
    goto(r.h2h ? `/h2h/${r.a.player_id}/${r.b.player_id}` : `/players/${r.player_id}`);
  }
</script>

<div class="search" class:compact>
  <input type="search" placeholder="Search player, CFN ID, or “a vs b”" bind:value={q} oninput={onInput}
         onkeydown={(e) => e.key === 'Enter' && results[0] && go(results[0])} aria-label="Search players" />
  {#if results.length}
    <ul>
      {#each results as r}
        <li><button onclick={() => go(r)}>
          {#if r.h2h}<b>{r.a.name}</b> vs <b>{r.b.name}</b> <span class="muted">head to head</span>
          {:else}<b>{r.name}</b> <span class="muted">{parseJSON(r.characters, [])[0]?.[0] ?? ''} · {r.latest_band_label} · {r.sets} sets{r.other_names ? ` · also ${r.other_names}` : ''}</span>{/if}
        </button></li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .search { position: relative; width: min(100%, 520px); }
  .search.compact { width: min(100%, 300px); }
  input { width: 100%; }
  ul { position: absolute; z-index: 10; left: 0; right: 0; list-style: none; margin: 4px 0 0; padding: 4px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
  button { all: unset; display: block; width: 100%; padding: 6px 8px; border-radius: 6px; cursor: pointer; font-size: .9rem; }
  button:hover, button:focus-visible { background: var(--chip); }
</style>
