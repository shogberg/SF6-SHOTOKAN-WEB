<script lang="ts">
  // MR over time for one player, from reviewed ranked games (GET /players/{id}/mr). One line per character (MR is per
  // character), colours in fixed categorical order by first-played character, so a filter never repaints a line.
  import { api } from '$lib/api';

  let { pid }: { pid: number | string } = $props();

  type Pt = { replay_id: string; set_key: string; at: string; character: string; mr: number; mr_after: number; change: number;
              source: string; opponent: string | null; opp_mr: number; won: boolean };
  const PRESETS: [string, string, number | null][] = [
    ['day', 'Last day', 1], ['week', 'Last week', 7], ['month', 'Last month', 30], ['phase', 'Last phase', null],
    ['90', '90 days', 90], ['year', 'Year', 365], ['all', 'All', null]];

  let preset = $state('all');
  let from = $state('');
  let to = $state('');
  let char = $state('');
  let all: Pt[] = $state([]);
  let chars: string[] = $state([]);
  let phases: { name?: string; start: string }[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  const iso = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const lastPhase = $derived([...phases].filter((p) => p.start <= iso(new Date())).sort((a, b) => a.start.localeCompare(b.start)).at(-1));

  function pick(id: string) {
    preset = id;
    const p = PRESETS.find((x) => x[0] === id)!;
    if (id === 'all') { from = ''; to = ''; return; }
    if (id === 'phase') { from = lastPhase?.start ?? ''; to = ''; return; }
    const d = new Date(); d.setDate(d.getDate() - (p[2] as number));
    from = iso(d); to = '';
  }

  $effect(() => {
    const id = pid;
    loading = true; error = '';
    api(`/players/${id}/mr`).then((r: any) => {
      all = r.data; chars = (r.characters as string[]) ?? []; phases = (r.phases as any[]) ?? []; loading = false;
    }).catch((e) => { error = String(e?.message ?? e); loading = false; });
  });

  // light / dark categorical slots 1-3 (validated all-pairs in both modes); more characters fold onto a neutral
  const SLOT = ['var(--mr-s1)', 'var(--mr-s2)', 'var(--mr-s3)'];
  const color = (c: string) => SLOT[chars.indexOf(c)] ?? 'var(--muted)';

  const pts = $derived(all.filter((p) => (!char || p.character === char) && (!from || p.at.slice(0, 10) >= from) && (!to || p.at.slice(0, 10) <= to)));
  const series = $derived(chars.filter((c) => pts.some((p) => p.character === c)).map((c) => ({ c, pts: pts.filter((p) => p.character === c) })));

  let w = $state(640);
  const H = 260, M = { t: 12, r: 16, b: 28, l: 46 };
  const W = $derived(Math.max(240, w - 34));   // card padding
  const t = (s: string) => new Date(s.replace(' ', 'T')).getTime();
  const x0 = $derived(pts.length ? t(pts[0].at) : 0);
  const x1 = $derived(pts.length ? t(pts[pts.length - 1].at) : 1);
  const yv = $derived(pts.flatMap((p) => [p.mr, p.mr_after]));
  const ylo = $derived(yv.length ? Math.floor((Math.min(...yv) - 10) / 25) * 25 : 0);
  const yhi = $derived(yv.length ? Math.ceil((Math.max(...yv) + 10) / 25) * 25 : 1);
  const sx = (ms: number) => M.l + (x1 === x0 ? (W - M.l - M.r) / 2 : ((ms - x0) / (x1 - x0)) * (W - M.l - M.r));
  const sy = (v: number) => M.t + (1 - (v - ylo) / (yhi - ylo || 1)) * (H - M.t - M.b);
  const yticks = $derived.by(() => { const step = Math.max(25, Math.ceil((yhi - ylo) / 5 / 25) * 25); const o = []; for (let v = ylo; v <= yhi; v += step) o.push(v); return o; });
  const xticks = $derived.by(() => {
    if (!pts.length) return [];
    const n = Math.max(2, Math.min(6, Math.floor((W - M.l - M.r) / 110)));
    return Array.from({ length: n }, (_, i) => x0 + ((x1 - x0) * i) / (n - 1));
  });
  const fmtDay = (ms: number) => new Date(ms).toLocaleDateString(undefined, { month: 'short', day: 'numeric', ...(x1 - x0 > 300 * 864e5 ? { year: '2-digit' } : {}) });
  // each series: its first MR before the first game, then MR after every game
  const path = (s: { pts: Pt[] }) => {
    const p = s.pts; if (!p.length) return '';
    let d = `M${sx(t(p[0].at)).toFixed(1)},${sy(p[0].mr).toFixed(1)}`;
    for (const q of p) d += ` L${sx(t(q.at)).toFixed(1)},${sy(q.mr_after).toFixed(1)}`;
    return d;
  };

  let hx: number | null = $state(null);
  const hover = $derived.by(() => {
    if (hx == null || !pts.length) return null;
    let best = pts[0], bd = Infinity;
    for (const p of pts) { const d = Math.abs(sx(t(p.at)) - hx); if (d < bd) { bd = d; best = p; } }
    const at = t(best.at);
    // one row per series: that series' latest game at or before the hovered time
    const rows = series.map((s) => ({ c: s.c, p: [...s.pts].reverse().find((q) => t(q.at) <= at) })).filter((r) => r.p);
    return { x: sx(at), at: best.at, rows };
  });
  function move(e: PointerEvent) {
    const r = (e.currentTarget as SVGRectElement).getBoundingClientRect();
    hx = e.clientX - r.left + M.l;
  }
  const sign = (n: number) => (n > 0 ? `+${n}` : `${n}`);
  const first = $derived(pts[0]);
  const last = $derived(pts[pts.length - 1]);
</script>

<div class="filters" role="group" aria-label="MR date range">
  {#each PRESETS as [id, label]}
    <button class="preset" class:on={preset === id} disabled={id === 'phase' && !lastPhase}
            title={id === 'phase' ? (lastPhase ? `${lastPhase.name ?? 'Phase'} from ${lastPhase.start}` : 'No phase dates set (publish config "phases")') : ''}
            onclick={() => pick(id)}>{label}</button>
  {/each}
  <label class="small" for="mr-from">From</label><input id="mr-from" type="date" bind:value={from} oninput={() => (preset = 'custom')} />
  <label class="small" for="mr-to">To</label><input id="mr-to" type="date" bind:value={to} oninput={() => (preset = 'custom')} />
  {#if chars.length > 1}
    <select bind:value={char} aria-label="Character"><option value="">All characters</option>{#each chars as c}<option value={c}>{c}</option>{/each}</select>
  {/if}
</div>

<div class="card mr" class:dim={loading} bind:clientWidth={w}>
  {#if error}<p class="muted">Couldn't load MR: {error}</p>
  {:else if !pts.length}<p class="muted">{loading ? 'Loading…' : 'No reviewed ranked games with MR in this range.'}</p>
  {:else}
    <div class="head small">
      {#if series.length === 1}<span class="muted">{series[0].c} MR</span>{/if}
      <span><b>{last.mr_after}</b> <span class="muted">now</span> · <span class={last.mr_after - first.mr >= 0 ? 'ok' : 'bad'}>{sign(last.mr_after - first.mr)}</span> <span class="muted">over {pts.length} games</span></span>
    </div>
    <svg width={W} height={H} role="img" aria-label="MR over time">
      {#each yticks as v}<line x1={M.l} x2={W - M.r} y1={sy(v)} y2={sy(v)} class="grid" /><text x={M.l - 6} y={sy(v) + 4} class="tick" text-anchor="end">{v}</text>{/each}
      {#each xticks as ms}<text x={sx(ms)} y={H - 8} class="tick" text-anchor="middle">{fmtDay(ms)}</text>{/each}
      {#each series as s}<path d={path(s)} fill="none" stroke={color(s.c)} stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />{/each}
      {#if hover}
        <line x1={hover.x} x2={hover.x} y1={M.t} y2={H - M.b} class="cross" />
        {#each hover.rows as r}<circle cx={hover.x} cy={sy(r.p!.mr_after)} r="4" fill={color(r.c)} stroke="var(--panel)" stroke-width="2" />{/each}
      {/if}
      <rect x={M.l} y={M.t} width={Math.max(0, W - M.l - M.r)} height={H - M.t - M.b} fill="transparent" role="presentation"
            onpointermove={move} onpointerleave={() => (hx = null)} />
    </svg>
    {#if hover}
      <div class="tip small" style:left={`${Math.max(0, Math.min(hover.x + 12, W - 200))}px`}>
        <div class="muted">{hover.at}</div>
        {#each hover.rows as r}
          <div class="row"><span class="key" style:background={color(r.c)}></span><b>{r.p!.mr_after}</b>
            <span class={r.p!.change >= 0 ? 'ok' : 'bad'}>{sign(r.p!.change)}</span>
            <span class="muted">{series.length > 1 ? r.c + ' · ' : ''}{r.p!.won ? 'W' : 'L'} vs {r.p!.opponent ?? '?'} ({r.p!.opp_mr})</span></div>
        {/each}
      </div>
    {/if}
    {#if series.length > 1}
      <div class="legend small">{#each series as s}<span><span class="key" style:background={color(s.c)}></span>{s.c}</span>{/each}</div>
    {/if}
    <details class="small"><summary>Table</summary>
      <div class="wrap"><table><thead><tr><th>When</th><th>Character</th><th>Opponent</th><th class="n">Before</th><th class="n">Change</th><th class="n">After</th><th>Source</th></tr></thead>
        <tbody>{#each [...pts].reverse() as p}<tr><td>{p.at}</td><td>{p.character}</td><td><a href={`/sets/${p.set_key}`}>{p.won ? 'W' : 'L'} vs {p.opponent ?? '?'}</a> ({p.opp_mr})</td>
          <td class="n">{p.mr}</td><td class="n {p.change >= 0 ? 'ok' : 'bad'}">{sign(p.change)}</td><td class="n">{p.mr_after}</td><td class="muted">{p.source}</td></tr>{/each}</tbody></table></div>
    </details>
  {/if}
</div>
<p class="muted small">From reviewed ranked games only (sets in this database), so matches that weren't reviewed don't show. Each game's change comes from the next game's MR, or for a set's last game from the MR formula (Elo, K=16, as sfbuff calculates it).</p>

<style>
  .mr { position: relative; padding: 12px 16px; --mr-s1: #257de0; --mr-s2: #f47230; --mr-s3: #00b894; }
  @media (prefers-color-scheme: dark) { .mr { --mr-s1: #338ced; --mr-s2: #e76624; --mr-s3: #00a888; } }
  .dim { opacity: .55; }
  .head { display: flex; gap: 14px; margin-bottom: 4px; }
  svg { display: block; overflow: visible; }
  .grid { stroke: var(--line); stroke-width: 1; }
  .tick { fill: var(--muted); font-size: 11px; }
  .cross { stroke: var(--muted); stroke-width: 1; }
  .tip { position: absolute; top: 34px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 6px 9px; pointer-events: none; min-width: 200px; box-shadow: 0 2px 8px rgb(0 0 0 / .08); }
  .row { display: flex; gap: 6px; align-items: center; }
  .key { display: inline-block; width: 12px; height: 2px; border-radius: 1px; margin-right: 4px; vertical-align: middle; }
  .legend { display: flex; gap: 14px; margin-top: 4px; }
  .preset { font: inherit; font-size: .85rem; color: var(--fg); background: var(--panel); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px; cursor: pointer; }
  .preset.on { background: var(--chip); border-color: var(--muted); font-weight: 600; }
  .preset:disabled { opacity: .45; cursor: default; }
  details { margin-top: 8px; }
</style>
