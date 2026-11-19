<script lang="ts">
  let { error }: { error?: any } = $props();
</script>
{#if error}<div class="notice bad">{error.status === 404 ? 'Not found.' : error.status === 503 ? `No data yet: ${error.detail}` : error.message}</div>
{:else}<p class="muted">Loading…</p>{/if}
