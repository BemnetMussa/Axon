/** Proxied through SvelteKit (`/api/backend`) so FastAPI receives internal auth headers. */
const BASE_URL = '/api/backend';

async function failIfNotOk(res: Response): Promise<void> {
    if (res.ok) return;
    let body = '';
    try {
        body = await res.text();
    } catch {
        body = '';
    }
    throw new Error(`API ${res.status}${body ? `: ${body}` : ''}`);
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
    await failIfNotOk(res);
    return res.json() as Promise<T>;
}

export interface Trend {
    keyword: string;
    count: number;
    velocity: string;
    is_new: boolean;
}

export interface Article {
    id: number;
    title: string;
    url: string;
    source: string;
    published_date: string;
    content_snippet: string;
    full_content?: string;
    category: string;
    views: number;
    likes: number;
    engagement_score: number;
    insight?: string;
}

export interface ArticlesResponse {
    articles: Article[];
    next_cursor: number | null;
    has_more: boolean;
}

const PAGE_SIZE = 10;

export const api = {
    getTrends: async (): Promise<Trend[]> => {
        const res = await fetch(`${BASE_URL}/trends`);
        return jsonOrThrow<Trend[]>(res);
    },

    getArticles: async (cursor?: number | null, limit = PAGE_SIZE): Promise<ArticlesResponse> => {
        const params = new URLSearchParams({ limit: String(limit) });
        if (cursor) params.set('cursor', String(cursor));
        const res = await fetch(`${BASE_URL}/articles?${params}`);
        return jsonOrThrow<ArticlesResponse>(res);
    },

    countNewSince: async (sinceId: number): Promise<number> => {
        const res = await fetch(`${BASE_URL}/articles/count-since?since_id=${sinceId}`);
        const data = await jsonOrThrow<{ new_count?: number }>(res);
        return data.new_count ?? 0;
    },

    getArticleContent: async (id: number): Promise<{ content: string }> => {
        const res = await fetch(`${BASE_URL}/articles/${id}/content`);
        return jsonOrThrow<{ content: string }>(res);
    },

    triggerRefresh: async (contextId?: string | null) => {
        let url = `${BASE_URL}/ingest`;
        if (contextId) {
            url += `?context_id=${encodeURIComponent(contextId === 'GitHub' ? 'GitHub' : contextId)}`;
        }
        await failIfNotOk(await fetch(url, { method: 'POST' }));
        await failIfNotOk(await fetch(`${BASE_URL}/analyze`, { method: 'POST' }));
    },

    trackView: async (id: number) => {
        await failIfNotOk(await fetch(`${BASE_URL}/articles/${id}/view`, { method: 'POST' }));
    },

    chatWithArticle: async (id: number, question: string): Promise<{ answer: string }> => {
        const res = await fetch(`${BASE_URL}/articles/${id}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        return jsonOrThrow<{ answer: string }>(res);
    },

    getChatSuggestions: async (id: number): Promise<{ suggestions: string[] }> => {
        const res = await fetch(`${BASE_URL}/articles/${id}/suggestions`);
        return jsonOrThrow<{ suggestions: string[] }>(res);
    },

    getBrief: async (id: number): Promise<{ title: string; brief: string }> => {
        const res = await fetch(`${BASE_URL}/brief/${id}`);
        return jsonOrThrow<{ title: string; brief: string }>(res);
    },

    searchSemantic: async (query: string): Promise<{ articles: Article[] }> => {
        const params = new URLSearchParams({ query });
        const res = await fetch(`${BASE_URL}/search/semantic?${params}`);
        return jsonOrThrow<{ articles: Article[] }>(res);
    },

    getLatestDigest: async (): Promise<{ content: string; created_at: string }> => {
        const res = await fetch(`${BASE_URL}/digests/latest`);
        return jsonOrThrow<{ content: string; created_at: string }>(res);
    },

    generateDigest: async (): Promise<{ status: string; digest?: string; detail?: string }> => {
        const res = await fetch(`${BASE_URL}/digests/generate`, { method: 'POST' });
        return jsonOrThrow<{ status: string; digest?: string; detail?: string }>(res);
    }
};


// ---------------------------------------------------------------------------
// localStorage cache with TTL
// ---------------------------------------------------------------------------

const CACHE_KEY = 'axon_feed_cache';
const CACHE_TTL_MS = 3 * 60 * 1000; // 3 minutes = "fresh"
const STALE_TTL_MS = 30 * 60 * 1000; // 30 minutes = still usable as stale

interface FeedCache {
    articles: Article[];
    trends: Trend[];
    nextCursor: number | null;
    hasMore: boolean;
    timestamp: number;
}

export const feedCache = {
    get(): FeedCache | null {
        try {
            const raw = localStorage.getItem(CACHE_KEY);
            if (!raw) return null;
            return JSON.parse(raw) as FeedCache;
        } catch {
            return null;
        }
    },

    set(data: Omit<FeedCache, 'timestamp'>) {
        const entry: FeedCache = { ...data, timestamp: Date.now() };
        try {
            localStorage.setItem(CACHE_KEY, JSON.stringify(entry));
        } catch {
            localStorage.removeItem(CACHE_KEY);
        }
    },

    isFresh(): boolean {
        const c = this.get();
        return !!c && Date.now() - c.timestamp < CACHE_TTL_MS;
    },

    isUsable(): boolean {
        const c = this.get();
        return !!c && c.articles.length > 0 && Date.now() - c.timestamp < STALE_TTL_MS;
    },

    latestId(): number | null {
        const c = this.get();
        if (!c || c.articles.length === 0) return null;
        return Math.max(...c.articles.map((a) => a.id));
    },

    appendPage(articles: Article[], nextCursor: number | null, hasMore: boolean) {
        const c = this.get();
        if (!c) return;
        const existingIds = new Set(c.articles.map((a) => a.id));
        const newOnes = articles.filter((a) => !existingIds.has(a.id));
        this.set({
            articles: [...c.articles, ...newOnes],
            trends: c.trends,
            nextCursor,
            hasMore,
        });
    },

    prependNew(articles: Article[]) {
        const c = this.get();
        if (!c) return;
        const existingIds = new Set(c.articles.map((a) => a.id));
        const newOnes = articles.filter((a) => !existingIds.has(a.id));
        if (newOnes.length === 0) return;
        this.set({
            articles: [...newOnes, ...c.articles],
            trends: c.trends,
            nextCursor: c.nextCursor,
            hasMore: c.hasMore,
        });
    },
};
