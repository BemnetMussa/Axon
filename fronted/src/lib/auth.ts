import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { sveltekitCookies } from 'better-auth/svelte-kit';
import { getRequestEvent } from '$app/server';
import { env } from '$env/dynamic/private';
import { db } from '$lib/server/db';
import * as schema from '$lib/server/auth-schema';

function requireEnv(name: 'BETTER_AUTH_SECRET' | 'GOOGLE_CLIENT_ID' | 'GOOGLE_CLIENT_SECRET'): string {
	const value = env[name]?.trim();
	if (!value) {
		throw new Error(`[auth] Missing required env var: ${name}`);
	}
	return value;
}

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
const authSecret = requireEnv('BETTER_AUTH_SECRET');
const googleClientId = requireEnv('GOOGLE_CLIENT_ID');
const googleClientSecret = requireEnv('GOOGLE_CLIENT_SECRET');

export const auth = betterAuth({
	secret: authSecret,
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
	emailAndPassword: {
		enabled: true,
		requireEmailVerification: false,
	},
	socialProviders: {
		google: {
			clientId: googleClientId,
			clientSecret: googleClientSecret,
		},
	},
	plugins: [sveltekitCookies(getRequestEvent)],
});
