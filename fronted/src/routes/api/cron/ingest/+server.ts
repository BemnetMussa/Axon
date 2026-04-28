import { env } from '$env/dynamic/private';
import type { RequestHandler } from '@sveltejs/kit';

/**
 * Vercel Cron calls this route on a schedule (see vercel.json).
 * Secured with Authorization: Bearer <CRON_SECRET> (set in Vercel project env).
 * Forwards to the FastAPI /ingest endpoint with internal auth headers.
 */
function require(name: 'AXON_INTERNAL_SECRET' | 'INTERNAL_API_URL'): string {
	const v = env[name]?.trim();
	if (!v) throw new Error(`Missing ${name}`);
	return v;
}

async function runIngest(): Promise<Response> {
	const INTERNAL_SECRET = require('AXON_INTERNAL_SECRET');
	const base = require('INTERNAL_API_URL').replace(/\/$/, '');
	const userId = env.CRON_INGEST_USER_ID?.trim() || 'vercel-cron';

	const res = await fetch(`${base}/ingest`, {
		method: 'POST',
		headers: {
			'X-Axon-Internal-Secret': INTERNAL_SECRET,
			'X-Axon-User-Id': userId,
		},
	});
	const text = await res.text();
	const out = new Headers();
	const ct = res.headers.get('content-type');
	if (ct) out.set('Content-Type', ct);
	return new Response(text, { status: res.status, headers: out });
}

function verifyCronAuth(request: Request): boolean {
	const secret = env.CRON_SECRET?.trim();
	if (!secret) return false;
	const auth = request.headers.get('authorization');
	return auth === `Bearer ${secret}`;
}

export const GET: RequestHandler = async ({ request }) => {
	if (!verifyCronAuth(request)) {
		return new Response(JSON.stringify({ detail: 'Unauthorized' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' },
		});
	}
	return runIngest();
};

export const POST: RequestHandler = async ({ request }) => {
	if (!verifyCronAuth(request)) {
		return new Response(JSON.stringify({ detail: 'Unauthorized' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' },
		});
	}
	return runIngest();
};
