import { env } from '$env/dynamic/private';
import type { Pulse } from '$lib/api';
import type { PageServerLoad } from './$types';

// Live filter numbers for the landing readout. Visitors are signed out, so this
// calls the API directly with the internal secret; any failure just hides the
// numbers rather than breaking the page.
export const load: PageServerLoad = async ({ fetch }) => {
	const base = env.INTERNAL_API_URL?.trim();
	const secret = env.AXON_INTERNAL_SECRET?.trim();
	if (!base || !secret) return { pulse: null };

	try {
		const res = await fetch(`${base.replace(/\/$/, '')}/pulse`, {
			headers: { 'X-Axon-Internal-Secret': secret, 'X-Axon-User-Id': 'landing' },
			signal: AbortSignal.timeout(1500)
		});
		if (!res.ok) return { pulse: null };
		return { pulse: (await res.json()) as Pulse };
	} catch {
		return { pulse: null };
	}
};
