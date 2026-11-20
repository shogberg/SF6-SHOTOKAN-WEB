<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import SetTable from '$lib/components/SetTable.svelte';
  import Loading from '$lib/components/Loading.svelte';
  import Pager from '$lib/components/Pager.svelte';

  let id = $derived($page.params.id);
  let f = $state({ result: '', review: '', context: '', character: '', opponent: '' });
  let pageNo = $state(1);
  $effect(() => { JSON.stringify(f); id; pageNo = 1; });   // new filters or player: back to page 1
  let profile = $derived(api(`/players/${id}`));
  let sets = $derived(api(`/players/${id}/sets`, { ...f, page: pageNo }));
</script>

{#await profile then pr}
  <div class="muted small"><a href={`/players/${id}`}>← {pr.data.name}</a></div>
  <h1>{pr.data.name}: all sets</h1>
  <div class="filters">
    <select bind:value={f.result}><option value="">Any result</option><option value="won">Won</option><option value="lost">Lost</option></select>
    <select bind:value={f.review}><option value="">Any review</option><option>Quick</option><option>Full</option><option>Tournament</option></select>
    <select bind:value={f.context}><option value="">Any context</option><option value="ranked">Ranked</option><option value="casual">Casual</option><option value="local">Local</option><option value="tournament">Tournament</option></select>
    <select bind:value={f.character}><option value="">Any character</option>{#each pr.data.characters as c}<option>{c[0]}</option>{/each}</select>
    <select bind:value={f.opponent}><option value="">Any opponent</option>{#each pr.data.top_opponents as o}<option value={o.player_id}>{o.name}</option>{/each}</select>
  </div>
{/await}
{#await sets}<Loading />{:then s}
  <p class="small">{s.totals.sets} sets · {s.totals.won}-{s.totals.lost} in sets · {s.totals.games_won}-{s.totals.games_lost} in games</p>
  <Pager page={s.page} onpage={(n) => (pageNo = n)} />
  <SetTable sets={s.data} />
  {#if s.page.pages > 1}<Pager page={s.page} onpage={(n) => (pageNo = n)} />{/if}
{:catch e}<Loading error={e} />{/await}
