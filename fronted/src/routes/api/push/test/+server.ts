import { json, type RequestHandler } from '@sveltejs/kit';
import { auth } from '$lib/auth';
import { sendToUser } from '$lib/server/push-sender';

/**
 * Fire a test notification to the current user's own devices — lets you verify the
 * whole chain (subscription stored → VAPID configured → SW renders it) after setup,
 * without waiting for an ingest.
 */
export const POST: RequestHandler = async (event) => {
	const session = await auth.api.getSession({ headers: event.request.headers });
	if (!session?.user?.id) {
		return json({ detail: 'Unauthorized' }, { status: 401 });
	}

	const result = await sendToUser(session.user.id, {
		title: 'Notifications are on',
		body: 'You’ll get one ping per sweep, with the top stories that made the cut.',
		url: '/app'
	});

	return json({ status: 'sent', ...result });
};
