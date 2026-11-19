import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  kit: {
    // single-page app: the API serves index.html for every route
    adapter: adapter({ pages: 'build', assets: 'build', fallback: 'index.html', strict: false })
  }
};
