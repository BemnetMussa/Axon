import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { PageServerLoad } from './$types';

/**
 * Admin dashboard gate. The global layout already redirects unauthenticated users
 * to /login, so here we only decide whether the logged-in user is an admin.
 *
 * Allow-list = AXON_ADMIN_USER_IDS (comma-separated Better-Auth user IDs). The
 * SAME env must be set on the backend, which independently enforces it on
 * /admin/stats — this page-level check is just for UX (non-admins get a clear
 * "your id is X" screen instead of a wall of 403s).
 */
export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) throw redirect(302, '/login?redirectTo=/admin');

	const allow = new Set(
		(env.AXON_ADMIN_USER_IDS ?? '')
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean),
	);

	return {
		isAdmin: allow.has(locals.user.id),
		configured: allow.size > 0,
		userId: locals.user.id,
	};
};
