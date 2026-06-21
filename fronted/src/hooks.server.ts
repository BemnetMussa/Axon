import { auth } from '$lib/auth';
import { svelteKitHandler } from 'better-auth/svelte-kit';
import { building } from '$app/environment';
import type { Handle, HandleServerError } from '@sveltejs/kit';

// Surface the real cause of 500s. Without this, SvelteKit renders the generic
// +error.svelte and the underlying stack trace is lost. The errorId is shown to
// the user and printed here so a report can be matched to its server log line.
export const handleError: HandleServerError = ({ error, event, status, message }) => {
	const errorId = crypto.randomUUID();
	console.error(
		`[error] id=${errorId} ${status} ${message} — ${event.request.method} ${event.url.pathname}`,
		error,
	);
	return { message, errorId };
};

export const handle: Handle = async ({ event, resolve }) => {
	try {
		const session = await auth.api.getSession({
			headers: event.request.headers,
		});
		if (session) {
			event.locals.session = session.session;
			event.locals.user = session.user;
		} else {
			event.locals.session = null;
			event.locals.user = null;
		}
	} catch (e) {
		console.error('[auth] getSession failed', e);
		event.locals.session = null;
		event.locals.user = null;
	}

	return svelteKitHandler({ event, resolve, auth, building });
};

