<script lang="ts">
  // Renamed to Archetypes (/analysis/archetypes) on 2026-11-26; this path stays for old links.
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  onMount(() => { goto('/analysis/archetypes', { replaceState: true }); });
</script>
<p class="muted">Archetype matchups moved to <a href="/analysis/archetypes">Archetypes</a>.</p>
