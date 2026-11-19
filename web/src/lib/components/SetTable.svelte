<script lang="ts">
  import { rank, contextLabel } from '$lib/format';
  let { sets, showArchetype = true }: { sets: any[]; showArchetype?: boolean } = $props();
</script>

<div class="wrap card" style="padding:0">
  <table>
    <thead><tr><th>Date</th><th>Opponent</th><th>Characters</th><th>Result</th><th>Games</th><th>MR / league</th>{#if showArchetype}<th>Archetype</th>{/if}<th>Context</th><th>Review</th><th>Prediction</th></tr></thead>
    <tbody>
      {#each sets as s}
        <tr>
          <td><a href={`/sets/${s.set_key}`}>{s.played_date}</a></td>
          <td><a href={`/players/${s.opp_id}`}>{s.opponent}</a></td>
          <td>{s.character} / {s.opp_character}</td>
          <td class={s.won ? 'ok' : 'bad'}><a href={`/sets/${s.set_key}`}>{s.won ? 'W' : 'L'} {s.games_won}-{s.games_lost}</a></td>
          <td class="muted">{s.game_scores}</td>
          <td class="small">{rank(s.mr, s.league)} / {rank(s.opp_mr, s.opp_league)}</td>
          {#if showArchetype}<td>{s.archetype ?? '—'}{#if s.read_confidence === 'Low'} <span class="muted small">(low)</span>{/if}</td>{/if}
          <td>{contextLabel[s.context] ?? s.context}</td>
          <td>{s.review}</td>
          <td>{s.has_prediction ? (s.prediction_correct === 1 ? '✓' : s.prediction_correct === 0 ? '✗' : '~') : ''}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
