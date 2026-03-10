import { AlertCircle, Boxes, Home, Sparkles, TrendingUp } from 'lucide-svelte';

export type NavItem = {
	id: string | null;
	label: string;
	icon: typeof Home;
};

export const SUGGESTIONS = [
	'Technical primitives?',
	'Architecture shift?',
	'Data moat?',
	'Strategic impact?',
	'Build opportunity?'
];

export const NAVIGATION: NavItem[] = [
	{ id: null, label: 'All Signals', icon: Home },
	{ id: 'AI', label: 'AI & Research', icon: Sparkles },
	{ id: 'Discovery', label: 'Cool Tools', icon: Boxes },
	{ id: 'Momentum', label: 'Momentum', icon: TrendingUp },
	{ id: 'Concerns', label: 'Concerns', icon: AlertCircle }
];

const BRAND_COLORS: Record<string, string> = {
	HackerNews: '#FF6600',
	OpenAI: '#FFFFFF',
	NVIDIA: '#76B900',
	GitHub: '#EDEDED',
	Reddit: '#FF4500',
	ArXiv: '#B31B1B',
	DeepMind: '#2D3436',
	Anthropic: '#D97757'
};

export function getBrandColor(source: string) {
	return BRAND_COLORS[source] || '#3f3f46';
}

export function stripHtml(content: string): string {
	return (content ?? '')
		.replace(/<[^>]*>/g, '')
		.replace(/&[a-z#0-9]+;/gi, ' ')
		.replace(/\s+/g, ' ')
		.trim();
}

export function relativeTime(dateStr: string): string {
	if (!dateStr) return '';
	const diff = Date.now() - new Date(dateStr).getTime();
	const hours = Math.floor(diff / 3_600_000);
	if (hours < 1) return `${Math.max(1, Math.floor(diff / 60_000))}m`;
	if (hours < 24) return `${hours}h`;
	return `${Math.floor(hours / 24)}d`;
}