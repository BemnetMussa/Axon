import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { sveltekitCookies } from 'better-auth/svelte-kit';
import { getRequestEvent } from '$app/server';
import { env } from '$env/dynamic/private';
import { db } from '$lib/server/db';
import * as schema from '$lib/server/auth-schema';

function fallbackBaseUrl(): string {
	const explicit = env.BETTER_AUTH_URL?.trim();
	if (explicit) return explicit.replace(/\/$/, '');
	const production = env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
	if (production) return `https://${production.replace(/^https?:\/\//, '').replace(/\/$/, '')}`;
	if (env.VERCEL_URL)
		return `https://${env.VERCEL_URL.replace(/^https?:\/\//, '').replace(/\/$/, '')}`;
	return 'http://localhost:5173';
}

function buildAllowedHosts(): string[] {
	const hosts = new Set<string>(['localhost:5173', '127.0.0.1:5173', '*.vercel.app']);
	const pub = (env.PUBLIC_APP_URL as string | undefined)?.trim();
	if (pub) {
		try {
			hosts.add(new URL(pub).host);
		} catch {
			/* ignore */
		}
	}
	for (const h of env.BETTER_AUTH_ALLOWED_HOSTS?.split(',') ?? []) {
		const t = h.trim();
		if (t) hosts.add(t);
	}
	return [...hosts];
}

const fallback = fallbackBaseUrl();

export const auth = betterAuth({
	secret: env.BETTER_AUTH_SECRET || 'dev-secret-change-me-min-32-chars-long!!',
	baseURL: {
		allowedHosts: buildAllowedHosts(),
		fallback,
	},
	trustedOrigins: [
		fallback,
		...(env.PUBLIC_APP_URL ? [(env.PUBLIC_APP_URL as string).replace(/\/$/, '')] : []),
	],
	database: drizzleAdapter(db, {
		provider: 'pg',
		schema,
	}),
	socialProviders: {
		google: {
			clientId: env.GOOGLE_CLIENT_ID as string,
			clientSecret: env.GOOGLE_CLIENT_SECRET as string,
		},
	},
	plugins: [sveltekitCookies(getRequestEvent)],
});
