import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

const publicPaths = new Set(['/login', '/signup']);

export const load: LayoutServerLoad = async ({ locals, url }) => {
	const path = url.pathname;
	if (path.startsWith('/api/auth')) return { user: locals.user, session: locals.session };
	const isPublic = publicPaths.has(path);

	if (!locals.user && !isPublic) {
		const dest = path === '/' ? '' : `${path}${url.search}`;
		throw redirect(302, `/login?redirectTo=${encodeURIComponent(dest || '/')}`);
	}

	if (locals.user && isPublic) {
		throw redirect(302, '/');
	}

	return {
		user: locals.user,
		session: locals.session,
	};
};
