<script lang="ts">
  // Badge for a player flag (player_flags): "notable" = ★ Notable player; "azfgc" = Arizona state flag + AZFGC;
  // country codes (jp, kr, no, gb, us) = that country's flag + its name. Flags are drawn as SVG because flag emoji
  // don't render on Windows. compact = icon only (player lists).
  let { flag, compact = false }: { flag: { flag: string; label: string; note?: string | null }; compact?: boolean } = $props();

  const COUNTRIES: Record<string, { name: string; bg: string; who: string }> = {
    jp: { name: 'Japan', bg: '#BC002D', who: 'Japanese player' },
    kr: { name: 'South Korea', bg: '#0047A0', who: 'South Korean player' },
    no: { name: 'Norway', bg: '#BA0C2F', who: 'Norwegian player' },
    gb: { name: 'United Kingdom', bg: '#012169', who: 'British player' },
    us: { name: 'United States', bg: '#0A3161', who: 'American player' },
  };
  const country = $derived(COUNTRIES[flag.flag]);

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
  // South Korean flag, simplified: taeguk (red over blue) and four solid trigrams at the corners
  const trigrams = [{ x: 5.5, y: 4.3, a: -59 }, { x: 24.5, y: 4.3, a: 59 }, { x: 5.5, y: 15.7, a: 59 }, { x: 24.5, y: 15.7, a: -59 }];
  // US flag, simplified: 13 stripes, blue canton with a grid of dots for the stars
  const stripes = Array.from({ length: 13 }, (_, i) => i).filter((i) => i % 2 === 0);
  const SH = 20 / 13;
  const dots = Array.from({ length: 20 }, (_, i) => ({ x: 1.3 + (i % 5) * 2.35, y: 1.3 + Math.floor(i / 5) * 2.6 }));

  const title = $derived(flag.note && !country ? flag.note : flag.flag === 'azfgc' ? 'Arizona FGC player' : country ? country.who
    : flag.flag === 'notable' ? (flag.note ?? 'Notable / pro player: their sets are worth studying for their character') : flag.label);
</script>

{#if flag.flag === 'azfgc'}
  <span class="badge" style="background:#002868" class:compact {title}>
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
{:else if country}
  <span class="badge" style={`background:${country.bg}`} class:compact {title}>
    <svg viewBox="0 0 30 20" width={compact ? 18 : 21} height={compact ? 12 : 14} role="img" aria-label={`${country.name} flag`}>
      <clipPath id={`clip-${flag.flag}`}><rect width="30" height="20" rx="1.5" /></clipPath>
      <g clip-path={`url(#clip-${flag.flag})`}>
        {#if flag.flag === 'jp'}
          <rect width="30" height="20" fill="#fff" />
          <circle cx="15" cy="10" r="6" fill="#BC002D" />
        {:else if flag.flag === 'kr'}
          <rect width="30" height="20" fill="#fff" />
          <circle cx="15" cy="10" r="5" fill="#0047A0" />
          <path d="M10 10 A5 5 0 0 1 20 10 Z" fill="#CD2E3A" />
          <circle cx="12.5" cy="10" r="2.5" fill="#CD2E3A" />
          <circle cx="17.5" cy="10" r="2.5" fill="#0047A0" />
          {#each trigrams as t}
            <g transform={`translate(${t.x} ${t.y}) rotate(${t.a})`} fill="#000">
              <rect x="-2.4" y="-1.9" width="4.8" height=".8" /><rect x="-2.4" y="-.4" width="4.8" height=".8" /><rect x="-2.4" y="1.1" width="4.8" height=".8" />
            </g>
          {/each}
        {:else if flag.flag === 'no'}
          <rect width="30" height="20" fill="#BA0C2F" />
          <rect x="8" width="5" height="20" fill="#fff" /><rect y="7.5" width="30" height="5" fill="#fff" />
          <rect x="9.25" width="2.5" height="20" fill="#00205B" /><rect y="8.75" width="30" height="2.5" fill="#00205B" />
        {:else if flag.flag === 'gb'}
          <rect width="30" height="20" fill="#012169" />
          <path d="M0 0 L30 20 M30 0 L0 20" stroke="#fff" stroke-width="4" />
          <path d="M0 0 L30 20 M30 0 L0 20" stroke="#C8102E" stroke-width="1.4" />
          <path d="M15 0 V20 M0 10 H30" stroke="#fff" stroke-width="6" />
          <path d="M15 0 V20 M0 10 H30" stroke="#C8102E" stroke-width="3.4" />
        {:else if flag.flag === 'us'}
          <rect width="30" height="20" fill="#fff" />
          {#each stripes as i}<rect y={i * SH} width="30" height={SH} fill="#B31942" />{/each}
          <rect width="12" height={7 * SH} fill="#0A3161" />
          {#each dots as d}<circle cx={d.x} cy={d.y} r=".55" fill="#fff" />{/each}
        {/if}
      </g>
      <rect x=".25" y=".25" width="29.5" height="19.5" rx="1.5" fill="none" stroke="rgba(0,0,0,.25)" stroke-width=".5" />
    </svg>
    {#if !compact}<span>{country.name}</span>{/if}
  </span>
{:else}
  <span class="badge" class:compact {title}>★{#if !compact} {flag.label}{/if}</span>
{/if}

<style>
  .badge { display: inline-flex; align-items: center; gap: 6px; vertical-align: middle; margin-left: 10px; font: 600 .8rem/1 system-ui, sans-serif; letter-spacing: .02em;
           color: #fff; background: var(--accent); border-radius: 999px; padding: 5px 10px; }
  .badge.compact { margin-left: 6px; padding: 0; background: none !important; color: var(--accent); }
  svg { display: block; border-radius: 2px; }
</style>
