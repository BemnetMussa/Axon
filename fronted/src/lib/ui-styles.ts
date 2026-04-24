export type ThemeMode = 'dark' | 'light';

/** Standard text input — same border/bg/focus language everywhere */
export function inputClass(theme: ThemeMode) {
	return `h-9 rounded-lg border px-3 text-[13px] outline-none transition-colors ${
		theme === 'dark'
			? 'border-white/[0.06] bg-white/[0.03] text-white placeholder:text-zinc-600 focus:border-white/15'
			: 'border-zinc-200 bg-zinc-50 text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400'
	}`;
}

/**
 * Square icon button — 40px touch target on mobile, 32px on desktop.
 * tone='muted' = slightly more prominent bg fill (for secondary actions).
 */
export function iconButtonClass(theme: ThemeMode, tone: 'default' | 'muted' = 'default') {
	const base = 'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border transition-all sm:h-8 sm:w-8 sm:rounded-md';
	if (tone === 'muted') {
		return `${base} ${
			theme === 'dark'
				? 'border-white/[0.06] bg-white/[0.03] text-zinc-400 hover:bg-white/[0.07] hover:text-zinc-200'
				: 'border-zinc-200 bg-zinc-50 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700'
		}`;
	}
	return `${base} ${
		theme === 'dark'
			? 'border-white/[0.06] text-zinc-500 hover:bg-white/[0.06] hover:text-zinc-300'
			: 'border-zinc-200 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700'
	}`;
}

/** Small inline pill/chip button in filter bars */
export function chipButtonClass(theme: ThemeMode, active = false) {
	if (active) {
		return theme === 'dark'
			? 'rounded-md bg-white/[0.08] text-zinc-200'
			: 'rounded-md bg-zinc-100 text-zinc-800';
	}
	return theme === 'dark'
		? 'rounded-md text-zinc-600 hover:text-zinc-400'
		: 'rounded-md text-zinc-400 hover:text-zinc-600';
}

/** Floating card / dock panel */
export function panelClass(theme: ThemeMode) {
	return `rounded-xl border shadow-lg backdrop-blur-2xl ${
		theme === 'dark'
			? 'border-white/[0.08] bg-[#111]/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)]'
			: 'border-zinc-200 bg-white/95 shadow-[0_4px_24px_rgba(0,0,0,0.08)]'
	}`;
}

/** Full-width primary CTA button (inside a view, e.g. digest page) */
export function primaryBtnClass(theme: ThemeMode) {
	return `inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-[13px] font-bold shadow-md transition-all disabled:opacity-60 ${
		theme === 'dark'
			? 'bg-white text-black hover:bg-zinc-200'
			: 'bg-zinc-900 text-white hover:bg-zinc-700'
	}`;
}

/** Ghost/secondary button in the quick-actions bar */
export function quickActionClass(theme: ThemeMode, active = false) {
	return `inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold transition-all ${
		active
			? theme === 'dark'
				? 'border-white/[0.15] bg-white/[0.08] text-zinc-100'
				: 'border-zinc-400 bg-zinc-100 text-zinc-800'
			: theme === 'dark'
				? 'border-white/[0.08] bg-white/[0.03] text-zinc-300 hover:bg-white/[0.08]'
				: 'border-zinc-200 bg-zinc-50 text-zinc-700 hover:bg-zinc-100'
	}`;
}
