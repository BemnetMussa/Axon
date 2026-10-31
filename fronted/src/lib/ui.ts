import { Boxes, Home, Lightbulb, Github, Flame } from 'lucide-svelte';

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

// The only way to narrow the feed besides search. Each tab is server-paginated,
// so "Load more" pulls the next page *of that tab*. Ids are the backend category
// ids ('GitHub' is a source filter, 'Trending' its own endpoint; see feedParams).
export const NAVIGATION: NavItem[] = [
	{ id: null, label: 'Frontier', icon: Home },
	{ id: 'Trending', label: 'Trending', icon: Flame },
	{ id: 'Signal', label: 'Research', icon: Lightbulb },
	{ id: 'Discovery', label: 'Tools', icon: Boxes },
	{ id: 'GitHub', label: 'GitHub', icon: Github },
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

// Backend sends naive UTC datetimes; without the Z they would parse as local time.
function parseApiDate(dateStr: string): Date {
	let d = dateStr;
	if (!d.endsWith('Z') && !d.includes('+') && !d.includes('-', 10)) {
		d += 'Z';
	}
	return new Date(d);
}

export function relativeTime(dateStr: string): string {
	if (!dateStr) return '';
	const date = parseApiDate(dateStr);
	const diff = Date.now() - date.getTime();
	if (diff < 0) return 'Just now';
	const mins = Math.floor(diff / 60_000);
	if (mins < 1) return 'Just now';
	if (mins < 60) return `${mins}m ago`;
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

// Card labels use the tab words, so a "Research" card lives under the Research tab.
const CATEGORY_LABELS: Record<string, string> = {
	Signal: 'Research',
	Discovery: 'Tools',
	Momentum: 'Rising',
	Concerns: 'Discussion',
};

export function categoryLabel(category: string): string {
	return CATEGORY_LABELS[category] ?? category;
}

const ENGAGEMENT_UNITS: Record<string, string> = {
	HackerNews: 'points',
	Lobsters: 'points',
	GitHub: 'stars',
	ProductHunt: 'votes',
	Reddit: 'upvotes',
};

const PRIMARY_SOURCES = new Set([
	'OpenAI', 'Anthropic', 'DeepMind', 'GoogleAI', 'GoogleResearch', 'HuggingFace', 'NVIDIA', 'Together', 'BAIR',
	'Karpathy', 'SimonW', 'LilianWeng', 'Altman', 'Fast.ai',
]);

/** The main reason a story made the cut, in the filter's own terms (traction or source trust). */
export function whyKept(article: { source: string; likes: number }): string {
	const count = formatEngagement(article.likes);
	if (count) {
		const unit = ENGAGEMENT_UNITS[article.source];
		return unit ? `${count} ${unit}` : count;
	}
	if (article.source === 'ArXiv') return 'New paper';
	if (PRIMARY_SOURCES.has(article.source)) return 'Primary source';
	return '';
}

export function formatDate(dateStr: string): string {
	if (!dateStr) return '';
	return parseApiDate(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export function hostname(url: string): string {
	try {
		return new URL(url).hostname.replace(/^www\./, '');
	} catch {
		return '';
	}
}

/** UTC calendar day, matching the backend's day bucket for feed ordering. */
export function utcDay(dateStr: string): number {
	return Math.floor(parseApiDate(dateStr).getTime() / 86_400_000);
}

export function dayLabel(dateStr: string, now = Date.now()): string {
	const diff = Math.floor(now / 86_400_000) - utcDay(dateStr);
	if (diff <= 0) return 'Today';
	if (diff === 1) return 'Yesterday';
	return parseApiDate(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' });
}
