<script lang="ts">
  // Badge for a player flag (player_flags): "notable" = ★ Notable player; "azfgc" = Arizona state flag + AZFGC.
  // compact = icon only (player lists).
  let { flag, compact = false }: { flag: { flag: string; label: string; note?: string | null }; compact?: boolean } = $props();

  // Arizona flag, simplified: 13 alternating red / gold rays over the top half, blue bottom half, copper star in the middle
  const CX = 15, CY = 10, R = 30;
  const rays = Array.from({ length: 13 }, (_, i) => {
    const a0 = Math.PI - (i * Math.PI) / 13, a1 = Math.PI - ((i + 1) * Math.PI) / 13;
    return { red: i % 2 === 0, pts: `${CX},${CY} ${CX + R * Math.cos(a0)},${CY - R * Math.sin(a0)} ${CX + R * Math.cos(a1)},${CY - R * Math.sin(a1)}` };
  });
  const star = Array.from({ length: 10 }, (_, i) => {
    const r = i % 2 === 0 ? 4.6 : 1.9, a = -Math.PI / 2 + (i * Math.PI) / 5;
    return `${(CX + r * Math.cos(a)).toFixed(2)},${(CY + r * Math.sin(a)).toFixed(2)}`;
  }).join(' ');
  const title = $derived(flag.note ?? (flag.flag === 'azfgc' ? 'Arizona FGC player' : flag.flag === 'notable' ? 'Notable / pro player: their sets are worth studying for their character' : flag.label));
</script>

{#if flag.flag === 'azfgc'}
  <span class="badge az" class:compact {title}>
    <svg viewBox="0 0 30 20" width={compact ? 18 : 21} height={compact ? 12 : 14} role="img" aria-label="Arizona flag">
      <clipPath id="azclip"><rect width="30" height="20" rx="1.5" /></clipPath>
      <g clip-path="url(#azclip)">
        <rect width="30" height="10" fill="#FED700" />
        {#each rays as r}{#if r.red}<polygon points={r.pts} fill="#BF0A30" />{/if}{/each}
        <rect y="10" width="30" height="10" fill="#002868" />
        <polygon points={star} fill="#CE5C17" />
      </g>
    </svg>
    {#if !compact}<span>AZFGC</span>{/if}
  </span>
{:else}
  <span class="badge" class:compact {title}>★{#if !compact} {flag.label}{/if}</span>
{/if}

<style>
  .badge { display: inline-flex; align-items: center; gap: 6px; vertical-align: middle; margin-left: 10px; font: 600 .8rem/1 system-ui, sans-serif; letter-spacing: .02em;
           color: #fff; background: var(--accent); border-radius: 999px; padding: 5px 10px; }
  .badge.az { background: #002868; }
  .badge.compact { margin-left: 6px; padding: 0; background: none; color: var(--accent); }
  svg { display: block; border-radius: 2px; }
</style>
