<script lang="ts">
  // Stats by character: game win rates of every character against every other (GET /matchups?band=). The band filter
  // keeps games where the player using the character was in that MR band at the set.
  import { api } from '$lib/api';
  import Loading from '$lib/components/Loading.svelte';
  import BandFilter from '$lib/components/BandFilter.svelte';

  let band = $state('all');
  let pick = $state('');
  let data = $derived(api('/matchups', { band: band === 'all' ? undefined : band }));
  const SMALL = 5;
</script>

<h1>Stats by Character</h1>
<p class="muted">Game win rates for each character against every other character, across every reviewed game. Each game counts from both sides. The MR filter keeps games where the player using the character was in that band at the time.</p>

{#await data}<Loading />{:then r}
  {@const d = r.data}
  <BandFilter bands={r.bands} bind:value={band} />
  {@const sel = d.find((c: any) => c.character === pick) ?? null}
  {#if !d.length}<p class="muted">No games in this band yet.</p>{:else}
  <div class="grid two">
    <div class="card" style="padding:0"><div class="wrap"><table>
      <thead><tr><th>Character</th><th class="n">Games</th><th class="n">W-L</th><th class="n">Win %</th><th style="width:30%"></th></tr></thead>
      <tbody>{#each d as c (c.character)}
        <tr class:sel={c.character === pick} class:dim={c.games_non_mirror < SMALL}>
          <td><button class="linklike" onclick={() => (pick = c.character)}>{c.character}</button></td>
          <td class="n">{c.games}</td><td class="n">{c.won}-{c.lost}</td><td class="n">{c.win_pct == null ? '—' : c.win_pct + '%'}</td>
          <td>{#if c.win_pct != null}<div class="bar"><div class="fill" style:width={`${c.win_pct}%`}></div><div class="mid"></div></div>{/if}</td></tr>
      {/each}</tbody></table></div></div>

    <div class="card">
      {#if sel}
        <h3>{sel.character} vs each character <span class="muted small">{sel.won}-{sel.lost} outside mirrors</span></h3>
        <table><thead><tr><th>Opponent</th><th class="n">Games</th><th class="n">W-L</th><th class="n">Win %</th><th style="width:30%"></th></tr></thead>
          <tbody>{#each sel.vs as v (v.opp_character)}
            <tr class:dim={v.games < SMALL}><td>{v.opp_character}</td><td class="n">{v.games}</td>
              {#if v.mirror}<td class="n muted" colspan="3">mirror</td>
              {:else}<td class="n">{v.won}-{v.lost}</td><td class="n">{v.win_pct}%</td>
                <td><div class="bar"><div class="fill" style:width={`${v.win_pct}%`}></div><div class="mid"></div></div></td>{/if}</tr>
          {/each}</tbody></table>
      {:else}<p class="muted">Pick a character to see its win rate against each opponent character.</p>{/if}
    </div>
  </div>
  <p class="muted small">Win rates leave mirror matches out. Dimmed: fewer than {SMALL} games. The line marks 50%. Most reviewed games include the site owner's Cammy, so Cammy's rows lean on one player.</p>
  {/if}
{:catch e}<Loading error={e} />{/await}

<style>
  .two { grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); align-items: start; }
  .bar { position: relative; height: 10px; background: var(--chip); border-radius: 5px; overflow: hidden; }
  .fill { position: absolute; inset: 0 auto 0 0; background: var(--accent); opacity: .75; }
  .mid { position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: var(--muted); }
  .dim td { opacity: .55; } tr.sel td { background: var(--chip); }
  .linklike { font: inherit; background: none; border: 0; padding: 0; color: var(--accent); cursor: pointer; text-decoration: underline; }
</style>
