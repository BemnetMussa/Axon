import { marked } from 'marked';

/**
 * Parse markdown to HTML and sanitize it before it touches {@html}.
 * Article snippets/insights come from scraped, untrusted sources, so the
 * rendered HTML must be sanitized to prevent stored XSS.
 *
 * Intentionally zero Node DOM deps. isomorphic-dompurify (jsdom) and
 * sanitize-html (htmlparser2 ESM) both crash Vercel serverless with
 * ERR_REQUIRE_ESM — so we strip the dangerous bits with a small filter.
 */
const _cache = new Map<string, string>();

/** Strip the XSS vectors that matter for scraped markdown → {@html}. */
export function sanitizeHtmlLite(html: string): string {
	return (
		html
			// comments can hide payloads in some parsers
			.replace(/<!--[\s\S]*?-->/g, '')
			// drop dangerous elements (open+close and void)
			.replace(/<\/?(?:script|iframe|object|embed|link|meta|base|form|svg|math)[\s\S]*?>/gi, '')
			// event handlers: onerror=, onclick=, …
			.replace(/\son[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '')
			// javascript: / vbscript: / data:text/html URLs
			.replace(
				/(\s(?:href|src|xlink:href)\s*=\s*)(["'])\s*(?:javascript|vbscript|data\s*:\s*text\s*\/\s*html)[^"']*\2/gi,
				'$1$2#$2',
			)
			.replace(
				/(\s(?:href|src|xlink:href)\s*=\s*)(?:javascript|vbscript|data\s*:\s*text\s*\/\s*html)[^\s>]*/gi,
				'$1"#"',
			)
	);
}

export function renderMarkdown(src: string | null | undefined): string {
	const key = src ?? '';
	const hit = _cache.get(key);
	if (hit !== undefined) return hit;
	const html = sanitizeHtmlLite(marked.parse(key, { async: false }) as string);
	if (_cache.size > 500) _cache.clear(); // simple bound
	_cache.set(key, html);
	return html;
}
