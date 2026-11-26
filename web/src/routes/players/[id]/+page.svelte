<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { rank, num, pct } from '$lib/format';
  import SpectrumBar from '$lib/components/SpectrumBar.svelte';
  import Loading from '$lib/components/Loading.svelte';
  import MrChart from '$lib/components/MrChart.svelte';
  import FlagBadge from '$lib/components/FlagBadge.svelte';
  import WinRates from '$lib/components/WinRates.svelte';

  let id = $derived($page.params.id);
  let data = $derived(Promise.all([api(`/players/${id}`), api(`/players/${id}/archetypes`)]));
  const PG: [string, string][] = [['throws', 'Throws'], ['throw_techs', 'Throw techs'], ['anti_airs', 'Anti-airs'], ['counter_hits', 'Counter hits'],
    ['punish_counters', 'Punish counters'], ['raw_drive_rush', 'Raw Drive Rushes'], ['burnouts', 'Burnouts'], ['perfect_parries', 'Perfect parries']];
  const diff = (a?: number | null, b?: number | null) => (a == null || b == null ? null : Math.round((a - b) * 10) / 10);
  let char = $state('');   // '' = all characters
  $effect(() => { id; char = ''; });
  const byChar = (p: any) => (char ? (p.by_character ?? []).find((c: any) => c.character === char) : null);
</script>

{#await data}<Loading />{:then [pr, ar]}
  {@const p = pr.data}
  {@const a = ar.data}
  <div class="muted small">{p.characters.map((c: any) => c[0]).join(' / ')} · {rank(p.latest_mr, p.latest_league)} · {p.latest_band_label}{p.cfn_id ? ` · CFN ${p.cfn_id}` : ''}</div>
  <h1>{p.name}{#each p.flags ?? [] as f}<FlagBadge flag={f} />{/each}</h1>
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

  <h2>MR over time</h2>
  <MrChart pid={p.player_id} />

  <h2>Win rate</h2>
  <WinRates pid={p.player_id} />

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

  {#if (p.by_character ?? []).length > 1}
    <h2>By character</h2>
    <div class="wrap card" style="padding:0"><table>
      <thead><tr><th>Character</th><th class="n">Sets</th><th class="n">Games</th><th class="n">Throws</th><th class="n">Anti-airs</th><th class="n">Counter hits</th><th class="n">Punish counters</th><th class="n">Burnouts</th><th class="n">Attacks first on wake-up</th></tr></thead>
      <tbody>{#each p.by_character as c}
        <tr><td><button class="linklike" onclick={() => (char = c.character)}>{c.character}</button></td><td class="n">{c.sets_won}-{c.sets - c.sets_won}</td><td class="n">{c.games_won}-{c.games_lost}</td>
          <td class="n">{num(c.per_game.throws)}</td><td class="n">{num(c.per_game.anti_airs)}</td><td class="n">{num(c.per_game.counter_hits)}</td><td class="n">{num(c.per_game.punish_counters)}</td>
          <td class="n">{num(c.per_game.burnouts)}</td><td class="n">{pct(c.per_game.wake_up_attack_pct)}</td></tr>
      {/each}</tbody></table></div>
    <p class="muted small">Per game on each character. Pick one below to see its spectra and per-game numbers on their own.</p>
  {/if}

  {#if (p.by_character ?? []).length > 1}
    <div class="filters" style="margin-top:16px"><label class="small" for="char-pick">Character</label>
      <select id="char-pick" bind:value={char}><option value="">All characters</option>{#each p.by_character as c}<option value={c.character}>{c.character} ({c.games} games)</option>{/each}</select></div>
  {/if}
  {@const pc = byChar(p)}
  {@const pg = pc ? pc.per_game : p.per_game}

  <h2>Spectra{pc ? ` on ${pc.character}` : ''}</h2>
  <div class="card">{#each (pc ? pc.spectra : p.spectra) as s}<SpectrumBar {s} />{/each}</div>

  <h2>Strengths and weaknesses</h2>
  <div class="grid">
    <div class="card"><h3 class="ok">Strengths</h3><p>{p.strengths || '—'}</p></div>
    <div class="card"><h3 class="bad">Leaks</h3><p>{p.leaks || '—'}</p></div>
  </div>
  <div class="card try" style="margin-top:14px">{p.player_id && p.how_to_beat ? p.how_to_beat : '—'}</div>

  <h2>Per game{pc ? ` on ${pc.character}` : ''}</h2>
  <div class="tiles">
    {#each PG as [k, l]}<div class="card tile"><div class="muted small">{l}</div><div class="v">{num(pg[k])}</div></div>{/each}
    <div class="card tile"><div class="muted small">Attacks first after blocking</div><div class="v">{pct(pg.after_block_attack_pct)}</div></div>
    <div class="card tile"><div class="muted small">Attacks first on wake-up</div><div class="v">{pct(pg.wake_up_attack_pct)}</div></div>
  </div>
  <p class="muted small">Over {pg.games} games{pc && pc.stats_source === 'sets' ? ' (from whole-set stats: these sets were reviewed before per-game stats were kept)' : ''}. Opponents counter-hit them {num(p.opp_did.counter_hits_taken)}×, anti-aired them {num(p.opp_did.anti_aired)}× and threw them {num(p.opp_did.thrown)}× a game.</p>
{:catch e}<Loading error={e} />{/await}

<style>.timeline { display: flex; flex-wrap: wrap; } .linklike { font: inherit; background: none; border: 0; padding: 0; color: var(--accent); cursor: pointer; text-decoration: underline; }</style>
