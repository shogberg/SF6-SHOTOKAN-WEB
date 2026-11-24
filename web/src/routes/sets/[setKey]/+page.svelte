<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { rank, contextLabel, num } from '$lib/format';
  import SpectrumBar from '$lib/components/SpectrumBar.svelte';
  import Loading from '$lib/components/Loading.svelte';

  let key = $derived($page.params.setKey);
  let data = $derived(api(`/sets/${key}`));
  const CATS = ['Neutral', 'Offense', 'Defense', 'Player reads / profile'];
  const ENDS: Record<string, [string, string]> = { 'Temperament (defense)': ['Impulsive', 'Mindful'], 'Temperament (offense)': ['Impulsive', 'Mindful'],
    Adaptability: ['Inelastic', 'Elastic'], 'Risk tolerance': ['Low', 'High'], Initiative: ['Reactive', 'Proactive'], Composure: ['Steady', 'Tilts'],
    Variety: ['Scripted', 'Mixed'], 'Resource use': ['Conservative', 'Spendthrift'] };

  function kpis(d: any, pid: number) {
    const h = d.hits.filter((x: any) => x.attacker_id === pid), e = d.events.filter((x: any) => x.player_id === pid);
    return { 'Anti-airs': h.filter((x: any) => x.anti_air).length, 'Counter hits': h.filter((x: any) => x.hit_kind === 'counter hit').length,
      'Punish counters': h.filter((x: any) => x.hit_kind === 'punish counter').length, Burnouts: e.filter((x: any) => x.type === 'burnout').length,
      'Perfect parries': e.filter((x: any) => x.type === 'perfect parry').length };
  }
  function drive(d: any, pid: number) {
    const r = d.resources.filter((x: any) => x.player_id === pid), s = (k: string) => Math.round(r.reduce((a: number, x: any) => a + (x[k] || 0), 0) * 10) / 10;
    return { rounds: r.length, spent: s('drive_total'), cancels: s('drive_rush_cancel'), parry: s('drive_parry'), impact: s('drive_impact'), od: s('od_specials'),
      lost_block: s('loss_block'), lost_hit: s('loss_hit'), gained: Math.round((s('gain_hit') + s('gain_block') + s('parry_regain')) * 10) / 10 };
  }
  function share(d: any, victim: number, field: string) {
    const h = d.hits.filter((x: any) => x.victim_id === victim), tot = h.reduce((a: number, x: any) => a + (x.damage || 0), 0) || 1, m: Record<string, number> = {};
    for (const x of h) m[x[field] || 'unclear'] = (m[x[field] || 'unclear'] || 0) + (x.damage || 0);
    return Object.entries(m).map(([k, v]) => [k, Math.round((100 * v) / tot)] as [string, number]).sort((a, b) => b[1] - a[1]);
  }
  let hitFilter = $state('');
</script>

