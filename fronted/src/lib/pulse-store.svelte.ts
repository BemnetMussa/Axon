import { api, type Pulse } from '$lib/api';

const REFRESH_MS = 60_000;
const CLOCK_MS = 30_000;

let current = $state<Pulse | null>(null);
let now = $state(Date.now());
let refreshTimer: ReturnType<typeof setInterval> | null = null;
let clockTimer: ReturnType<typeof setInterval> | null = null;

async function refresh() {
	try {
		current = await api.getPulse();
	} catch {
		/* keep the last good reading */
	}
}

/** Filter activity shared by the sidebar sweep panel and the mobile header. */
export const pulseStore = {
	get value() {
		return current;
	},
	get now() {
		return now;
	},
	/** Use a reading fetched elsewhere (the signed-out landing page passes its own). */
	set(value: Pulse | null) {
		current = value;
		now = Date.now();
	},
	start() {
		if (refreshTimer) return;
		refresh();
		refreshTimer = setInterval(refresh, REFRESH_MS);
		clockTimer = setInterval(() => (now = Date.now()), CLOCK_MS);
	},
	stop() {
		if (refreshTimer) clearInterval(refreshTimer);
		if (clockTimer) clearInterval(clockTimer);
		refreshTimer = null;
		clockTimer = null;
	}
};
