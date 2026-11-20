<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { num, contextLabel } from '$lib/format';
  import Loading from '$lib/components/Loading.svelte';

  let data = $derived(api(`/h2h/${$page.params.a}/${$page.params.b}`));
  const M: [string, string][] = [['after_block_attack', 'Attacks after blocking'], ['wake_up_attack', 'Attacks on wake-up'], ['throws', 'Throws'], ['throw_techs', 'Throw techs'],
    ['anti_airs', 'Anti-airs'], ['counter_hits', 'Counter hits'], ['punish_counters', 'Punish counters'], ['raw_drive_rush', 'Raw Drive Rushes'], ['burnouts', 'Burnouts'],
    ['perfect_parries', 'Perfect parries']];
  const delta = (x: number, y: number) => (y ? Math.round(((x - y) / y) * 100) : null);
</script>

{#await data}<Loading />{:then r}
  {@const d = r.data}
  <div class="muted small">Head to head</div>
  <h1><a href={`/players/${d.a.player_id}`}>{d.a.name}</a> vs <a href={`/players/${d.b.player_id}`}>{d.b.name}</a></h1>
  {#if !d.sets.length}<div class="notice">No reviewed sets between these two players yet.</div>{:else}
  <div class="tiles">
    <div class="card tile"><div class="muted small">Sets</div><div class="v">{d.record.a_sets}-{d.record.sets - d.record.a_sets}</div></div>
    <div class="card tile"><div class="muted small">Games</div><div class="v">{d.record.a_games}-{d.record.b_games}</div></div>
    <div class="card tile"><div class="muted small">Meetings</div><div class="v">{d.record.sets}</div><div class="muted small">{d.record.first} → {d.record.last}</div></div>
  </div>

  <h2>Sets</h2>
  <div class="grid">{#each d.sets as s}
    <a class="card" style="text-decoration:none" href={`/sets/${s.set_key}`}>
      <div class="muted small">{s.played_date} · {contextLabel[s.context] ?? s.context} · {s.format} · {s.review}</div>
      <h3 class={s.a_won == null ? '' : s.a_won ? 'ok' : 'bad'}>{d.a.name} {s.a_games}-{s.b_games}</h3>
      <div class="small">{s.a_char} vs {s.b_char} · {s.a_game_scores}</div>
      <div class="small muted">{d.a.name}: {s.a_archetype ?? '—'} · {d.b.name}: {s.b_archetype ?? '—'}{s.has_prediction ? ` · prediction ${s.prediction_correct ? '✓' : '✗'}` : ''}</div>
    </a>{/each}</div>

  <h2>How they play each other</h2>
  <p class="muted small">Per game against each other vs against everyone. Big differences show how this pairing changes their game.</p>
  <div class="grid">
    {#each [['a', d.a], ['b', d.b]] as [k, p]}
      {@const sd = d.sides[k]}
      <div class="card"><h3>{p.name}</h3>
        <p class="small">Archetype here: {Object.entries(sd.archetypes_here).map(([x, n]) => `${x} (${n})`).join(', ')} · usually {sd.archetype_overall ?? '—'}</p>
        <table><thead><tr><th>Per game</th><th class="n">vs {k === 'a' ? d.b.name : d.a.name}</th><th class="n">Overall</th><th class="n">Δ</th></tr></thead>
          <tbody>{#each M as [m, l]}{@const dl = delta(sd.pairing[m], sd.overall[m])}
            <tr><td>{l}</td><td class="n">{num(sd.pairing[m])}</td><td class="n">{num(sd.overall[m])}</td>
              <td class="n" style:font-weight={dl != null && Math.abs(dl) >= 50 ? 700 : 400}>{dl == null ? '—' : (dl > 0 ? '+' : '') + dl + '%'}</td></tr>{/each}</tbody></table>
        <p class="muted small">{sd.pairing.games} games vs {sd.overall.games} overall.</p>
      </div>
    {/each}
  </div>
  {/if}
{:catch e}<Loading error={e} />{/await}
