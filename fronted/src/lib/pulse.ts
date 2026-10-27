import type { Pulse } from '$lib/api';

/** "just now" / "12m ago" / "3h ago" / "2d ago". */
export function sweepAgo(iso: string | null | undefined, now = Date.now()): string {
	if (!iso) return '—';
	const secs = Math.max(0, (now - new Date(iso).getTime()) / 1000);
	if (secs < 60) return 'just now';
	if (secs < 3600) return `${Math.floor(secs / 60)}m ago`;
	if (secs < 86_400) return `${Math.floor(secs / 3600)}h ago`;
	return `${Math.floor(secs / 86_400)}d ago`;
}

/** "in 3h 48m" / "in 12m" / "due now". */
export function sweepIn(iso: string | null | undefined, now = Date.now()): string {
	if (!iso) return '—';
	const mins = Math.round((new Date(iso).getTime() - now) / 60_000);
	if (mins <= 0) return 'due now';
	if (mins < 60) return `in ${mins}m`;
	const h = Math.floor(mins / 60);
	const m = mins % 60;
	return m ? `in ${h}h ${m}m` : `in ${h}h`;
}

/** Share of scanned items that made it into the feed, as a 0–100 integer. */
export function keptPercent(scanned: number, kept: number): number | null {
	if (!scanned || scanned <= 0) return null;
	return Math.max(0, Math.min(100, Math.round((kept / scanned) * 100)));
}

/**
 * The most useful scanned/kept pair to show: the last 24h when there was a
 * sweep in that window, otherwise the most recent sweep on its own.
 */
export function pulseWindow(p: Pulse | null | undefined): { scanned: number; kept: number; label: string } | null {
	if (!p) return null;
	if (p.scanned_24h > 0) return { scanned: p.scanned_24h, kept: p.kept_24h, label: '24h' };
	if (p.last_scanned > 0) return { scanned: p.last_scanned, kept: p.last_kept, label: 'last sweep' };
	return null;
}

export function formatCount(n: number): string {
	return n >= 10_000 ? `${(n / 1000).toFixed(1)}k` : n.toLocaleString('en-US');
}
