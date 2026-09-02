import { marked } from 'marked';
import sanitizeHtml from 'sanitize-html';

/**
 * Parse markdown to HTML and sanitize it before it touches {@html}.
 * Article snippets/insights come from scraped, untrusted sources, so the
 * rendered HTML must be sanitized to prevent stored XSS. marked does not
 * sanitize on its own.
 *
 * Uses sanitize-html (pure JS) instead of isomorphic-dompurify/jsdom —
 * jsdom pulls html-encoding-sniffer which `require()`s ESM-only
 * `@exodus/bytes` and crashes Vercel serverless with ERR_REQUIRE_ESM.
 */
// Memoize by source string: chat/insight content re-renders often, and
// parse+sanitize is pure, so caching keeps the reader and chat list smooth.
const _cache = new Map<string, string>();

const SANITIZE: sanitizeHtml.IOptions = {
	allowedTags: [...sanitizeHtml.defaults.allowedTags, 'img', 'h1', 'h2'],
	allowedAttributes: {
		...sanitizeHtml.defaults.allowedAttributes,
		img: ['src', 'alt', 'title'],
		a: ['href', 'name', 'target', 'rel'],
	},
	allowedSchemes: ['http', 'https', 'mailto'],
};

export function renderMarkdown(src: string | null | undefined): string {
	const key = src ?? '';
	const hit = _cache.get(key);
	if (hit !== undefined) return hit;
	const html = sanitizeHtml(marked.parse(key, { async: false }) as string, SANITIZE);
	if (_cache.size > 500) _cache.clear(); // simple bound
	_cache.set(key, html);
	return html;
}
