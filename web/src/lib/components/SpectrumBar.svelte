<script lang="ts">
  // One spectrum: axis name, left end, five dots (score filled), right end, then label and evidence.
  let { s }: { s: { axis: string; left: string; right: string; score: number | null; label?: string | null; evidence?: string; lo?: number; hi?: number; n?: number } } = $props();
</script>

<div class="spec">
  <div class="axis">{s.axis}</div>
  <div class="bar" role="img" aria-label={s.score ? `${s.axis}: ${s.score} of 5, ${s.label}` : `${s.axis}: not enough data`}>
    <span>{s.left}</span>
    <span class="dots">{#each [1, 2, 3, 4, 5] as i}<i class:on={s.score === i} class:range={s.lo != null && i >= (s.lo ?? 0) && i <= (s.hi ?? 0)}></i>{/each}</span>
    <span>{s.right}</span>
  </div>
  <div class="ev muted small">{s.score ? `${s.label}${s.n && s.n > 1 ? ` (range ${s.lo}-${s.hi} over ${s.n} sets). Latest set: ` : ': '}` : 'Not enough data: '}{s.evidence}</div>
</div>

<style>
  .spec { margin-bottom: 10px; }
  .axis { font-size: .85rem; font-weight: 600; }
  .bar { display: flex; align-items: center; gap: 6px; font-size: .8rem; color: var(--muted); }
  .dots { display: inline-flex; gap: 4px; }
  i { width: 11px; height: 11px; border-radius: 50%; border: 1px solid var(--line); display: inline-block; }
  i.range { background: var(--chip); }
  i.on { background: var(--accent); border-color: transparent; }
</style>
