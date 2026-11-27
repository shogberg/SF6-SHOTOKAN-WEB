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
  // strengths / leaks window: last 10 sets, last 7 days (before the snapshot was built) or all time
  const WINDOWS: [string, string][] = [['recent10', 'Last 10 sets'], ['last7', 'Last 7 days'], ['all', 'All time']];
  let win = $state('recent10');
  $effect(() => { id; win = 'recent10'; });
  const points = (s?: string | null) => (s ?? '').split(/;\s+(?![^()]*\))/).map((x) => x.trim()).filter(Boolean).map((x) => x[0].toUpperCase() + x.slice(1));
  // how to beat: JSON {tips, notes_label, notes} since 2026-11-27; plain text in older snapshots
  const beatOf = (s?: string | null) => { try { const o = JSON.parse(s ?? ''); return o && Array.isArray(o.tips) ? o : null; } catch { return null; } };
  const winOf = (p: any) => {
    const w = p.habit_windows ?? {};
    return w[win] ?? (win === 'all' || !Object.keys(w).length ? { strengths: p.strengths, leaks: p.leaks, sets: p.sets } : null);
  };
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
  <nav class="navlinks" aria-label="Sets and head-to-head">
    <a class="navlink primary" href={`/players/${p.player_id}/sets`}>All {p.sets} sets <span aria-hidden="true">→</span></a>
    {#each p.top_opponents.slice(0, 4) as o}
      <a class="navlink" href={`/h2h/${p.player_id}/${o.player_id}`} title={`Head-to-head with ${o.name}`}>vs {o.name} <span class="score">{o.wins}-{o.sets - o.wins}</span> <span aria-hidden="true">→</span></a>
    {/each}
  </nav>

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
  <div class="timeline">{#each a.timeline.slice(-10) as t}
    <a href={`/sets/${t.set_key}`} class="chip setchip" title={`${t.played_date} vs ${t.opponent}: ${t.archetype ?? 'unread'} (${t.read_confidence ?? '—'}). Open the set`}
       style:outline={t.is_deviation ? '1px dashed var(--accent)' : 'none'}><span class={t.won == null ? '' : t.won ? 'ok' : 'bad'}>{t.won == null ? '–' : t.won ? 'W' : 'L'}</span> {t.archetype ?? '?'}</a>
  {/each}</div>
  <p class="muted small">{a.timeline.length > 10 ? `The ${Math.min(10, a.timeline.length)} most recent of ${a.timeline.length} sets, oldest first. ` : 'Oldest first. '}Click one to open the set. Dashed: a deviation from their usual archetype.
    {#if a.timeline.length > 10}<a href={`/players/${p.player_id}/sets`}>All sets →</a>{/if}</p>

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
  {@const hw = winOf(p)}
  <div class="filters seg" role="group" aria-label="Window">
    {#each WINDOWS as [k, l]}<button class:active={win === k} aria-pressed={win === k} onclick={() => (win = k)}>{l}</button>{/each}
  </div>
  {#if hw}
    <p class="muted small">{hw.sets} set{hw.sets === 1 ? '' : 's'}{hw.won != null ? ` (won ${hw.won}, lost ${hw.lost})` : ''}{hw.first ? `, ${hw.first === hw.last ? hw.first : `${hw.first} to ${hw.last}`}` : ''}{hw.games ? ` · ${hw.games} games` : ''}</p>
    <div class="grid">
      <div class="card"><h3 class="ok">Strengths</h3>{#if points(hw.strengths).length}<ul class="pts">{#each points(hw.strengths) as x}<li>{x}</li>{/each}</ul>{:else}<p class="muted">—</p>{/if}</div>
      <div class="card"><h3 class="bad">Leaks</h3>{#if points(hw.leaks).length}<ul class="pts">{#each points(hw.leaks) as x}<li>{x}</li>{/each}</ul>{:else}<p class="muted">—</p>{/if}</div>
    </div>
  {:else}
    <p class="muted">No sets in this window.</p>
  {/if}
  {@const hb = beatOf(p.how_to_beat)}
  <div class="card try" style="margin-top:14px">
    {#if hb && (hb.tips.length || hb.notes.length)}
      <h3>How to beat this player</h3>
      {#if hb.tips.length}<ul class="pts">{#each hb.tips as x}<li>{x}</li>{/each}</ul>{/if}
      {#if hb.notes.length}<h4 class="muted small" style="margin:10px 0 0">{hb.notes_label} (newest reviews first)</h4><ul class="pts">{#each hb.notes as x}<li>{x}</li>{/each}</ul>{/if}
    {:else}{p.how_to_beat || '—'}{/if}
  </div>

  <h2>Per game{pc ? ` on ${pc.character}` : ''}</h2>
  <div class="tiles">
    {#each PG as [k, l]}<div class="card tile"><div class="muted small">{l}</div><div class="v">{num(pg[k])}</div></div>{/each}
    <div class="card tile"><div class="muted small">Attacks first after blocking</div><div class="v">{pct(pg.after_block_attack_pct)}</div></div>
    <div class="card tile"><div class="muted small">Attacks first on wake-up</div><div class="v">{pct(pg.wake_up_attack_pct)}</div></div>
  </div>
  <p class="muted small">Over {pg.games} games{pc && pc.stats_source === 'sets' ? ' (from whole-set stats: these sets were reviewed before per-game stats were kept)' : ''}. Opponents counter-hit them {num(p.opp_did.counter_hits_taken)}×, anti-aired them {num(p.opp_did.anti_aired)}× and threw them {num(p.opp_did.thrown)}× a game.</p>
{:catch e}<Loading error={e} />{/await}

<style>.timeline { display: flex; flex-wrap: wrap; }
  .navlinks { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 4px; }
  .navlink { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border: 1px solid var(--line); border-radius: 8px;
             background: var(--panel, transparent); color: var(--fg, inherit); text-decoration: none; font-size: .88rem; font-weight: 600;
             transition: border-color .12s, color .12s, background .12s; }
  .navlink:hover, .navlink:focus-visible { border-color: var(--accent); color: var(--accent); }
  .navlink.primary { border-color: var(--accent); color: var(--accent); }
  .navlink.primary:hover { background: var(--accent); color: var(--panel); }
  .navlink .score { font-variant-numeric: tabular-nums; color: var(--muted, #777); font-weight: 500; }
  .navlink:hover .score { color: inherit; }
  .setchip { text-decoration: none; border: 1px solid transparent; transition: border-color .12s; }
  .setchip:hover, .setchip:focus-visible { border-color: var(--accent); color: inherit; } .seg { display: flex; gap: 6px; margin: 4px 0 8px; }
  .seg button { font: inherit; font-size: .85rem; padding: 4px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--panel); color: var(--fg); cursor: pointer; }
  .seg button:hover { border-color: var(--accent); }
  .seg button.active { background: var(--accent); border-color: var(--accent); color: var(--panel); }
  .pts { margin: 6px 0 0; padding-left: 1.2em; } .pts li { margin: 3px 0; }
  .linklike { font: inherit; background: none; border: 0; padding: 0; color: var(--accent); cursor: pointer; text-decoration: underline; }</style>
