const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

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

export const api = {
    getTrends: async (): Promise<Trend[]> => {
        const res = await fetch(`${BASE_URL}/trends`);
        return res.json();
    },

    getArticles: async (cursor?: number | null, limit = 40): Promise<ArticlesResponse> => {
        const params = new URLSearchParams({ limit: String(limit) });
        if (cursor) params.set('cursor', String(cursor));
        const res = await fetch(`${BASE_URL}/articles?${params}`);
        return res.json();
    },

    getArticleContent: async (id: number): Promise<{ content: string }> => {
        const res = await fetch(`${BASE_URL}/articles/${id}/content`);
        return res.json();
    },

    triggerRefresh: async () => {
        await fetch(`${BASE_URL}/ingest`, { method: 'POST' });
        await fetch(`${BASE_URL}/analyze`, { method: 'POST' });
    },

    trackView: async (id: number) => {
        await fetch(`${BASE_URL}/articles/${id}/view`, { method: 'POST' });
    },

    chatWithArticle: async (id: number, question: string): Promise<{ answer: string }> => {
        const res = await fetch(`${BASE_URL}/articles/${id}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        return res.json();
    },

    getBrief: async (id: number): Promise<{ title: string; brief: string }> => {
        const res = await fetch(`${BASE_URL}/brief/${id}`);
        return res.json();
    }
};
