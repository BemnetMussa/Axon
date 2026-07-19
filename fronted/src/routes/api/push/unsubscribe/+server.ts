import { json, type RequestHandler } from '@sveltejs/kit';
import { and, eq } from 'drizzle-orm';
import { auth } from '$lib/auth';
import { db } from '$lib/server/db';
import { pushSubscription } from '$lib/server/auth-schema';

/** Remove a push subscription (user turned notifications off on this device). */
export const POST: RequestHandler = async (event) => {
	const session = await auth.api.getSession({ headers: event.request.headers });
	if (!session?.user?.id) {
		return json({ detail: 'Unauthorized' }, { status: 401 });
	}

	let payload: { endpoint?: string };
	try {
		payload = await event.request.json();
	} catch {
		return json({ detail: 'Invalid JSON' }, { status: 400 });
	}

	if (!payload?.endpoint) {
		return json({ detail: 'Missing endpoint' }, { status: 422 });
	}

	await db
		.delete(pushSubscription)
		.where(
			and(
				eq(pushSubscription.endpoint, payload.endpoint),
				eq(pushSubscription.userId, session.user.id)
			)
		);

	return json({ status: 'unsubscribed' });
};
