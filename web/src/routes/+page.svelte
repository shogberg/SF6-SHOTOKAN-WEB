<script lang="ts">
  import { api } from '$lib/api';
  import SearchBox from '$lib/components/SearchBox.svelte';
  import Loading from '$lib/components/Loading.svelte';
  const meta = api('/meta');
</script>

<h1>SHOTOKAN</h1>
<p class="muted">Strategic Hit-confirm Oracle for Tactics, Okizeme, Knockdowns And Neutral</p>
<div style="margin:18px 0 26px"><SearchBox /></div>

{#await meta}<Loading />{:then m}
  <div class="tiles">
    {#each Object.entries(m.data.counts) as [k, v]}<div class="card tile"><div class="muted small">{k}</div><div class="v">{v}</div></div>{/each}
  </div>
  <h2>Latest reviewed sets <a class="small muted" href="/sets" style="font-weight:400">all sets →</a></h2>
  <p class="muted small">Newest review first. Played: when the set was played; Reviewed: when it was added to the database.</p>
  <div class="wrap card" style="padding:0"><table>
    <thead><tr><th>Reviewed</th><th>Played</th><th>Players</th><th>Score</th><th>Review</th></tr></thead>
    <tbody>{#each m.data.recent_sets as s}
      <tr><td>{s.reviewed_at ? s.reviewed_at.slice(0, 10) : '—'}</td><td><a href={`/sets/${s.set_key}`}>{s.played_date}</a></td>
        <td><a href={`/players/${s.p1_id}`}>{s.p1_name}</a> ({s.p1_char}) vs <a href={`/players/${s.p2_id}`}>{s.p2_name}</a> ({s.p2_char})
          · <a class="small muted" href={`/h2h/${s.p1_id}/${s.p2_id}`}>head to head</a></td>
        <td><a href={`/sets/${s.set_key}`}>{s.p1_games}-{s.p2_games}</a></td><td>{s.review}</td></tr>
    {/each}</tbody></table></div>
{:catch e}<Loading error={e} />{/await}
