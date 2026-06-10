import { Boxes, Home, Sparkles, Lightbulb, Github, Flame, AlertTriangle } from 'lucide-svelte';

export type NavItem = {
	id: string | null;
	label: string;
	icon: typeof Home;
};

export const SUGGESTIONS = [
	'Summarize in 3 bullets',
	'What can I build with this?',
	'Who does this affect?',
	'How does this compare to alternatives?',
	'Why does this matter now?',
];

export const NAVIGATION: NavItem[] = [
	{ id: null, label: 'Frontier', icon: Home },
	{ id: 'Trending', label: 'Trending', icon: Flame },
	{ id: 'GitHub', label: 'GitHub', icon: Github },
	{ id: 'AI', label: 'AI & News', icon: Sparkles },
	{ id: 'Discovery', label: 'Cool Tools', icon: Boxes },
	{ id: 'Signal', label: 'Research', icon: Lightbulb },
	{ id: 'Concerns', label: 'Concerns', icon: AlertTriangle },
];

const BRAND_COLORS: Record<string, string> = {
	HackerNews: '#FF6600',
	OpenAI: '#FFFFFF',
	NVIDIA: '#76B900',
	GitHub: '#EDEDED',
	Reddit: '#FF4500',
	ArXiv: '#B31B1B',
	DeepMind: '#2D3436',
	Anthropic: '#D97757',
	ProductHunt: '#DA552F',
	Lobsters: '#AC0000',
	TechCrunch: '#00A562',
	TheVerge: '#FA002A',
	ArsTechnica: '#FF4E00',
	HuggingFace: '#FFD21E',
	GoogleAI: '#4285F4',
	GoogleResearch: '#34A853',
	Together: '#6366F1',
	BAIR: '#FDB515',
	Karpathy: '#4A90D9',
	SimonW: '#5BA65B',
	LilianWeng: '#C084FC',
	'Fast.ai': '#00B4D8',
	Altman: '#9CA3AF',
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
	let d = dateStr;
	if (!d.endsWith('Z') && !d.includes('+') && !d.includes('-', 10)) {
		d += 'Z';
	}
	const date = new Date(d);
	const diff = Date.now() - date.getTime();
	if (diff < 0) return 'Just now';
	const mins = Math.floor(diff / 60_000);
	if (mins < 1) return 'Just now';
	if (mins < 60) return `${mins} min`;
	const hours = Math.floor(diff / 3_600_000);
	if (hours < 24) return `${hours}h ago`;
	const days = Math.floor(hours / 24);
	if (days === 1) return 'Yesterday';
	if (days < 7) return `${days}d ago`;
	if (days < 30) return `${Math.floor(days / 7)}w ago`;
	const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	return `${months[date.getMonth()]} ${date.getDate()}`;
}

/**
 * Estimate reading time from a content string.
 * Returns an empty string if there is not enough content to bother showing.
 */
export function readingTime(text: string): string {
	if (!text) return '';
	const words = text.trim().split(/\s+/).filter(Boolean).length;
	if (words < 30) return '';
	const mins = Math.max(1, Math.round(words / 220));
	return `${mins} min read`;
}

export function formatEngagement(likes: number): string {
	if (!likes || likes <= 0) return '';
	if (likes >= 1000) return `${(likes / 1000).toFixed(1)}k`;
	return String(likes);
}
