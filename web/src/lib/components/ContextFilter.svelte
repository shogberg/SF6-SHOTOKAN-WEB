<script lang="ts">
  // Set context filter for Stats by MR and Stats by Character: ranked sets, everything else (casual, custom room,
  // local, tournament: training-style sets can be lopsided), or all. The pages default to ranked.
  let { value = $bindable('ranked') }: { value?: string } = $props();
  const OPTS: [string, string][] = [['ranked', 'Ranked'], ['other', 'Other (casual, custom room, local)'], ['all', 'All']];
</script>

<div class="filters" role="group" aria-label="Set type">
  <span class="small muted">Sets</span>
  {#each OPTS as [id, label]}
    <button class="preset" class:on={value === id} onclick={() => (value = id)}>{label}</button>
  {/each}
</div>

<style>
  .preset { font: inherit; font-size: .85rem; color: var(--fg); background: var(--panel); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px; cursor: pointer; }
  .preset.on { background: var(--chip); border-color: var(--muted); font-weight: 600; }
</style>
