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

/** Aggregate filter activity from `/pulse` — what was scanned vs. kept. */
export interface Pulse {
    last_sweep_at: string | null;
    last_scanned: number;
    last_kept: number;
    scanned_24h: number;
    kept_24h: number;
    sweeps_24h: number;
    sources: number;
    interval_hours: number;
    next_sweep_at: string | null;
}

export interface ArticlesResponse {
    articles: Article[];
    next_cursor: string | null;
    has_more: boolean;
}

// --- Admin dashboard ----------------------------------------------------------
export interface SchedulerSnapshot {
    ap_scheduler_running: boolean;
    interval_hours: number;
    job_registered: boolean;
    next_run_at_utc: string | null;
}

export interface LastIngestSnapshot {
    at_utc: string | null;
    ok: boolean | null;
    detail: string | null;
    relative: string | null;
}

export interface SourceStat {
    source: string;
    total: number;
    last_24h: number;
    last_7d: number;
    missing_insight: number;
    latest_published: string | null;
    hours_since_latest: number | null;
}

export interface AiStatus {
    key_present: boolean;
    reachable: boolean;
    error: string | null;
}

export interface ProcessingState {
    running: boolean;
    phase: 'analyze' | 'retry' | 'done' | null;
    done: number;
    total: number;
    started_at: string | null;
    finished_at: string | null;
    result: string | null;
}

export interface FetchReport {
    at: string | null;
    raw: number;
    ingested: number;
    sources: Record<string, { raw: number; ingested: number }>;
}

export interface IngestRunRow {
    id: number;
    started_at: string | null;
    finished_at: string | null;
    trigger: string;
    ok: boolean;
    new_articles: number;
    analyzed: number;
    raw_found: number;
    detail: string | null;
}

export interface AdminStats {
    generated_at: string;
    scheduler: SchedulerSnapshot;
    last_scheduled_ingest: LastIngestSnapshot;
    ai: AiStatus;
    ai_last_error: string | null;
    processing: ProcessingState;
    fetch_report: FetchReport;
    recent_runs: IngestRunRow[];
    totals: {
        articles: number;
        processed: number;
        unprocessed: number;
        missing_insight: number;
        trends: number;
        digests: number;
        feedback: number;
        saved: number;
    };
    sources: SourceStat[];
    daily_volume: { day: string; count: number }[];
    engagement: {
        total_views: number;
        total_saves: number;
        source_score_sum: number;
        feedback_count: number;
        avg_feedback_rating: number | null;
        recent_feedback: { user: string | null; rating: number; comment: string | null; created_at: string | null }[];
    };
}

const PAGE_SIZE = 10;

export const api = {
    getTrends: async (): Promise<Trend[]> => {
        const res = await fetch(`${BASE_URL}/trends`);
        return jsonOrThrow<Trend[]>(res);
    },

    getArticles: async (
        cursor?: string | null,
        limit = PAGE_SIZE,
        filter?: { category?: string | null; source?: string | null }
    ): Promise<ArticlesResponse> => {
        const params = new URLSearchParams({ limit: String(limit) });
        if (cursor) params.set('cursor', cursor);
        // Scope the feed to a single tab. The backend paginates within the filter,
        // so the cursor returned here is the next page *of this tab*.
        if (filter?.category) params.set('category', filter.category);
        if (filter?.source) params.set('source', filter.source);
        // no-store: never let the browser/HTTP cache answer the feed — always fresh.
        const res = await fetch(`${BASE_URL}/articles?${params}`, { cache: 'no-store' });
        return jsonOrThrow<ArticlesResponse>(res);
    },

    getTrending: async (): Promise<{ articles: Article[] }> => {
        const res = await fetch(`${BASE_URL}/articles/trending`);
        return jsonOrThrow<{ articles: Article[] }>(res);
    },

    getSavedArticles: async (): Promise<{ articles: Article[] }> => {
        const res = await fetch(`${BASE_URL}/saved`);
        return jsonOrThrow<{ articles: Article[] }>(res);
    },

    toggleSave: async (id: number): Promise<{ status: string }> => {
        const res = await fetch(`${BASE_URL}/articles/${id}/save`, { method: 'POST' });
        return jsonOrThrow<{ status: string }>(res);
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
        const data = await jsonOrThrow<{ status?: string; new_articles?: number }>(await fetch(url, { method: 'POST' }));
        // Fire analysis in the background — never blocks the UI or causes a visible error
        fetch(`${BASE_URL}/analyze`, { method: 'POST' }).catch(() => {});
        return data;
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
    },
    
    submitFeedback: async (rating: number, comment?: string): Promise<{ status: string }> => {
        const res = await fetch(`${BASE_URL}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rating, comment })
        });
        return jsonOrThrow<{ status: string }>(res);
    },

    getPulse: async (): Promise<Pulse> => {
        const res = await fetch(`${BASE_URL}/pulse`, { cache: 'no-store' });
        return jsonOrThrow<Pulse>(res);
    },

    getHealth: async (): Promise<any> => {
        const res = await fetch(`${BASE_URL}/health`);
        return res.json();
    },

    // --- Admin dashboard ---
    getAdminStats: async (): Promise<AdminStats> => {
        const res = await fetch(`${BASE_URL}/admin/stats`, { cache: 'no-store' });
        return jsonOrThrow<AdminStats>(res);
    },

    adminRunIngest: async (force = true): Promise<{ status?: string; reason?: string; new_articles?: number }> => {
        const res = await fetch(`${BASE_URL}/ingest?force=${force}`, { method: 'POST' });
        return jsonOrThrow(res);
    },

    adminRunAnalyze: async (): Promise<{ status?: string; processed?: number }> => {
        const res = await fetch(`${BASE_URL}/analyze`, { method: 'POST' });
        return jsonOrThrow(res);
    },

    adminRetryInsights: async (): Promise<{ status?: string; retried?: number }> => {
        const res = await fetch(`${BASE_URL}/retry-insights`, { method: 'POST' });
        return jsonOrThrow(res);
    },

    // Background drain of the unprocessed + failed-insight backlog. Returns
    // immediately; progress shows up in getAdminStats().processing.
    adminProcessBacklog: async (): Promise<{ status: string }> => {
        const res = await fetch(`${BASE_URL}/admin/process`, { method: 'POST' });
        return jsonOrThrow(res);
    }
};


// ---------------------------------------------------------------------------
// localStorage cache with TTL
// ---------------------------------------------------------------------------

// v2: keyset cursor is now an opaque string (was a numeric id). Bumping the key
// discards stale v1 caches so returning users don't carry a numeric cursor.
const CACHE_KEY = 'axon_feed_cache_v2';
const CACHE_TTL_MS = 3 * 60 * 1000; // 3 minutes = "fresh"
const STALE_TTL_MS = 30 * 60 * 1000; // 30 minutes = still usable as stale

interface FeedCache {
    articles: Article[];
    trends: Trend[];
    nextCursor: string | null;
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

    appendPage(articles: Article[], nextCursor: string | null, hasMore: boolean) {
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
