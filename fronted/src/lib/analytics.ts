/**
 * Thin wrapper around PostHog that no-ops gracefully when PostHog is not
 * configured (no VITE_POSTHOG_KEY set) or not yet loaded.
 *
 * Usage:
 *   import { track, identify } from '$lib/analytics';
 *   track('article_opened', { article_id: 123, source: 'HackerNews' });
 */

declare global {
	interface Window {
		posthog?: {
			capture: (event: string, properties?: Record<string, unknown>) => void;
			identify: (userId: string, properties?: Record<string, unknown>) => void;
			reset: () => void;
		};
	}
}

function ph() {
	return typeof window !== 'undefined' ? window.posthog : undefined;
}

export function track(event: string, properties?: Record<string, unknown>) {
	ph()?.capture(event, properties);
}

export function identify(userId: string, properties?: Record<string, unknown>) {
	ph()?.identify(userId, properties);
}

export function resetAnalytics() {
	ph()?.reset();
}

// ── Typed event helpers ─────────────────────────────────────────────────────

export const analytics = {
	articleOpened: (articleId: number, source: string, category: string) =>
		track('article_opened', { article_id: articleId, source, category }),

	chatStarted: (articleId: number, trigger: 'suggestion' | 'manual') =>
		track('chat_started', { article_id: articleId, trigger }),

	articleSaved: (articleId: number, saved: boolean) =>
		track('article_saved', { article_id: articleId, saved }),

	searchPerformed: (query: string, mode: 'local' | 'semantic', resultCount: number) =>
		track('search_performed', { query: query.slice(0, 60), mode, result_count: resultCount }),

	digestOpened: () => track('digest_opened'),

	digestGenerated: () => track('digest_generated'),

	syncSources: (category: string | null) =>
		track('sync_sources', { category: category ?? 'all' }),

	onboardingCompleted: () => track('onboarding_completed'),

	topicChipClicked: (keyword: string) => track('topic_chip_clicked', { keyword }),
};
