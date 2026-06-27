import { error, fail, redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { desc, eq, sql } from 'drizzle-orm';
import { db } from '$lib/server/db';
import { user as userTable, session as sessionTable } from '$lib/server/auth-schema';
import type { PageServerLoad, Actions } from './$types';

/**
 * Admin dashboard gate + user/visitor data.
 *
 * Allow-list = AXON_ADMIN_USER_IDS (comma-separated Better-Auth user IDs); the
 * SAME env must be set on the backend, which independently enforces it on
 * /admin/stats. Configured + non-admin → plain 404 (route looks nonexistent).
 * Not configured → first-run setup screen so the owner can read their user ID.
 *
 * User management (revoke sessions / delete) hits the real Better-Auth tables.
 * Deleting a user cascades to their sessions + accounts (FK onDelete: cascade).
 * Their Axon saves/feedback live in separate tables and are left orphaned.
 */
function adminAllowList(): Set<string> {
	return new Set(
		(env.AXON_ADMIN_USER_IDS ?? '')
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean),
	);
}

const toISO = (v: unknown): string | null =>
	v == null ? null : v instanceof Date ? v.toISOString() : String(v);

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) throw redirect(302, '/login?redirectTo=/admin');
	const myId = locals.user.id;

	const allow = adminAllowList();
	const isAdmin = allow.has(myId);

	if (allow.size > 0 && !isAdmin) {
		throw error(404, 'Not Found');
	}

	const base = { isAdmin, configured: allow.size > 0, userId: myId };
	if (!isAdmin) {
		return { ...base, users: [], sessions: [], totalUsers: 0 };
	}

	// --- Users + visit/session activity (admin only) ---
	const users = await db
		.select({
			id: userTable.id,
			name: userTable.name,
			email: userTable.email,
			emailVerified: userTable.emailVerified,
			image: userTable.image,
			createdAt: userTable.createdAt,
		})
		.from(userTable)
		.orderBy(desc(userTable.createdAt))
		.limit(200);

	// Per-user: most recent activity + session count, in one grouped query.
	const agg = await db
		.select({
			userId: sessionTable.userId,
			last: sql<string>`max(${sessionTable.updatedAt})`,
			sessions: sql<number>`count(*)::int`,
		})
		.from(sessionTable)
		.groupBy(sessionTable.userId);
	const seen = new Map(agg.map((r) => [r.userId, { last: toISO(r.last), sessions: Number(r.sessions) }]));

	// Most recent sessions = "who visited", with IP + device.
	const sessionRows = await db
		.select({
			id: sessionTable.id,
			userId: sessionTable.userId,
			name: userTable.name,
			email: userTable.email,
			ipAddress: sessionTable.ipAddress,
			userAgent: sessionTable.userAgent,
			createdAt: sessionTable.createdAt,
			expiresAt: sessionTable.expiresAt,
		})
		.from(sessionTable)
		.leftJoin(userTable, eq(sessionTable.userId, userTable.id))
		.orderBy(desc(sessionTable.createdAt))
		.limit(30);

	const [{ n: totalUsers }] = await db
		.select({ n: sql<number>`count(*)::int` })
		.from(userTable);

	return {
		...base,
		totalUsers: Number(totalUsers) || users.length,
		users: users.map((u) => ({
			id: u.id,
			name: u.name,
			email: u.email,
			emailVerified: u.emailVerified,
			image: u.image,
			createdAt: toISO(u.createdAt),
			lastSeen: seen.get(u.id)?.last ?? null,
			sessionCount: seen.get(u.id)?.sessions ?? 0,
			isYou: u.id === myId,
		})),
		sessions: sessionRows.map((s) => ({
			id: s.id,
			userId: s.userId,
			name: s.name,
			email: s.email,
			ipAddress: s.ipAddress,
			userAgent: s.userAgent,
			createdAt: toISO(s.createdAt),
			active: s.expiresAt ? new Date(s.expiresAt as unknown as string).getTime() > Date.now() : false,
		})),
	};
};

function requireAdminAction(locals: App.Locals) {
	if (!locals.user || !adminAllowList().has(locals.user.id)) {
		return fail(403, { message: 'Forbidden' });
	}
	return null;
}

export const actions: Actions = {
	revokeSessions: async ({ request, locals }) => {
		const denied = requireAdminAction(locals);
		if (denied) return denied;

		const form = await request.formData();
		const userId = String(form.get('userId') ?? '');
		if (!userId) return fail(400, { message: 'Missing userId' });

		await db.delete(sessionTable).where(eq(sessionTable.userId, userId));
		return { success: true, message: 'Sessions revoked — that user is now signed out.' };
	},

	deleteUser: async ({ request, locals }) => {
		const denied = requireAdminAction(locals);
		if (denied) return denied;

		const form = await request.formData();
		const userId = String(form.get('userId') ?? '');
		if (!userId) return fail(400, { message: 'Missing userId' });
		if (userId === locals.user!.id) {
			return fail(400, { message: "You can't delete your own admin account." });
		}

		// Cascades to sessions + accounts via FK onDelete: 'cascade'.
		await db.delete(userTable).where(eq(userTable.id, userId));
		return { success: true, message: 'User deleted.' };
	},
};
