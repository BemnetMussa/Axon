import { auth } from '$lib/auth';
import { env } from '$env/dynamic/private';
import type { RequestEvent, RequestHandler } from '@sveltejs/kit';

function requireEnv(name: 'AXON_INTERNAL_SECRET' | 'INTERNAL_API_URL'): string {
	const value = env[name]?.trim();
	if (!value) {
		throw new Error(`[api/backend proxy] Missing required env var: ${name}`);
	}
	return value;
}

const INTERNAL_SECRET = requireEnv('AXON_INTERNAL_SECRET');
const INTERNAL_API_URL = requireEnv('INTERNAL_API_URL');

async function proxy(event: RequestEvent, method: string): Promise<Response> {
	const session = await auth.api.getSession({
		headers: event.request.headers,
	});
	if (!session?.user?.id) {
		return new Response(JSON.stringify({ detail: 'Unauthorized' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' },
		});
	}

	const path = event.params.path ?? '';
	const url = `${INTERNAL_API_URL.replace(/\/$/, '')}/${path}${event.url.search}`;

	const headers: Record<string, string> = {
		'X-Axon-User-Id': session.user.id,
		'X-Axon-Internal-Secret': INTERNAL_SECRET,
	};
	const contentType = event.request.headers.get('content-type');
	if (contentType) headers['Content-Type'] = contentType;

	const init: RequestInit = { method, headers };
	if (!['GET', 'HEAD'].includes(method)) {
		const buf = await event.request.arrayBuffer();
		if (buf.byteLength) init.body = buf;
	}

	const res = await fetch(url, init);
	const outHeaders = new Headers();
	const ct = res.headers.get('content-type');
	if (ct) outHeaders.set('Content-Type', ct);
	return new Response(await res.arrayBuffer(), { status: res.status, headers: outHeaders });
}

export const GET: RequestHandler = (e) => proxy(e, 'GET');
export const POST: RequestHandler = (e) => proxy(e, 'POST');
export const PUT: RequestHandler = (e) => proxy(e, 'PUT');
export const PATCH: RequestHandler = (e) => proxy(e, 'PATCH');
export const DELETE: RequestHandler = (e) => proxy(e, 'DELETE');
