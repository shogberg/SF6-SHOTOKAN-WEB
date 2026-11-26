<script lang="ts">
  import FlagBadge from '$lib/components/FlagBadge.svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { rank } from '$lib/format';
  import Loading from '$lib/components/Loading.svelte';

  const data = api('/players');
  let filter = $state('');
  let pick = $state('');
  const chars = (p: any) => (p.characters ?? []).map((c: any) => c[0]).join(' / ');
  const shown = (list: any[]) => {
    const f = filter.trim().toLowerCase();
    return f ? list.filter((p) => p.name.toLowerCase().includes(f) || chars(p).toLowerCase().includes(f) || p.cfn_id === filter.trim()) : list;
  };
</script>

<h1>Players</h1>
<p class="muted">Every player with a reviewed set. Pick one to open their overview: record, archetype, spectra, habits and sets.</p>

{#await data}<Loading />{:then r}
  <div class="filters">
    <label class="small" for="player-pick">Player</label>
    <select id="player-pick" bind:value={pick} onchange={() => pick && goto(`/players/${pick}`)}>
      <option value="">Choose a player…</option>
      {#each r.data as p}<option value={String(p.player_id)}>{p.name} ({chars(p)}, {p.sets} set{p.sets === 1 ? '' : 's'})</option>{/each}
    </select>
    <input type="search" placeholder="Filter by name, character or CFN ID" bind:value={filter} aria-label="Filter players" style="min-width:240px" />
  </div>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Player</th><th>Characters</th><th>Sets</th><th>Games</th><th>Rank</th><th>Archetype</th><th>Last set</th></tr></thead>
    <tbody>{#each shown(r.data) as p}
      <tr><td><a href={`/players/${p.player_id}`}>{p.name}</a>{#each p.flags ?? [] as f}<FlagBadge flag={f} compact />{/each}</td><td>{chars(p)}</td>
        <td>{p.sets_won}-{p.sets - p.sets_won}</td><td>{p.games_won}-{p.games_lost}</td>
        <td>{rank(p.latest_mr, p.latest_league)}</td><td>{p.archetype ?? '—'}</td><td>{p.last_date ?? '—'}</td></tr>
    {/each}</tbody></table></div>
  <p class="muted small">{shown(r.data).length} of {r.data.length} players.</p>
{:catch e}<Loading error={e} />{/await}

