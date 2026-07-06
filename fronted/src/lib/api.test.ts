import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { api, feedCache, type Article } from './api';

function makeArticle(id: number, overrides: Partial<Article> = {}): Article {
	return {
		id,
		title: `Article ${id}`,
		url: `https://example.com/${id}`,
		source: 'HackerNews',
		published_date: new Date().toISOString(),
		content_snippet: 'snippet',
		category: 'AI',
		views: 0,
		likes: 0,
		engagement_score: 0,
		...overrides
	};
}

const baseCache = {
	articles: [makeArticle(1), makeArticle(2)],
	trends: [],
	nextCursor: 'cursor-a',
	hasMore: true
};

describe('feedCache', () => {
	beforeEach(() => {
		localStorage.clear();
		vi.useFakeTimers();
	});
	afterEach(() => {
		vi.useRealTimers();
	});

	it('roundtrips a cache entry', () => {
		feedCache.set(baseCache);
		const got = feedCache.get();
		expect(got?.articles.map((a) => a.id)).toEqual([1, 2]);
		expect(got?.nextCursor).toBe('cursor-a');
	});

	it('returns null for missing or corrupt entries', () => {
		expect(feedCache.get()).toBeNull();
		localStorage.setItem('axon_feed_cache_v2', '{not json');
		expect(feedCache.get()).toBeNull();
	});

	it('is fresh under 3 minutes, usable under 30, then dead', () => {
		feedCache.set(baseCache);
		expect(feedCache.isFresh()).toBe(true);
		expect(feedCache.isUsable()).toBe(true);

		vi.advanceTimersByTime(4 * 60 * 1000);
		expect(feedCache.isFresh()).toBe(false);
		expect(feedCache.isUsable()).toBe(true);

		vi.advanceTimersByTime(27 * 60 * 1000);
		expect(feedCache.isUsable()).toBe(false);
	});

	it('appendPage dedupes by id and advances the cursor', () => {
		feedCache.set(baseCache);
		feedCache.appendPage([makeArticle(2), makeArticle(3)], 'cursor-b', false);
		const got = feedCache.get();
		expect(got?.articles.map((a) => a.id)).toEqual([1, 2, 3]);
		expect(got?.nextCursor).toBe('cursor-b');
		expect(got?.hasMore).toBe(false);
	});

	it('prependNew puts unseen articles first and keeps the cursor', () => {
		feedCache.set(baseCache);
		feedCache.prependNew([makeArticle(5), makeArticle(1)]);
		const got = feedCache.get();
		expect(got?.articles.map((a) => a.id)).toEqual([5, 1, 2]);
		expect(got?.nextCursor).toBe('cursor-a');
	});

	it('latestId returns the max id', () => {
		expect(feedCache.latestId()).toBeNull();
		feedCache.set({ ...baseCache, articles: [makeArticle(7), makeArticle(3)] });
		expect(feedCache.latestId()).toBe(7);
	});
});

describe('api error handling', () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it('throws with status and body on non-ok responses', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue(new Response('boom', { status: 500 }))
		);
		await expect(api.getTrends()).rejects.toThrow('API 500: boom');
	});

	it('parses json on ok responses', async () => {
		const payload = { articles: [], next_cursor: null, has_more: false };
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue(
				new Response(JSON.stringify(payload), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			)
		);
		await expect(api.getArticles()).resolves.toEqual(payload);
	});

	it('sends filters and cursor as query params', async () => {
		const spy = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ articles: [], next_cursor: null, has_more: false }), {
				status: 200
			})
		);
		vi.stubGlobal('fetch', spy);
		await api.getArticles('cur123', 10, { category: 'Signal' });
		const url = String(spy.mock.calls[0][0]);
		expect(url).toContain('cursor=cur123');
		expect(url).toContain('category=Signal');
	});

	it('countNewSince falls back to 0 when the field is missing', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
		);
		await expect(api.countNewSince(10)).resolves.toBe(0);
	});
});
