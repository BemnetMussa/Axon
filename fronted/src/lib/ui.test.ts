import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { getBrandColor, stripHtml, relativeTime, readingTime, formatEngagement, categoryLabel, whyKept, dayLabel, formatDate, formatDateLong, hostname } from './ui';

describe('getBrandColor', () => {
	it('returns brand colors for known sources and a fallback otherwise', () => {
		expect(getBrandColor('HackerNews')).toBe('#FF6600');
		expect(getBrandColor('UnknownSource')).toBe('#3f3f46');
	});
});

describe('stripHtml', () => {
	it('removes tags and entities', () => {
		expect(stripHtml('<p>Hello&nbsp;<b>world</b></p>')).toBe('Hello world');
	});
	it('collapses whitespace', () => {
		expect(stripHtml('a\n\n   b')).toBe('a b');
	});
});

describe('relativeTime', () => {
	beforeEach(() => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date('2026-07-06T12:00:00Z'));
	});
	afterEach(() => {
		vi.useRealTimers();
	});

	it('handles empty input', () => {
		expect(relativeTime('')).toBe('');
	});

	it('labels sub-minute and future dates as Just now', () => {
		expect(relativeTime('2026-07-06T11:59:40Z')).toBe('Just now');
		expect(relativeTime('2026-07-06T13:00:00Z')).toBe('Just now');
	});

	it('formats minutes, hours, days, weeks', () => {
		expect(relativeTime('2026-07-06T11:30:00Z')).toBe('30m ago');
		expect(relativeTime('2026-07-06T07:00:00Z')).toBe('5h ago');
		expect(relativeTime('2026-07-05T09:00:00Z')).toBe('Yesterday');
		expect(relativeTime('2026-07-03T12:00:00Z')).toBe('3d ago');
		expect(relativeTime('2026-06-20T12:00:00Z')).toBe('2w ago');
	});

	it('treats naive timestamps (no timezone suffix) as UTC', () => {
		// Backend sends naive UTC datetimes; without the Z-append they would be
		// parsed as local time and drift by the machine's UTC offset.
		expect(relativeTime('2026-07-06T11:30:00')).toBe('30m ago');
	});
});

describe('readingTime', () => {
	it('returns empty for short or missing content', () => {
		expect(readingTime('')).toBe('');
		expect(readingTime('a few words only')).toBe('');
	});
	it('estimates at ~220 wpm with a 1 minute floor', () => {
		expect(readingTime(Array(100).fill('word').join(' '))).toBe('1 min read');
		expect(readingTime(Array(700).fill('word').join(' '))).toBe('3 min read');
	});
});

describe('formatEngagement', () => {
	it('hides non-positive values', () => {
		expect(formatEngagement(0)).toBe('');
		expect(formatEngagement(-5)).toBe('');
	});
	it('formats plain and thousand-scale counts', () => {
		expect(formatEngagement(42)).toBe('42');
		expect(formatEngagement(1500)).toBe('1.5k');
	});
});

describe('categoryLabel', () => {
	it('uses the tab words for backend categories', () => {
		expect(categoryLabel('Signal')).toBe('Research');
		expect(categoryLabel('Discovery')).toBe('Tools');
		expect(categoryLabel('AI')).toBe('AI');
	});
});

describe('whyKept', () => {
	it('names the traction unit per source', () => {
		expect(whyKept({ source: 'HackerNews', likes: 412 })).toBe('412 points');
		expect(whyKept({ source: 'GitHub', likes: 2100 })).toBe('2.1k stars');
	});
	it('falls back to source trust when there is no count', () => {
		expect(whyKept({ source: 'Anthropic', likes: 0 })).toBe('Primary source');
		expect(whyKept({ source: 'ArXiv', likes: 0 })).toBe('New paper');
		expect(whyKept({ source: 'TechCrunch', likes: 0 })).toBe('');
	});
});

describe('formatDate', () => {
	it('writes an unambiguous UTC date', () => {
		expect(formatDate('2026-10-06T12:00:00')).toBe('Oct 6, 2026');
		expect(formatDate('')).toBe('');
	});
});

describe('formatDateLong', () => {
	it('includes the UTC weekday', () => {
		expect(formatDateLong('2026-10-14T09:00:00')).toBe('Wednesday, October 14, 2026');
		expect(formatDateLong('')).toBe('');
	});
});

describe('hostname', () => {
	it('strips www and tolerates bad URLs', () => {
		expect(hostname('https://www.pola.rs/posts/2.0')).toBe('pola.rs');
		expect(hostname('not a url')).toBe('');
	});
});

describe('dayLabel', () => {
	const now = new Date('2026-07-06T12:00:00Z').getTime();
	it('labels by UTC day', () => {
		expect(dayLabel('2026-07-06T00:30:00', now)).toBe('Today');
		expect(dayLabel('2026-07-05T23:59:00Z', now)).toBe('Yesterday');
		expect(dayLabel('2026-07-03T09:00:00Z', now)).toBe('Fri, Jul 3');
	});
});
