<script lang="ts">
  import '../app.css';
  import Nav from '$lib/components/Nav.svelte';
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  let { children } = $props();
  let snap: any = $state(null);
  onMount(async () => { try { snap = (await api('/meta')).snapshot; } catch { /* shown by pages */ } });
</script>

<Nav />
<main>{@render children()}</main>
<footer class="muted small">
  {#if snap}Data as of {new Date(snap.built_at).toLocaleString()} · snapshot {snap.id}{snap.anonymized ? ' · anonymized' : ''}{/if}
</footer>

<style>
  footer { max-width: 1100px; margin: 0 auto; padding: 0 16px 30px; }
</style>
