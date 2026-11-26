<script lang="ts">
  // Game win rates per character the player used (GET /players/{id}/winrates): against the opponent's MR in
  // 100-point bands (only bands with games) and against each opponent character. One block per character played,
  // so a two-character player like Phenom gets each character's own tables.
  import { api } from '$lib/api';

  let { pid }: { pid: number | string } = $props();

  type Row = { games: number; won: number; lost: number; win_pct: number | null };
  type Band = Row & { band: string; mr_from: number };
  type Opp = Row & { opp_character: string };
  type Char = Row & { character: string; by_mr: Band[]; mr_games: number; by_opponent_character: Opp[] };

  let ranked = $state(false);
  let chars: Char[] = $state([]);
  let pick = $state('');
  let loading = $state(true);
  let error = $state('');
  const SMALL = 5;   // fewer games than this: shown dimmed, too few to read much into

  $effect(() => {
    const id = pid, ctx = ranked ? 'ranked' : undefined;
    loading = true; error = '';
    api(`/players/${id}/winrates`, { context: ctx }).then((r: any) => {
      chars = r.data; loading = false;
      if (!chars.some((c) => c.character === pick)) pick = '';
    }).catch((e: any) => { error = String(e?.message ?? e); loading = false; });
  });

  const shown = $derived(pick ? chars.filter((c) => c.character === pick) : chars);
</script>

<div class="filters">
  <button class="preset" class:on={!ranked} onclick={() => (ranked = false)}>All reviewed games</button>
  <button class="preset" class:on={ranked} onclick={() => (ranked = true)}>Ranked only</button>
  {#if chars.length > 1}
    <label class="small" for="wr-char" style="margin-left:8px">Character</label>
    <select id="wr-char" bind:value={pick}><option value="">All characters</option>{#each chars as c}<option value={c.character}>{c.character} ({c.games} games)</option>{/each}</select>
  {/if}
</div>

{#if loading}<p class="muted small">Loading…</p>
{:else if error}<p class="bad small">{error}</p>
{:else if !chars.length}<p class="muted">No decided games yet.</p>
{:else}
  {#each shown as c (c.character)}
    {#if chars.length > 1}<h3 style="margin-top:14px">{c.character} <span class="muted small">{c.won}-{c.lost} in games ({c.win_pct}%)</span></h3>{/if}
    <div class="grid">
      <div class="card">
        <h3>vs opponent MR</h3>
        {#if c.by_mr.length}
          <table><thead><tr><th>Opponent MR</th><th class="n">Games</th><th class="n">W-L</th><th class="n">Win %</th><th style="width:34%"></th></tr></thead>
            <tbody>{#each c.by_mr as b (b.band)}
              <tr class:dim={b.games < SMALL} title={`${b.won} won, ${b.lost} lost vs opponents at ${b.band} MR`}>
                <td>{b.band}</td><td class="n">{b.games}</td><td class="n">{b.won}-{b.lost}</td><td class="n">{b.win_pct}%</td>
                <td><div class="bar"><div class="fill" style:width={`${b.win_pct}%`}></div><div class="mid"></div></div></td></tr>
            {/each}</tbody></table>
          <p class="muted small">{c.mr_games} of {c.games} games had an opponent MR (Master rank, ranked).</p>
        {:else}<p class="muted small">No games against an opponent with an MR.</p>{/if}
      </div>
      <div class="card">
        <h3>vs character</h3>
        <table><thead><tr><th>Opponent</th><th class="n">Games</th><th class="n">W-L</th><th class="n">Win %</th><th style="width:34%"></th></tr></thead>
          <tbody>{#each c.by_opponent_character as o (o.opp_character)}
            <tr class:dim={o.games < SMALL} title={`${o.won} won, ${o.lost} lost vs ${o.opp_character}`}>
              <td>{o.opp_character}</td><td class="n">{o.games}</td><td class="n">{o.won}-{o.lost}</td><td class="n">{o.win_pct}%</td>
              <td><div class="bar"><div class="fill" style:width={`${o.win_pct}%`}></div><div class="mid"></div></div></td></tr>
          {/each}</tbody></table>
      </div>
    </div>
  {/each}
  <p class="muted small">Win rate in games (a character switch inside a set counts each game under the character used). Dimmed: fewer than {SMALL} games. The line marks 50%.</p>
{/if}

<style>
  .preset { font: inherit; font-size: .85rem; color: var(--fg); background: var(--panel); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px; cursor: pointer; }
  .preset.on { background: var(--chip); border-color: var(--muted); font-weight: 600; }
  .bar { position: relative; height: 10px; background: var(--chip); border-radius: 5px; overflow: hidden; }
  .fill { position: absolute; inset: 0 auto 0 0; background: var(--accent); opacity: .75; }
  .mid { position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: var(--muted); }
  tr.dim td { opacity: .55; }
</style>
