<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { rank, num, pct } from '$lib/format';
  import SpectrumBar from '$lib/components/SpectrumBar.svelte';
  import Loading from '$lib/components/Loading.svelte';

  let id = $derived($page.params.id);
  let data = $derived(Promise.all([api(`/players/${id}`), api(`/players/${id}/archetypes`)]));
  const PG: [string, string][] = [['throws', 'Throws'], ['throw_techs', 'Throw techs'], ['anti_airs', 'Anti-airs'], ['counter_hits', 'Counter hits'],
    ['punish_counters', 'Punish counters'], ['raw_drive_rush', 'Raw Drive Rushes'], ['burnouts', 'Burnouts'], ['perfect_parries', 'Perfect parries']];
  const diff = (a?: number | null, b?: number | null) => (a == null || b == null ? null : Math.round((a - b) * 10) / 10);
</script>

{#await data}<Loading />{:then [pr, ar]}
  {@const p = pr.data}
  {@const a = ar.data}
  <div class="muted small">{p.characters.map((c: any) => c[0]).join(' / ')} · {rank(p.latest_mr, p.latest_league)} · {p.latest_band_label}{p.cfn_id ? ` · CFN ${p.cfn_id}` : ''}</div>
  <h1>{p.name}</h1>
  {#if p.other_names.length}<div class="muted small">Also played as {p.other_names.join(', ')}</div>{/if}
  <div class="tiles" style="margin-top:14px">
    <div class="card tile"><div class="muted small">Sets</div><div class="v">{p.sets_won}-{p.sets - p.sets_won}</div></div>
    <div class="card tile"><div class="muted small">Games</div><div class="v">{p.games_won}-{p.games_lost}</div></div>
    <div class="card tile"><div class="muted small">Archetype</div><div class="v" style="font-size:1.25rem">{p.archetype ?? '—'}</div><div class="muted small">{p.archetype_n} of {p.sets} sets · {p.confidence}</div></div>
    <div class="card tile"><div class="muted small">Deviates from it</div><div class="v">{p.deviation_rate == null ? '—' : Math.round(p.deviation_rate * 100) + '%'}</div><div class="muted small">{p.deviation_n} sets</div></div>
  </div>
  <p style="margin-top:16px">{p.summary}</p>
  <p class="small"><a href={`/players/${p.player_id}/sets`}>All {p.sets} sets →</a>
    {#each p.top_opponents.slice(0, 4) as o} · <a href={`/h2h/${p.player_id}/${o.player_id}`}>vs {o.name} ({o.wins}-{o.sets - o.wins})</a>{/each}</p>

  <h2>Archetype</h2>
  <div class="grid">
    <div class="card">
      <h3>By result</h3>
      <table><thead><tr><th>Archetype</th><th class="n">Sets</th><th class="n">Won</th><th class="n">Lost</th></tr></thead>
        <tbody>{#each a.summary as r}<tr><td>{r.archetype}{r.archetype === p.archetype ? ' (usual)' : ''}</td><td class="n">{r.sets}</td><td class="n ok">{r.wins}</td><td class="n bad">{r.losses}</td></tr>{/each}</tbody></table>
    </div>
    <div class="card">
      <h3>When they deviate</h3>
      {#if a.deviations.length}
        <table><thead><tr><th>From → to</th><th>Context</th><th class="n">Sets</th></tr></thead>
          <tbody>{#each a.deviations.slice(0, 10) as d}<tr><td>{d.from_archetype} → {d.to_archetype}</td><td>{d.context}</td><td class="n">{d.n}</td></tr>{/each}</tbody></table>
      {:else}<p class="muted">Always read as {p.archetype ?? 'unread'} so far.</p>{/if}
    </div>
  </div>
  <h3 style="margin-top:16px">Spectra in won vs lost sets</h3>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Axis</th><th class="n">Won (n)</th><th class="n">Lost (n)</th><th class="n">Difference</th><th class="n">Spread</th></tr></thead>
    <tbody>{#each a.spectra_by_result as s}
      {@const d = diff(s.mean_win, s.mean_loss)}
      <tr><td>{s.axis}</td><td class="n">{num(s.mean_win)} ({s.n_win})</td><td class="n">{num(s.mean_loss)} ({s.n_loss})</td>
        <td class="n" style:font-weight={d != null && Math.abs(d) > s.sd_all ? 700 : 400}>{d == null ? '—' : (d > 0 ? '+' : '') + d}</td><td class="n muted">±{num(s.sd_all)}</td></tr>
    {/each}</tbody></table></div>
  <p class="muted small">Bold: the won-vs-lost difference is bigger than their normal set-to-set spread.</p>

  <h3 style="margin-top:16px">Archetype by set</h3>
  <div class="timeline">{#each a.timeline as t}
    <a href={`/sets/${t.set_key}`} class="chip" title={`${t.played_date} vs ${t.opponent}: ${t.archetype ?? 'unread'} (${t.read_confidence ?? '—'})`}
       style:outline={t.is_deviation ? '1px dashed var(--accent)' : 'none'}><span class={t.won == null ? '' : t.won ? 'ok' : 'bad'}>{t.won == null ? '–' : t.won ? 'W' : 'L'}</span> {t.archetype ?? '?'}</a>
  {/each}</div>
  <p class="muted small">Dashed: a deviation from their usual archetype.</p>

  <h2>Spectra</h2>
  <div class="card">{#each p.spectra as s}<SpectrumBar {s} />{/each}</div>

  <h2>Strengths and weaknesses</h2>
  <div class="grid">
    <div class="card"><h3 class="ok">Strengths</h3><p>{p.strengths || '—'}</p></div>
    <div class="card"><h3 class="bad">Leaks</h3><p>{p.leaks || '—'}</p></div>
  </div>
  <div class="card try" style="margin-top:14px">{p.player_id && p.how_to_beat ? p.how_to_beat : '—'}</div>

  <h2>Per game</h2>
  <div class="tiles">
    {#each PG as [k, l]}<div class="card tile"><div class="muted small">{l}</div><div class="v">{num(p.per_game[k])}</div></div>{/each}
    <div class="card tile"><div class="muted small">Attacks first after blocking</div><div class="v">{pct(p.per_game.after_block_attack_pct)}</div></div>
    <div class="card tile"><div class="muted small">Attacks first on wake-up</div><div class="v">{pct(p.per_game.wake_up_attack_pct)}</div></div>
  </div>
  <p class="muted small">Over {p.per_game.games} games. Opponents counter-hit them {num(p.opp_did.counter_hits_taken)}×, anti-aired them {num(p.opp_did.anti_aired)}× and threw them {num(p.opp_did.thrown)}× a game.</p>
{:catch e}<Loading error={e} />{/await}

<style>.timeline { display: flex; flex-wrap: wrap; }</style>
