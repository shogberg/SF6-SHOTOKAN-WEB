<script lang="ts">
  // MR band filter shared by Stats by Character and Archetypes: "All" plus the Stats by MR bands.
  let { bands, value = $bindable('all') }: { bands: { id: string; label: string }[]; value?: string } = $props();
</script>

<div class="filters" role="group" aria-label="MR band">
  <span class="small muted">MR</span>
  {#each bands as b}
    <button class="preset" class:on={value === b.id} onclick={() => (value = b.id)}>{b.label}</button>
  {/each}
</div>

<style>
  .preset { font: inherit; font-size: .85rem; color: var(--fg); background: var(--panel); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px; cursor: pointer; }
  .preset.on { background: var(--chip); border-color: var(--muted); font-weight: 600; }
</style>
