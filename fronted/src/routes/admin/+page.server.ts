import { error, redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { PageServerLoad } from './$types';

/**
 * Admin dashboard gate. The global layout already redirects unauthenticated users
 * to /login, so here we only decide whether the logged-in user is an admin.
 *
 * Allow-list = AXON_ADMIN_USER_IDS (comma-separated Better-Auth user IDs). The
 * SAME env must be set on the backend, which independently enforces it on
 * /admin/stats.
 *
 * Once the allow-list is configured, /admin is a real protected page: a non-admin
 * gets a plain 404 (the route should look like it doesn't exist — no hint that an
 * admin area is here). The only time a non-admin sees anything is during first-run
 * setup, when the allow-list is empty: then we render a setup screen so the owner
 * can read their own user ID and add it to the env.
 */
export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) throw redirect(302, '/login?redirectTo=/admin');

	const allow = new Set(
		(env.AXON_ADMIN_USER_IDS ?? '')
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean),
	);
	const isAdmin = allow.has(locals.user.id);

	// Configured + not an admin → behave as if the page doesn't exist.
	if (allow.size > 0 && !isAdmin) {
		throw error(404, 'Not Found');
	}

	return {
		isAdmin,
		configured: allow.size > 0,
		userId: locals.user.id,
	};
};
