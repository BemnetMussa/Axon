import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { sveltekitCookies } from 'better-auth/svelte-kit';
import { getRequestEvent } from '$app/server';
import { db } from '$lib/server/db';
import * as schema from '$lib/server/auth-schema';

/** Fallback when host cannot be inferred (OAuth state, logs). Not used as request base if dynamic URL matches. */
function fallbackBaseUrl(): string {
	const explicit = process.env.BETTER_AUTH_URL?.trim();
	if (explicit) return explicit.replace(/\/$/, '');
	const production = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
	if (production) return `https://${production.replace(/^https?:\/\//, '').replace(/\/$/, '')}`;
	if (process.env.VERCEL_URL)
		return `https://${process.env.VERCEL_URL.replace(/^https?:\/\//, '').replace(/\/$/, '')}`;
	return 'http://localhost:5173';
}

function buildAllowedHosts(): string[] {
	const hosts = new Set<string>(['localhost:5173', '127.0.0.1:5173', '*.vercel.app']);
	const pub = process.env.PUBLIC_APP_URL?.trim();
	if (pub) {
		try {
			hosts.add(new URL(pub).host);
		} catch {
			/* ignore */
		}
	}
	for (const h of process.env.BETTER_AUTH_ALLOWED_HOSTS?.split(',') ?? []) {
		const t = h.trim();
		if (t) hosts.add(t);
	}
	return [...hosts];
}

const fallback = fallbackBaseUrl();

export const auth = betterAuth({
	secret: process.env.BETTER_AUTH_SECRET || 'dev-secret-change-me-min-32-chars-long!!',
	// Dynamic base URL: OAuth redirect_uri and SvelteKit isAuthPath match the *actual* request host
	// (fixes production when BETTER_AUTH_URL was wrong or preview vs production hostname differs).
	baseURL: {
		allowedHosts: buildAllowedHosts(),
		fallback,
	},
	trustedOrigins: [
		fallback,
		...(process.env.PUBLIC_APP_URL ? [process.env.PUBLIC_APP_URL.replace(/\/$/, '')] : []),
	],
	database: drizzleAdapter(db, {
		provider: 'pg',
		schema,
	}),
	socialProviders: {
		google: {
			clientId: process.env.GOOGLE_CLIENT_ID as string,
			clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
		},
	},
	plugins: [sveltekitCookies(getRequestEvent)],
});
