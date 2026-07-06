import { describe, it, expect } from 'vitest';
import { renderMarkdown } from './markdown';

describe('renderMarkdown', () => {
	it('renders basic markdown', () => {
		const html = renderMarkdown('**bold** and *italic*');
		expect(html).toContain('<strong>bold</strong>');
		expect(html).toContain('<em>italic</em>');
	});

	it('strips script tags (stored XSS from scraped sources)', () => {
		const html = renderMarkdown('hello <script>alert(1)</script> world');
		expect(html).not.toContain('<script');
		expect(html).toContain('hello');
	});

	it('strips event handler attributes', () => {
		const html = renderMarkdown('<img src="x" onerror="alert(1)">');
		expect(html).not.toContain('onerror');
	});

	it('strips javascript: urls in links', () => {
		const html = renderMarkdown('[click](javascript:alert(1))');
		expect(html).not.toContain('javascript:');
	});

	it('handles null and undefined', () => {
		expect(renderMarkdown(null)).toBe('');
		expect(renderMarkdown(undefined)).toBe('');
	});

	it('returns identical output from the memo cache', () => {
		const a = renderMarkdown('# Title');
		const b = renderMarkdown('# Title');
		expect(a).toBe(b);
		expect(a).toContain('Title');
	});
});
