// frontend/src/lib/api.ts
const BASE_URL = 'http://127.0.0.1:8000';

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
}

export const api = {
    getTrends: async (): Promise<Trend[]> => {
        const res = await fetch(`${BASE_URL}/trends`);
        return res.json();
    },
    getArticles: async (keyword?: string): Promise<Article[]> => {
        const url = keyword ? `${BASE_URL}/articles?keyword=${keyword}` : `${BASE_URL}/articles`;
        const res = await fetch(url);
        return res.json();
    },
    triggerRefresh: async () => {
        await fetch(`${BASE_URL}/ingest`, { method: 'POST' });
        await fetch(`${BASE_URL}/analyze`, { method: 'POST' });
    }
};