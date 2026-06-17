import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		// adapter-node builds a standalone Node server (run with `node build`) for
		// hosts like Render. It reads PORT/HOST from the environment at runtime, which
		// Render provides automatically. See https://svelte.dev/docs/kit/adapter-node
		adapter: adapter()
	}
};

export default config;
