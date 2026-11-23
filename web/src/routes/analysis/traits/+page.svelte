<script lang="ts">
  import { api } from '$lib/api';
  import Loading from '$lib/components/Loading.svelte';

  const data = api('/analysis/traits');
  const GROUPS = ['Offense', 'Defense', 'Drive', 'Neutral', 'Damage taken', 'Spectra'];
  const fmt = (r: any, v: number) => (r.unit === 'share' ? `${Math.round(v * 100)}%` : r.unit === 'score 1-5' ? v.toFixed(1) : v.toFixed(2));
  const hi = (v: number | null) => (v == null ? '—' : `${Math.round(v * 100)}%`);
  // a row "stands out" when the winner was higher (or lower) in at least 62% of the sets that weren't ties, with 20+ such sets
  const stands = (r: any) => r.winner_higher != null && r.n - r.ties >= 20 && Math.abs(r.winner_higher - 0.5) >= 0.12;
  const lean = (r: any) => (r.winner_higher > 0.5 ? 'more' : 'less');
</script>

<h1>What winning players do</h1>
<p class="muted">The winner and the loser of the same set, compared stat by stat. Pairing inside a set keeps the opponent, matchup and day the same. Each set is weighted by its players' MR (higher-MR sets count more; weights in the analysis methods doc).</p>

{#await data}<Loading />{:then r}
  {@const d = r.data}
  {@const top = d.rows.filter(stands).sort((a: any, b: any) => Math.abs(b.winner_higher - 0.5) - Math.abs(a.winner_higher - 0.5))}
  <div class="tiles">
    <div class="card tile"><div class="muted small">Sets compared</div><div class="v">{d.pairs}</div></div>
    <div class="card tile"><div class="muted small">Clear differences</div><div class="v">{top.length}</div><div class="muted small">of {d.rows.length} stats</div></div>
  </div>

  <h2>What stands out</h2>
  {#if !top.length}<div class="notice">No stat separates winners from losers clearly yet. More sets will sharpen this.</div>{/if}
  <div class="grid">
    {#each top as t}
      <div class="card">
        <div class="muted small">{t.group}</div>
        <h3>Winners: {lean(t)} {t.label.charAt(0).toLowerCase() + t.label.slice(1)}</h3>
        <p class="small">Winner {fmt(t, t.winner)} vs loser {fmt(t, t.loser)} ({t.unit}). The winner was higher in {hi(t.winner_higher)} of {t.n - t.ties} sets{t.ties ? ` (${t.ties} ties left out)` : ''}.</p>
      </div>
    {/each}
  </div>

  {#each GROUPS as g}
    {@const rows = d.rows.filter((x: any) => x.group === g)}
    {#if rows.length}
      <h2>{g}</h2>
      <div class="wrap card" style="padding:0"><table>
        <thead><tr><th>Stat</th><th>Winner</th><th>Loser</th><th>Difference</th><th>Winner higher in</th><th>Sets</th></tr></thead>
        <tbody>{#each rows as x}
          <tr><td>{x.label} <span class="muted small">({x.unit})</span></td><td>{fmt(x, x.winner)}</td><td>{fmt(x, x.loser)}</td>
            <td>{x.diff > 0 ? '+' : ''}{fmt(x, x.diff)}</td><td>{hi(x.winner_higher)}</td><td>{x.n}{x.ties ? ` (${x.ties} ties)` : ''}</td></tr>
        {/each}</tbody></table></div>
    {/if}
  {/each}

  <h2>Archetypes</h2>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Archetype</th><th>Player-sets</th><th>Win rate</th><th>MR-weighted win rate</th></tr></thead>
    <tbody>{#each d.archetypes as a}
      <tr><td>{a.archetype}</td><td>{a.n}</td><td>{hi(a.win_rate)}</td><td>{hi(a.weighted_win_rate)}</td></tr>
    {/each}</tbody></table></div>

  <p class="muted small" style="margin-top:16px">Most reviewed sets include .shog, so these numbers lean on his matches; treat small differences as hints. Spectra are 1-5 (for Composure, higher means tilts more). Damage-taken rows are shares of each player's own damage taken, so lower is better.</p>
{:catch e}<Loading error={e} />{/await}
