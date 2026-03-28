import { auth } from '$lib/auth';
import { env } from '$env/dynamic/private';
import type { RequestEvent, RequestHandler } from '@sveltejs/kit';

function upstreamBase(): string {
	return env.INTERNAL_API_URL || 'http://127.0.0.1:8000';
}

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

	const secret = env.AXON_INTERNAL_SECRET;
	if (!secret) {
		return new Response(JSON.stringify({ detail: 'AXON_INTERNAL_SECRET not configured' }), {
			status: 500,
			headers: { 'Content-Type': 'application/json' },
		});
	}

	const path = event.params.path ?? '';
	const url = `${upstreamBase().replace(/\/$/, '')}/${path}${event.url.search}`;

	const headers: Record<string, string> = {
		'X-Axon-User-Id': session.user.id,
		'X-Axon-Internal-Secret': secret,
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
