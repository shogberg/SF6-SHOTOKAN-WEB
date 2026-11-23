<script lang="ts">
  import { ABOUT } from '$lib/about';
  const sections = [...new Set(ABOUT.map((a) => a.section))];
</script>

<h1>About SHOTOKAN</h1>
<p class="muted">How the system behind these reviews works, how it reads the game and players, and which habits it thinks matter most.</p>
{#each sections as sec}
  <h2>{sec}</h2>
  <div class="grid">
    {#each ABOUT.filter((a) => a.section === sec) as a}
      <div class="card"><h3>{a.title}</h3><p class="small">{a.body}</p></div>
    {/each}
  </div>
{/each}
