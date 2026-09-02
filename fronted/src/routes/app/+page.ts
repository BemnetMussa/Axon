import type { PageLoad } from './$types';

// Feed is client-fetched in onMount. Skipping SSR avoids shipping a heavy
// render path through Vercel serverless for a page that hydrates immediately.
export const ssr = false;

export const load: PageLoad = async () => ({});
