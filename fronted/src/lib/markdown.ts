import { marked } from 'marked';
import DOMPurify from 'isomorphic-dompurify';

/**
 * Parse markdown to HTML and sanitize it before it touches {@html}.
 * Article snippets/insights come from scraped, untrusted sources, so the
 * rendered HTML must be sanitized to prevent stored XSS. marked does not
 * sanitize on its own — DOMPurify is the maintained, recommended pairing.
 */
export function renderMarkdown(src: string | null | undefined): string {
	return DOMPurify.sanitize(marked.parse(src ?? '', { async: false }) as string);
}
