import { createAuthClient } from 'better-auth/svelte';

export const authClient = createAuthClient({
	baseURL: typeof window !== 'undefined' ? window.location.origin : undefined,
});

export async function signOutToHome() {
	try {
		await authClient.signOut();
	} finally {
		window.location.href = '/';
	}
}
