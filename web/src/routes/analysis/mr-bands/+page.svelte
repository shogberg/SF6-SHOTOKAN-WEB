<script lang="ts">
  // Stats by MR: how players differ by MR band (GET /analysis/mr-bands). Bands are columns; each row is one measure,
  // with the band means and n. Notes at the top are hand-written from these numbers (web/src/lib/mrBandsNotes.ts).
  import { api } from '$lib/api';
  import { num } from '$lib/format';
  import Loading from '$lib/components/Loading.svelte';
  import { NOTES, NOTES_AS_OF, NOTES_SAMPLE } from '$lib/mrBandsNotes';
  import ContextFilter from '$lib/components/ContextFilter.svelte';

  let view = $state('all');
  let context = $state('ranked');
  let data = $derived(api('/analysis/mr-bands', { view: view === 'others' ? 'others' : undefined, context }));
  const groups = ['Button economy', 'Drive economy', 'Offense, pressure and oki', 'Neutral', 'Defense'];
  const bandLabel = (d: any, id: string) => d.bands.find((b: any) => b.id === id)?.label ?? id;
</script>

<h1>Stats by MR</h1>
<p class="muted">How players differ by MR band. Each player in each reviewed set counts once, in the band of their MR at that set. A cell is the band's average (hover for the median and how many player-sets it's from).</p>

<ContextFilter bind:value={context} />
<div class="filters">
  <button class="preset" class:on={view === 'all'} onclick={() => (view = 'all')}>Everyone</button>
  <button class="preset" class:on={view === 'others'} onclick={() => (view = 'others')}>Without the site owner</button>
</div>

{#await data}<Loading />{:then r}
  {@const d = r.data}
  {@const ids = d.bands.map((b: any) => b.id)}

  <h2>What changes with MR</h2>
  <p class="muted small">Notes as of {NOTES_AS_OF}: {NOTES_SAMPLE}</p>
  <div class="grid">{#each NOTES as n}<div class="card"><div class="muted small">{n.topic}</div><h3 style="margin-top:4px">{n.title}</h3><p>{n.body}</p></div>{/each}</div>

  <h2>Biggest differences between neighbouring bands</h2>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Measure</th><th>From → to</th><th class="n">From</th><th class="n">To</th><th class="n">Size</th></tr></thead>
    <tbody>{#each d.biggest_differences as x}
      <tr><td>{x.label} <span class="muted small">({x.group})</span></td><td>{bandLabel(d, x.from)} → {bandLabel(d, x.to)}</td>
        <td class="n">{num(x.from_mean, 2)}</td><td class="n">{num(x.to_mean, 2)}</td><td class="n">{x.effect > 0 ? '+' : ''}{x.effect}</td></tr>
    {/each}</tbody></table></div>
  <p class="muted small">Size: the change in units of the measure's spread across all player-sets. Only bands with at least {d.small} player-sets are compared.</p>

  {#snippet bandTable(title: string, rows: any[], pctRows = false)}
    <h3 style="margin-top:18px">{title}</h3>
    <div class="wrap card" style="padding:0"><table>
      <thead><tr><th>Measure</th>{#each d.bands as b}<th class="n" class:dim={b.player_sets < d.small}>{b.label}</th>{/each}</tr></thead>
      <tbody>{#each rows as m}
        <tr><td>{m.label}{m.high_end ? ` (high = ${m.high_end})` : ''}</td>
          {#each ids as id}{@const c = m.bands[id]}
            <td class="n" class:dim={!c || c.n < d.small} title={c ? `mean ${c.mean}, median ${c.median}, n ${c.n}` : 'no data'}>{c ? num(c.mean, pctRows ? 0 : 2) : '—'}</td>{/each}</tr>
      {/each}</tbody></table></div>
  {/snippet}

  <h2>By band</h2>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th></th>{#each d.bands as b}<th class="n">{b.label}</th>{/each}</tr></thead>
    <tbody>
      <tr><td>Player-sets</td>{#each d.bands as b}<td class="n" class:dim={b.player_sets < d.small}>{b.player_sets}</td>{/each}</tr>
      <tr><td>Players</td>{#each d.bands as b}<td class="n" class:dim={b.player_sets < d.small}>{b.players}</td>{/each}</tr>
    </tbody></table></div>
  <p class="muted small">Dimmed: fewer than {d.small} player-sets, read as a hint. {d.unknown_left_out} player-sets with no MR or league are left out. Per-game rates are per game played in the set; % rows are shares.</p>

  {#each groups as g}{@render bandTable(g, d.metrics.filter((m: any) => m.group === g))}{/each}
  {@render bandTable('Damage taken, by how it was taken (% of damage taken; reviewed players only)', d.lenses, true)}
  {@render bandTable('Spectra (1-5)', d.spectra)}

  <h3 style="margin-top:18px">Archetype mix</h3>
  <div class="grid">{#each d.bands as b}
    <div class="card" class:dimcard={b.player_sets < d.small}><h3>{b.label} <span class="muted small">({b.player_sets})</span></h3>
      <table><thead><tr><th>Archetype</th><th class="n">Share</th><th class="n">Set win %</th></tr></thead>
        <tbody>{#each d.archetypes[b.id] ?? [] as a}<tr><td>{a.archetype}</td><td class="n">{a.pct}%</td><td class="n">{a.win_pct == null ? '—' : a.win_pct + '%'}</td></tr>{/each}</tbody></table>
    </div>{/each}</div>
{:catch e}<Loading error={e} />{/await}

<style>
  .preset { font: inherit; font-size: .85rem; color: var(--fg); background: var(--panel); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px; cursor: pointer; }
  .preset.on { background: var(--chip); border-color: var(--muted); font-weight: 600; }
  .dim { opacity: .5; } .dimcard { opacity: .6; }
</style>
