<script lang="ts">
  import { api } from '$lib/api';
  import Loading from '$lib/components/Loading.svelte';
  let topic = $state('');
  let data = $derived(api('/analysis/observations', { topic }));
</script>

<h1>Observations</h1>
<p class="muted">What makes a winning player, what makes a struggling player, and how the model's view changes over time. Revisions are kept and linked.</p>
<div class="filters"><select bind:value={topic}><option value="">All topics</option><option>Winning</option><option>Struggling</option><option>Model change</option><option>Other</option></select></div>
{#await data}<Loading />{:then r}
  {#if !r.data.length}<div class="notice">No observations published yet. They're written locally as markdown files and shipped with each snapshot (see docs/pages/observations.md).</div>{/if}
  {#each r.data as o}
    <div class="card" style="margin-bottom:12px" id={o.obs_id}>
      <div class="muted small">{o.written_at} · {o.topic}{o.supersedes ? ' · revises ' : ''}{#if o.supersedes}<a href={`#${o.supersedes}`}>{o.supersedes}</a>{/if}</div>
      <h3>{o.title}</h3>
      <p style="white-space:pre-wrap">{o.body}</p>
      {#if o.evidence.length}<div class="small">{#each o.evidence as e}<span class="chip">{e}</span>{/each}</div>{/if}
    </div>
  {/each}
{:catch e}<Loading error={e} />{/await}
