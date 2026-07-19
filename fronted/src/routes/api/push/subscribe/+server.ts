import { json, type RequestHandler } from '@sveltejs/kit';
import { auth } from '$lib/auth';
import { db } from '$lib/server/db';
import { pushSubscription } from '$lib/server/auth-schema';

/**
 * Store (or refresh) a Web Push subscription for the logged-in user. The body is a
 * browser PushSubscription JSON: { endpoint, keys: { p256dh, auth } }. Keyed on the
 * globally-unique endpoint, so re-enabling on the same device upserts in place and a
 * device that switches accounts is re-pointed at the new user.
 */
export const POST: RequestHandler = async (event) => {
	const session = await auth.api.getSession({ headers: event.request.headers });
	if (!session?.user?.id) {
		return json({ detail: 'Unauthorized' }, { status: 401 });
	}

	let payload: { endpoint?: string; keys?: { p256dh?: string; auth?: string } };
	try {
		payload = await event.request.json();
	} catch {
		return json({ detail: 'Invalid JSON' }, { status: 400 });
	}

	const endpoint = payload?.endpoint;
	const p256dh = payload?.keys?.p256dh;
	const auth_ = payload?.keys?.auth;
	if (!endpoint || !p256dh || !auth_) {
		return json({ detail: 'Missing subscription fields' }, { status: 422 });
	}

	await db
		.insert(pushSubscription)
		.values({
			id: crypto.randomUUID(),
			userId: session.user.id,
			endpoint,
			p256dh,
			auth: auth_,
			createdAt: new Date()
		})
		.onConflictDoUpdate({
			target: pushSubscription.endpoint,
			set: { userId: session.user.id, p256dh, auth: auth_ }
		});

	return json({ status: 'subscribed' });
};