{#await data}<Loading />{:then r}
  {@const d = r.data}
  {@const s = d.summary}
  {@const names = Object.fromEntries(d.players.map((p: any) => [p.player_id, p.name]))}
  <div class="muted small">{s.played_date} · {contextLabel[s.context] ?? s.context} · {s.format} · {s.review} review{s.note ? ` · ${s.note}` : ''}</div>
  <h1><a href={`/players/${s.p1_id}`}>{s.p1_name}</a> ({s.p1_char}) {s.p1_games} – {s.p2_games} <a href={`/players/${s.p2_id}`}>{s.p2_name}</a> ({s.p2_char})</h1>
  <p class="small">Winner: <b>{names[s.winner_id]}</b> · score after each game {s.progression} · {rank(s.p1_mr, s.p1_league)} vs {rank(s.p2_mr, s.p2_league)}
    · <a href={`/h2h/${s.p1_id}/${s.p2_id}`}>head to head</a></p>

  {#each d.predictions as p}
    <h2>Prediction (written before review)</h2>
    <div class="card">
      <span class="chip" class:ok={p.correct === 1} class:bad={p.correct === 0}>{p.verdict}</span>
      <p><b>Predicted:</b> {p.predicted}<br /><b>Actual:</b> {p.actual}</p>
      {#if p.body.predicted_path}<p><b>Path:</b> {p.body.predicted_path}</p>{/if}
      {#if p.body.what_happened}<p>{p.body.what_happened}</p>{/if}
      {#if p.body.lessons}<p class="try"><b>Lessons:</b> {p.body.lessons}</p>{/if}
      {#if p.written_at}<div class="muted small">Written {p.written_at}</div>{/if}
    </div>
  {/each}

  <h2>Games</h2>
  <div class="grid">
    {#each d.games as g}
      {@const sg = (d.docs.story_games || []).find((x: any) => x.game_id === g.replay_id || x.game_no === g.game_no)}
      <div class="card"><h3>Game {g.game_no} · <span class="muted">{g.replay_id}</span></h3>
        <p>{names[g.winner_player_id]} won {g.round_score} <span class="muted small">({g.round_winners})</span></p>
        {#if sg}<p class="small">{sg.summary}</p>{#if sg.turning_point}<p class="small"><b>Turning point:</b> {sg.turning_point}</p>{/if}{/if}
      </div>
    {/each}
  </div>

  <h2>Players</h2>
  <div class="grid">
    {#each d.players as p}
      {@const k = kpis(d, p.player_id)}
      {@const dr = drive(d, p.player_id)}
      <div class="card">
        <h3><a href={`/players/${p.player_id}`}>{p.name}</a> · {p.character}</h3>
        {#if p.read}<p><span class="chip">{p.read.archetype}</span> <span class="muted small">{p.read.lean} · confidence {p.read.confidence}</span></p>
          <p class="small">{p.read.evidence}</p>{#if p.read.counter_note}<p class="small try">{p.read.counter_note}</p>{/if}{/if}
        <div class="small">{#each Object.entries(k) as [l, v]}<span class="chip">{l}: {v}</span>{/each}</div>
        <p class="small muted">Drive over {dr.rounds} rounds: spent {dr.spent} (Drive Rush cancels {dr.cancels}, parry {dr.parry}, Impact {dr.impact}, OD {dr.od}),
          lost {dr.lost_block} blocking and {dr.lost_hit} getting hit, gained {dr.gained}.</p>
        <p class="small muted">Damage taken by situation: {share(d, p.player_id, 'situation').slice(0, 4).map(([a, b]) => `${a} ${b}%`).join(', ')}</p>
        <details><summary>Spectra</summary>
          {#each p.spectra as sp}<SpectrumBar s={{ ...sp, left: ENDS[sp.axis]?.[0] ?? '', right: ENDS[sp.axis]?.[1] ?? '' }} />{/each}</details>
        {#if p.baseline?.length}
          {@const bl = p.baseline.filter((x: any) => x.baseline != null)}
          <details><summary>vs their last {p.baseline[0].window_days} days ({bl.length ? `${bl[0].n_sets} earlier sets` : 'no earlier sets'})</summary>
            {#if bl.length}<table class="small"><thead><tr><th>Stat</th><th>This set</th><th>Usual</th><th>Change</th></tr></thead><tbody>
              {#each bl as x}
                {@const pct = x.label.startsWith('Pressed') || x.label.startsWith('Held') || x.label.startsWith('Share')}
                {@const f = (v: number) => (pct ? `${Math.round(v * 100)}%` : Math.abs(v) >= 100 ? Math.round(v).toString() : v.toFixed(2))}
                <tr><td>{x.label}{x.metric.startsWith('spectrum') ? ' (raw)' : ''}</td><td>{f(x.value)}</td><td>{f(x.baseline)}</td>
                  <td>{x.delta > 0 ? '+' : ''}{f(x.delta)}{x.delta_score ? ` (${x.delta_score > 0 ? '+' : ''}${x.delta_score} on the 1-5 scale)` : ''}</td></tr>
              {/each}</tbody></table>{/if}</details>
        {/if}
        <details><summary>Habits ({p.habits.length})</summary>
          {#each p.habits as h}<p class="small"><span class="chip" class:ok={h.kind === 'Strength'} class:bad={h.kind === 'Leak'}>{h.kind} · {h.area}</span>{h.habit}
            <span class="muted">Seen: {h.seen}{h.times ? ` (${h.times}×)` : ''}</span><br /><span class="try" style="display:block">{h.fix}</span></p>{/each}</details>
      </div>
    {/each}
  </div>

  {#if d.docs.story?.length}
    <h2>Story of the set</h2>
    {@const setRows = d.docs.story.filter((x: any) => x.scope === 'set' && x.confidence !== 'Low')}
    <div class="grid">
      {#each [['Top highs', 'Worked well'], ['Top lows', 'To improve']] as [t, pol]}
        <div class="card"><h3>{t}</h3>{#each setRows.filter((x: any) => x.polarity === pol).sort((a: any, b: any) => a.rank - b.rank).slice(0, 3) as x}
          <p class="small"><b>{x.headline}</b><br />{x.detail} <span class="muted">({x.evidence})</span>{#if x.try_this}<span class="try" style="display:block">Try this: {x.try_this}</span>{/if}</p>{/each}</div>
      {/each}
    </div>
    <details><summary>All findings by category ({d.docs.story.length})</summary>
      {#each CATS as c}{@const xs = d.docs.story.filter((x: any) => x.category === c)}{#if xs.length}<h3 style="margin-top:12px">{c}</h3>
        {#each xs as x}<p class="small"><span class="chip">{x.polarity}{x.change ? ` · ${x.change}` : ''}</span><b>{x.headline}</b> {x.detail} <span class="muted">({x.scope === 'set' ? 'set' : x.scope}; {x.evidence}; {x.confidence})</span></p>{/each}{/if}{/each}
    </details>
  {/if}

  {#if d.docs.set_gameplan?.length}
    <h2>Gameplans</h2>
    <div class="grid">{#each d.docs.set_gameplan as g}<div class="card"><h3>{g.player} ({g.character})</h3><p class="small">{g.plan}</p>
      <p class="small"><b>Adjustments:</b> {g.adjustments}</p>{#if g.better}<p class="small try">{g.better}</p>{/if}</div>{/each}</div>
  {/if}

  {#if d.docs.tournament?.length}
    <h2>Tournament review</h2>
    {#each [...new Set(d.docs.tournament.map((x: any) => x.part))] as part}
      <h3 style="margin-top:12px">{part}</h3>
      <div class="grid">{#each d.docs.tournament.filter((x: any) => x.part === part) as x}<div class="card"><b>{x.title}</b>{#if x.verdict} <span class="chip">{x.verdict}</span>{/if}<p class="small">{x.body}</p>{#if x.evidence}<div class="muted small">{x.evidence}</div>{/if}</div>{/each}</div>
    {/each}
  {/if}

  {#if d.docs.fixes?.length}
    <h2>Fixes and drills</h2>
    <div class="grid">{#each d.docs.fixes as f}<div class="card"><div class="muted small">#{f.rank} · {f.player}</div><h3>{f.fix}</h3><p class="small try">Drill: {f.drill}</p><p class="small">{f.why}</p></div>{/each}</div>
  {/if}

  <h2>Every hit</h2>
  <details><summary>{d.hits.length} hits</summary>
    <div class="filters"><select bind:value={hitFilter}><option value="">Both players</option>{#each d.players as p}<option value={String(p.player_id)}>{p.name}</option>{/each}</select></div>
    <div class="wrap"><table>
      <thead><tr><th>Game</th><th>Round</th><th class="n">@</th><th>Attacker</th><th class="n">Damage</th><th>Starter</th><th class="n">Hits</th><th>Kind</th><th>Situation</th><th>Victim was</th></tr></thead>
      <tbody>{#each d.hits.filter((h: any) => !hitFilter || String(h.attacker_id) === hitFilter) as h}
        <tr><td>{h.replay_id}</td><td>{h.round}</td><td class="n">{h.round_timer}</td><td>{names[h.attacker_id]}</td><td class="n">{h.damage}</td><td>{h.starter}</td>
          <td class="n">{h.hits_in_combo}</td><td>{h.hit_kind}{h.anti_air ? ' · AA' : ''}</td><td>{h.situation}</td><td>{h.lens ?? '—'}</td></tr>
      {/each}</tbody></table></div>
  </details>
{:catch e}<Loading error={e} />{/await}
