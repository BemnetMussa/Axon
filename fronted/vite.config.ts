import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	// Drop noisy logs from the production build; keep console.error/warn so
	// real failures still surface (incl. server logs on Render).
	esbuild: { pure: ['console.log', 'console.debug', 'console.info'] },
	test: {
		environment: 'jsdom',
		include: ['src/**/*.{test,spec}.{js,ts}'],
		setupFiles: ['./vitest-setup.ts']
	}
});
