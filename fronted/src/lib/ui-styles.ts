export type ThemeMode = 'dark' | 'light';

/** Standard text input — same border/bg/focus language everywhere */
export function inputClass(theme: ThemeMode) {
	return `h-10 rounded-md border px-3 text-[13px] outline-none transition-colors lg:h-9 ${
		theme === 'dark'
			? 'border-white/10 bg-white/[0.03] text-white placeholder:text-white/35 focus:border-white/50 focus:bg-white/[0.05]'
			: 'border-black/10 bg-white text-black placeholder:text-black/35 focus:border-black/60'
	}`;
}

/**
 * Square icon button — 40px touch target on mobile, 36px on desktop.
 * tone='muted' = slightly more prominent bg fill (for secondary actions).
 */
export function iconButtonClass(theme: ThemeMode, tone: 'default' | 'muted' = 'default') {
	const base = 'flex h-10 w-10 shrink-0 items-center justify-center rounded-md border transition-all sm:h-9 sm:w-9';
	if (tone === 'muted') {
		return `${base} ${
			theme === 'dark'
				? 'border-white/10 bg-white/[0.04] text-white/60 hover:bg-white/[0.08] hover:text-white'
				: 'border-black/10 bg-black/[0.03] text-black/60 hover:bg-black/[0.06] hover:text-black'
		}`;
	}
	return `${base} ${
		theme === 'dark'
			? 'border-white/10 text-white/50 hover:bg-white/[0.06] hover:text-white'
			: 'border-black/10 text-black/50 hover:bg-black/[0.04] hover:text-black'
	}`;
}

/** Small inline chip button in filter bars */
export function chipButtonClass(theme: ThemeMode, active = false) {
	if (active) {
		return theme === 'dark' ? 'rounded-sm bg-white text-black' : 'rounded-sm bg-black text-white';
	}
	return theme === 'dark'
		? 'rounded-sm text-white/45 hover:bg-white/[0.06] hover:text-white'
		: 'rounded-sm text-black/45 hover:bg-black/[0.05] hover:text-black';
}

/** Floating card / dock panel */
export function panelClass(theme: ThemeMode) {
	return `rounded-2xl border shadow-lg backdrop-blur-2xl ${
		theme === 'dark'
			? 'border-white/[0.09] bg-[#111]/95 shadow-[0_12px_40px_rgba(0,0,0,0.55)]'
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
	return `inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold transition-all lg:text-[11px] lg:px-3 lg:py-2 ${
		active
			? theme === 'dark'
				? 'border-white/[0.15] bg-white/[0.08] text-zinc-100'
				: 'border-zinc-400 bg-zinc-100 text-zinc-800'
			: theme === 'dark'
				? 'border-white/[0.08] bg-white/[0.03] text-zinc-300 hover:bg-white/[0.08]'
				: 'border-zinc-200 bg-zinc-50 text-zinc-700 hover:bg-zinc-100'
	}`;
}
