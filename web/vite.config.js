import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  // `npm run dev` proxies the API (run uvicorn on 8100)
  server: { proxy: { '/api': 'http://127.0.0.1:8100' } }
});
