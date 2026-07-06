import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { getBrandColor, stripHtml, relativeTime, readingTime, formatEngagement } from './ui';

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
		expect(relativeTime('2026-07-06T11:30:00Z')).toBe('30 min');
		expect(relativeTime('2026-07-06T07:00:00Z')).toBe('5h ago');
		expect(relativeTime('2026-07-05T09:00:00Z')).toBe('Yesterday');
		expect(relativeTime('2026-07-03T12:00:00Z')).toBe('3d ago');
		expect(relativeTime('2026-06-20T12:00:00Z')).toBe('2w ago');
	});

	it('treats naive timestamps (no timezone suffix) as UTC', () => {
		// Backend sends naive UTC datetimes; without the Z-append they would be
		// parsed as local time and drift by the machine's UTC offset.
		expect(relativeTime('2026-07-06T11:30:00')).toBe('30 min');
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
