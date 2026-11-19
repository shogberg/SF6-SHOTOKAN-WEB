<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { rank, contextLabel, parseJSON } from '$lib/format';
  import SetTable from '$lib/components/SetTable.svelte';
  import Pager from '$lib/components/Pager.svelte';
  import Loading from '$lib/components/Loading.svelte';

  // state lives in the URL (?q=&player=&page=&result=&review=&context=) so a list can be bookmarked or shared
  let sp = $derived($page.url.searchParams);
  let params = $derived({ q: sp.get('q') ?? '', player: sp.get('player') ?? '', page: sp.get('page') ?? '1',
    result: sp.get('result') ?? '', review: sp.get('review') ?? '', context: sp.get('context') ?? '' });
  let data = $derived(api('/sets', params));
  let q = $state('');
  $effect(() => { q = params.q; });

  function update(changes: Record<string, string>, resetPage = true) {
    const u = new URLSearchParams($page.url.searchParams);
    for (const [k, v] of Object.entries(changes)) v ? u.set(k, v) : u.delete(k);
    if (resetPage && !('page' in changes)) u.delete('page');
    goto(`/sets${u.size ? `?${u}` : ''}`, { keepFocus: true, noScroll: !('page' in changes) });
  }
  const search = () => update({ q: q.trim(), player: '' });
  const pick = (id: number) => update({ player: String(id), q: '' });
</script>

<h1>Sets</h1>
<form class="filters" onsubmit={(e) => { e.preventDefault(); search(); }}>
  <input type="search" placeholder="Player name or CFN ID" bind:value={q} aria-label="Player name or CFN ID" style="min-width:260px" />
  <button class="btn" type="submit">Search</button>
  {#if params.player || params.q}<button class="btn ghost" type="button" onclick={() => update({ q: '', player: '' })}>All sets</button>{/if}
</form>

{#await data}<Loading />{:then r}
  {#if r.candidates?.length && !r.player}
    <p class="muted">{r.candidates.length} players match “{params.q}”. Choose one:</p>
    <ul class="pick" role="listbox" aria-label="Matching players">
      {#each r.candidates as c}
        <li><button role="option" aria-selected="false" onclick={() => pick(c.player_id)}>
          <b>{c.name}</b> <span class="muted small">{parseJSON(c.characters, [])[0]?.[0] ?? ''} · {c.latest_band_label} · {c.sets} set{c.sets === 1 ? '' : 's'}{c.cfn_id ? ` · CFN ${c.cfn_id}` : ''}{c.other_names ? ` · also ${c.other_names}` : ''}</span>
        </button></li>
      {/each}
    </ul>
  {:else if params.q && !r.player && !r.data.length}
    <div class="notice">No player matches “{params.q}”.</div>
  {:else}
    {#if r.player}
      <p><a href={`/players/${r.player.player_id}`}><b>{r.player.name}</b></a>
        <span class="muted small">{r.player.characters.map((c: any) => c[0]).join(' / ')}{r.player.cfn_id ? ` · CFN ${r.player.cfn_id}` : ''}</span>
        · {r.totals.won}-{r.totals.sets - r.totals.won} in sets · {r.totals.games_won}-{r.totals.games_lost} in games</p>
    {/if}
    <div class="filters">
      {#if r.player}<select value={params.result} onchange={(e) => update({ result: e.currentTarget.value })}><option value="">Any result</option><option value="won">Won</option><option value="lost">Lost</option></select>{/if}
      <select value={params.review} onchange={(e) => update({ review: e.currentTarget.value })}><option value="">Any review</option><option>Quick</option><option>Full</option><option>Tournament</option></select>
      <select value={params.context} onchange={(e) => update({ context: e.currentTarget.value })}><option value="">Any context</option><option value="ranked">Ranked</option><option value="casual">Casual</option><option value="local">Local</option><option value="tournament">Tournament</option></select>
    </div>
    <Pager page={r.page} onpage={(n) => update({ page: String(n) }, false)} />
    {#if r.player}
      <SetTable sets={r.data} />
    {:else}
      <div class="wrap card" style="padding:0"><table>
        <thead><tr><th>Date</th><th>Players</th><th>Score</th><th>Games</th><th>MR / league</th><th>Context</th><th>Review</th><th>Prediction</th></tr></thead>
        <tbody>{#each r.data as s}
          <tr><td><a href={`/sets/${s.set_key}`}>{s.played_date}</a></td>
            <td><a href={`/players/${s.p1_id}`} class:ok={s.winner_id === s.p1_id}>{s.p1_name}</a> ({s.p1_char}) vs <a href={`/players/${s.p2_id}`} class:ok={s.winner_id === s.p2_id}>{s.p2_name}</a> ({s.p2_char})</td>
            <td><a href={`/sets/${s.set_key}`}>{s.p1_games}-{s.p2_games}</a></td><td class="muted">{s.game_scores}</td>
            <td class="small">{rank(s.p1_mr, s.p1_league)} / {rank(s.p2_mr, s.p2_league)}</td>
            <td>{contextLabel[s.context] ?? s.context}</td><td>{s.review}</td>
            <td>{s.has_prediction ? (s.prediction_correct === 1 ? '✓' : s.prediction_correct === 0 ? '✗' : '~') : ''}</td></tr>
        {/each}</tbody></table></div>
    {/if}
    {#if r.page.pages > 1}<Pager page={r.page} onpage={(n) => update({ page: String(n) }, false)} />{/if}
  {/if}
{:catch e}<Loading error={e} />{/await}

<style>
  .pick { list-style: none; padding: 0; margin: 0 0 12px; display: grid; gap: 6px; }
  .pick button { all: unset; display: block; width: 100%; box-sizing: border-box; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); cursor: pointer; }
  .pick button:hover, .pick button:focus-visible { border-color: var(--accent); }
  .btn { font: inherit; padding: 6px 12px; border-radius: 8px; border: 1px solid var(--accent); background: var(--accent); color: #fff; cursor: pointer; }
  .btn.ghost { background: transparent; color: var(--fg); border-color: var(--line); }
</style>
