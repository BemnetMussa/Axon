import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	// Drop noisy logs from the production build; keep console.error/warn so
	// real failures still surface (incl. server logs on Render).
	esbuild: { pure: ['console.log', 'console.debug', 'console.info'] }
});
