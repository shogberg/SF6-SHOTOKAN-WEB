<script lang="ts">
  // Archetypes: general notes (web/src/lib/archetypeNotes.ts) plus live tables from GET /analysis/archetypes?band=.
  import { api } from '$lib/api';
  import { num } from '$lib/format';
  import Loading from '$lib/components/Loading.svelte';
  import BandFilter from '$lib/components/BandFilter.svelte';
  import { ARCH_NOTES, ARCH_GENERAL, ARCH_NOTES_AS_OF } from '$lib/archetypeNotes';

  let band = $state('all');
  let data = $derived(api('/analysis/archetypes', { band: band === 'all' ? undefined : band }));
  const MAIN = ['Aggressive', 'Balanced', 'Defensive', 'Fundamentalist'];
  const cell = (m: any[], a: string, b: string) => m.find((x) => x.archetype === a && x.opp_archetype === b);
</script>

<h1>Archetypes</h1>
<p class="muted">Every reviewed set reads each player as one of four archetypes. What each one looks like, why players lean that way, and how each does, overall and against the others.</p>

<h2>The four archetypes</h2>
<p class="muted small">Notes as of {ARCH_NOTES_AS_OF}, from all MR bands. The tables below follow the MR filter.</p>
<div class="grid">{#each ARCH_NOTES as n}
  <div class="card"><h3>{n.archetype}</h3><p>{n.body}</p><p class="small"><b>Why players lean this way:</b> {n.why}</p></div>
{/each}</div>
<ul class="small" style="margin-top:12px">{#each ARCH_GENERAL as g}<li>{g}</li>{/each}</ul>

{#await data}<Loading />{:then r}
  {@const d = r.data}
  <h2>By MR</h2>
  <BandFilter bands={r.bands} bind:value={band} />
  <p class="muted small">{d.player_sets} player-sets with an archetype read{band === 'all' ? '' : ' in this band'}.</p>

  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Archetype</th><th class="n">Share</th><th class="n">Player-sets</th><th class="n">Players</th><th class="n">Sets won</th><th>Most common characters</th><th>Most common leans</th></tr></thead>
    <tbody>{#each d.summary as s}
      <tr><td>{s.archetype}</td><td class="n">{s.share_pct == null ? '—' : s.share_pct + '%'}</td><td class="n">{s.player_sets}</td><td class="n">{s.players}</td>
        <td class="n">{s.win_pct == null ? '—' : `${s.win_pct}% (${s.won} of ${s.decided})`}</td>
        <td class="small">{s.top_characters.map((c: any) => `${c.character} ${c.n}`).join(', ') || '—'}</td>
        <td class="small">{s.top_leans.map((l: any) => l.lean).slice(0, 2).join('; ') || '—'}</td></tr>
    {/each}</tbody></table></div>

  <h3 style="margin-top:18px">Head to head</h3>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Row vs column</th>{#each MAIN as b}<th class="n">{b}</th>{/each}</tr></thead>
    <tbody>{#each MAIN as a}
      <tr><td>{a}</td>{#each MAIN as b}{@const c = cell(d.matrix, a, b)}
        <td class="n" class:dim={!c || c.sets < 5} title={c ? `${a} won ${c.won} of ${c.sets} sets against ${b}` : 'no sets'}>{c ? `${c.win_pct}% (${c.won}/${c.sets})` : '—'}</td>{/each}</tr>
    {/each}</tbody></table></div>
  <p class="muted small">Set win rate of the row archetype against the column archetype. The MR filter applies to the row player. Dimmed: fewer than 5 sets.</p>

  <h3 style="margin-top:18px">Spectra by archetype (1-5)</h3>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Spectrum</th>{#each d.summary as s}<th class="n">{s.archetype}</th>{/each}</tr></thead>
    <tbody>{#each d.summary[0].spectra as ax, i}
      <tr><td>{ax.axis} <span class="muted small">(high = {ax.high_end})</span></td>
        {#each d.summary as s}{@const x = s.spectra[i]}<td class="n" class:dim={!x.n || x.n < 5}>{x.mean == null ? '—' : num(x.mean, 2)}</td>{/each}</tr>
    {/each}</tbody></table></div>
{:catch e}<Loading error={e} />{/await}

<style>.dim { opacity: .5; }</style>
