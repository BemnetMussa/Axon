import { describe, it, expect, vi } from 'vitest';

// Mock the module's IO-heavy imports so we can import it in a plain test env and
// exercise the pure fan-out core (dispatchPush) without a DB, real VAPID keys, or
// the web-push package being installed.
vi.mock('$env/dynamic/private', () => ({ env: {} }));
vi.mock('$lib/server/db', () => ({ db: {} }));
vi.mock('web-push', () => ({
	default: { setVapidDetails: vi.fn(), sendNotification: vi.fn() }
}));

import { dispatchPush, type PushRow, type PushSubscriptionInput } from './push-sender';

const rows: PushRow[] = [
	{ endpoint: 'https://push.example/1', p256dh: 'a', auth: 'b' },
	{ endpoint: 'https://push.example/2', p256dh: 'c', auth: 'd' },
	{ endpoint: 'https://push.example/3', p256dh: 'e', auth: 'f' }
];

describe('dispatchPush', () => {
	it('counts successes, marks 410 endpoints dead, and counts other errors as failed', async () => {
		const send = vi.fn(async (sub: PushSubscriptionInput) => {
			if (sub.endpoint.endsWith('/2')) throw { statusCode: 410 };
			if (sub.endpoint.endsWith('/3')) throw { statusCode: 500, message: 'server error' };
		});
		const res = await dispatchPush(rows, { title: 'T', body: 'B' }, send);
		expect(res.sent).toBe(1);
		expect(res.dead).toEqual(['https://push.example/2']);
		expect(res.failed).toBe(1);
		expect(send).toHaveBeenCalledTimes(3);
	});

	it('treats 404 as a dead (prunable) subscription', async () => {
		const send = vi.fn(async () => {
			throw { statusCode: 404 };
		});
		const res = await dispatchPush([rows[0]], { title: 'T', body: 'B' }, send);
		expect(res.dead).toEqual([rows[0].endpoint]);
		expect(res.sent).toBe(0);
		expect(res.failed).toBe(0);
	});

	it('serializes the payload and defaults the click url to /app', async () => {
		const send = vi.fn(async (_sub: PushSubscriptionInput, _data: string) => {});
		await dispatchPush([rows[0]], { title: 'Axon — 2 new signals', body: 'Headline' }, send);
		const data = JSON.parse(send.mock.calls[0][1]);
		expect(data).toEqual({ title: 'Axon — 2 new signals', body: 'Headline', url: '/app' });
	});
});
