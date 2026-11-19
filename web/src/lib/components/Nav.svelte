<script lang="ts">
  import SearchBox from './SearchBox.svelte';
</script>

<header>
  <a class="brand" href="/">SHOTOKAN</a>
  <nav>
    <a href="/analysis/mr-bands">MR bands</a>
    <a href="/analysis/traits">Winning traits</a>
    <a href="/analysis/observations">Observations</a>
    <a href="/analysis/archetype-predictions">Archetype matchups</a>
    <a href="/matchups">Characters</a>
  </nav>
  <SearchBox compact />
</header>

<style>
  header { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; padding: 10px 16px; border-bottom: 1px solid var(--line); background: var(--panel); }
  .brand { font-family: Georgia, serif; font-size: 1.2rem; letter-spacing: .08em; text-decoration: none; }
  nav { display: flex; flex-wrap: wrap; gap: 12px; font-size: .9rem; flex: 1; }
  nav a { text-decoration: none; color: var(--muted); }
</style>
