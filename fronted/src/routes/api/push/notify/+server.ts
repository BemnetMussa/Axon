import { json, type RequestHandler } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { sendToAll, type SendResult } from '$lib/server/push-sender';
import { whyKept } from '$lib/ui';

/**
 * Fan story pushes out to every subscriber. Called server-to-server by the
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

const SOURCE_NAMES: Record<string, string> = {
	HackerNews: 'Hacker News',
	ArXiv: 'arXiv',
	ProductHunt: 'Product Hunt',
	GoogleAI: 'Google AI',
	GoogleResearch: 'Google Research',
	HuggingFace: 'Hugging Face',
	SimonW: 'Simon Willison',
	TheVerge: 'The Verge',
	ArsTechnica: 'Ars Technica',
};

interface PushStory {
	id: number;
	title: string;
	source: string;
	likes: number;
}

function storyBody(story: PushStory): string {
	const source = SOURCE_NAMES[story.source] ?? story.source;
	const reason = whyKept({ source: story.source, likes: Number(story.likes) || 0 });
	return reason ? `${source} · ${reason}` : source;
}

export const POST: RequestHandler = async ({ request }) => {
	if (!authorized(request)) {
		return json({ detail: 'Unauthorized' }, { status: 401 });
	}

	let payload: { count?: number; title?: string; titles?: string[]; stories?: PushStory[] };
	try {
		payload = await request.json();
	} catch {
		payload = {};
	}

	const stories = (Array.isArray(payload?.stories) ? payload.stories : []).filter(
		(s) => Number.isInteger(s?.id) && typeof s?.title === 'string' && s.title.trim()
	);
	if (stories.length > 0) {
		const total: SendResult = { sent: 0, pruned: 0, failed: 0 };
		for (const story of stories) {
			const result = await sendToAll({
				title: story.title.trim(),
				body: storyBody(story),
				url: `/app?story=${story.id}`,
				tag: `axon-story-${story.id}`
			});
			total.sent += result.sent;
			total.pruned += result.pruned;
			total.failed += result.failed;
		}
		return json({ status: 'sent', stories: stories.length, ...total });
	}

	// Summary payload from a backend that predates per-story pushes.
	const count = Number(payload?.count) || 0;
	if (count <= 0) {
		return json({ status: 'skipped', reason: 'no new signals' });
	}

	const titles = (Array.isArray(payload?.titles) ? payload.titles : [payload?.title])
		.map((t) => (typeof t === 'string' ? t.trim() : ''))
		.filter(Boolean)
		.slice(0, 2);
	const rest = count - titles.length;
	const lines = titles.map((t) => `· ${t}`);
	if (rest > 0) lines.push(`+${rest} more in your feed`);

	const result = await sendToAll({
		title: count === 1 ? '1 new story made the cut' : `${count} new stories made the cut`,
		body: lines.join('\n') || 'A new sweep just landed. Tap to read.',
		url: '/app'
	});

	return json({ status: 'sent', ...result });
};
