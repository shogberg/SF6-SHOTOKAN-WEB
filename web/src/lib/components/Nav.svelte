<script lang="ts">
  import { page } from '$app/state';
  import SearchBox from './SearchBox.svelte';

  const links = [
    { href: '/sets', label: 'Sets' },
    { href: '/players', label: 'Players' },
    { href: '/analysis/mr-bands', label: 'MR bands' },
    { href: '/analysis/traits', label: 'What winning players do' },
    { href: '/analysis/observations', label: 'Observations' },
    { href: '/analysis/archetype-predictions', label: 'Archetype matchups' },
    { href: '/matchups', label: 'Characters' },
    { href: '/about', label: 'About' }
  ];
  const active = (href: string) => page.url.pathname === href || page.url.pathname.startsWith(href + '/');
</script>

<header>
  <a class="brand" href="/">SHOTOKAN</a>
  <nav aria-label="Main">
    {#each links as l}
      <a href={l.href} class:active={active(l.href)} aria-current={active(l.href) ? 'page' : undefined}>{l.label}</a>
    {/each}
  </nav>
  <SearchBox compact />
</header>

<style>
  header { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; padding: 10px 16px; border-bottom: 1px solid var(--line); background: var(--panel); position: sticky; top: 0; z-index: 10; }
  .brand { font-family: Georgia, serif; font-size: 1.2rem; letter-spacing: .08em; text-decoration: none; }
  nav { display: flex; flex-wrap: wrap; gap: 6px; font-size: .9rem; flex: 1; }
  nav a { text-decoration: none; color: var(--fg); font-weight: 500; padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--chip); transition: background .12s, border-color .12s; }
  nav a:hover { border-color: var(--accent); color: var(--accent); background: var(--panel); }
  nav a.active { background: var(--accent); border-color: var(--accent); color: #fff; }
  nav a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
</style>
