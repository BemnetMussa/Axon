import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { sveltekitCookies } from 'better-auth/svelte-kit';
import { getRequestEvent } from '$app/server';
import { db } from '$lib/server/db';
import * as schema from '$lib/server/auth-schema';

export const auth = betterAuth({
	secret: process.env.BETTER_AUTH_SECRET || 'dev-secret-change-me-min-32-chars-long!!',
	baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:5173',
	trustedOrigins: [
		process.env.BETTER_AUTH_URL || 'http://localhost:5173',
		...(process.env.PUBLIC_APP_URL ? [process.env.PUBLIC_APP_URL] : []),
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
