import { marked } from 'marked';
import DOMPurify from 'isomorphic-dompurify';

/**
 * Parse markdown to HTML and sanitize it before it touches {@html}.
 * Article snippets/insights come from scraped, untrusted sources, so the
 * rendered HTML must be sanitized to prevent stored XSS. marked does not
 * sanitize on its own — DOMPurify is the maintained, recommended pairing.
 */
// Memoize by source string: chat/insight content re-renders often, and
// parse+sanitize is pure, so caching keeps the reader and chat list smooth.
const _cache = new Map<string, string>();

export function renderMarkdown(src: string | null | undefined): string {
	const key = src ?? '';
	const hit = _cache.get(key);
	if (hit !== undefined) return hit;
	const html = DOMPurify.sanitize(marked.parse(key, { async: false }) as string);
	if (_cache.size > 500) _cache.clear(); // simple bound
	_cache.set(key, html);
	return html;
}
