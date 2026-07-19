import { json, type RequestHandler } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { sendToAll } from '$lib/server/push-sender';

/**
 * Fan a "new signals" push out to every subscriber. Called server-to-server by the
 * backend after a productive ingest (see backend/app/main.py _notify_new_signals),
 * so it is guarded by a shared secret rather than a user session. Accepts either the
 * internal secret both services already share, or the cron bearer token.
 */
function authorized(request: Request): boolean {
	const internal = env.AXON_INTERNAL_SECRET?.trim();
	if (internal && request.headers.get('x-axon-internal-secret') === internal) return true;

	const cron = env.CRON_SECRET?.trim();
	if (cron && request.headers.get('authorization') === `Bearer ${cron}`) return true;

	return false;
}

export const POST: RequestHandler = async ({ request }) => {
	if (!authorized(request)) {
		return json({ detail: 'Unauthorized' }, { status: 401 });
	}

	let payload: { count?: number; title?: string };
	try {
		payload = await request.json();
	} catch {
		payload = {};
	}

	const count = Number(payload?.count) || 0;
	if (count <= 0) {
		return json({ status: 'skipped', reason: 'no new signals' });
	}

	const headline = payload?.title?.trim();
	const label = count === 1 ? '1 new signal' : `${count} new signals`;
	const result = await sendToAll({
		title: `Axon — ${label}`,
		body: headline || 'Fresh intelligence just landed. Tap to catch up.',
		url: '/app'
	});

	return json({ status: 'sent', ...result });
};
