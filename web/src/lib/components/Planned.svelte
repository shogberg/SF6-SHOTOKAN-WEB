<script lang="ts">
  let { title, phase, children }: { title: string; phase: number; children?: any } = $props();
</script>

<h1>{title}</h1>
<div class="notice">
  <b>Planned for phase {phase}.</b> This page is part of the project plan but isn't built yet.
  {#if children}<div style="margin-top:8px">{@render children()}</div>{/if}
</div>
