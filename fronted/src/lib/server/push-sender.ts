import webpush from 'web-push';
import { eq, inArray } from 'drizzle-orm';
import { env } from '$env/dynamic/private';
import { db } from './db';
import { pushSubscription } from './auth-schema';

export interface PushPayload {
	title: string;
	body: string;
	/** Path the SW opens on click. Defaults to /app. */
	url?: string;
}

export interface PushRow {
	endpoint: string;
	p256dh: string;
	auth: string;
}

/** Shape web-push expects for a subscription (structurally its PushSubscription). */
export interface PushSubscriptionInput {
	endpoint: string;
	keys: { p256dh: string; auth: string };
}

export interface SendResult {
	sent: number;
	pruned: number;
	failed: number;
}

// Configure VAPID once, lazily — the keys are runtime env, and a missing key must
// degrade to a no-op (push simply disabled) rather than crash the whole app on boot.
let configured: boolean | null = null;
function ensureConfigured(): boolean {
	if (configured !== null) return configured;
	const publicKey = env.VAPID_PUBLIC_KEY?.trim();
	const privateKey = env.VAPID_PRIVATE_KEY?.trim();
	const subject = env.VAPID_SUBJECT?.trim() || 'mailto:admin@axon.app';
	if (!publicKey || !privateKey) {
		console.warn('[push] VAPID keys not set — push notifications disabled');
		configured = false;
		return false;
	}
	webpush.setVapidDetails(subject, publicKey, privateKey);
	configured = true;
	return true;
}

function serialize(payload: PushPayload): string {
	return JSON.stringify({
		title: payload.title,
		body: payload.body,
		url: payload.url ?? '/app'
	});
}

/**
 * Pure fan-out core: sends `payload` to every row via the injected `send` fn and
 * classifies the outcome. Endpoints the push service reports as gone (404/410) are
 * returned in `dead` so the caller can prune them; other errors count as `failed`
 * (transient — keep the subscription). No DB or network of its own, so it's unit
 * testable without a database or real VAPID keys.
 */
export async function dispatchPush(
	rows: PushRow[],
	payload: PushPayload,
	send: (subscription: PushSubscriptionInput, data: string) => Promise<unknown>
): Promise<{ sent: number; dead: string[]; failed: number }> {
	const data = serialize(payload);
	const dead: string[] = [];
	let sent = 0;
	let failed = 0;

	await Promise.all(
		rows.map(async (row) => {
			try {
				await send({ endpoint: row.endpoint, keys: { p256dh: row.p256dh, auth: row.auth } }, data);
				sent++;
			} catch (err) {
				const code = (err as { statusCode?: number }).statusCode;
				if (code === 404 || code === 410) {
					dead.push(row.endpoint);
				} else {
					failed++;
					console.error('[push] send failed', code ?? '', (err as Error).message);
				}
			}
		})
	);

	return { sent, dead, failed };
}

async function sendToRows(rows: PushRow[], payload: PushPayload): Promise<SendResult> {
	if (!ensureConfigured() || rows.length === 0) {
		return { sent: 0, pruned: 0, failed: 0 };
	}
	const { sent, dead, failed } = await dispatchPush(rows, payload, (sub, data) =>
		webpush.sendNotification(sub, data)
	);
	if (dead.length > 0) {
		try {
			await db.delete(pushSubscription).where(inArray(pushSubscription.endpoint, dead));
		} catch (e) {
			console.error('[push] failed to prune dead subscriptions', (e as Error).message);
		}
	}
	return { sent, pruned: dead.length, failed };
}

/** Push to every subscribed device across all users (the ingest fan-out). */
export async function sendToAll(payload: PushPayload): Promise<SendResult> {
	if (!ensureConfigured()) return { sent: 0, pruned: 0, failed: 0 };
	const rows = await db
		.select({
			endpoint: pushSubscription.endpoint,
			p256dh: pushSubscription.p256dh,
			auth: pushSubscription.auth
		})
		.from(pushSubscription);
	return sendToRows(rows, payload);
}

/** Push to a single user's devices — used by the self-test endpoint. */
export async function sendToUser(userId: string, payload: PushPayload): Promise<SendResult> {
	if (!ensureConfigured()) return { sent: 0, pruned: 0, failed: 0 };
	const rows = await db
		.select({
			endpoint: pushSubscription.endpoint,
			p256dh: pushSubscription.p256dh,
			auth: pushSubscription.auth
		})
		.from(pushSubscription)
		.where(eq(pushSubscription.userId, userId));
	return sendToRows(rows, payload);
}
