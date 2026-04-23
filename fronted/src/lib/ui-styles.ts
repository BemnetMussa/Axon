export type ThemeMode = 'dark' | 'light';

export function inputClass(theme: ThemeMode) {
	return `h-8 rounded-md border px-2.5 text-[12px] outline-none transition-colors ${
		theme === 'dark'
			? 'border-white/[0.06] bg-white/[0.03] text-white placeholder:text-zinc-600 focus:border-white/15'
			: 'border-zinc-200 bg-zinc-50 text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400'
	}`;
}

export function iconButtonClass(theme: ThemeMode, tone: 'default' | 'muted' = 'default') {
	if (tone === 'muted') {
		return `flex h-8 w-8 shrink-0 items-center justify-center rounded-md border transition-all ${
			theme === 'dark'
				? 'border-white/[0.06] bg-white/[0.03] text-zinc-400 hover:text-zinc-200'
				: 'border-zinc-200 bg-zinc-50 text-zinc-500 hover:text-zinc-900'
		}`;
	}
	return `flex h-8 w-8 shrink-0 items-center justify-center rounded-md border transition-all ${
		theme === 'dark'
			? 'border-white/[0.06] text-zinc-500 hover:bg-white/[0.06] hover:text-zinc-300'
			: 'border-zinc-200 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700'
	}`;
}

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

export function panelClass(theme: ThemeMode) {
	return `rounded-xl border shadow-lg backdrop-blur-2xl ${
		theme === 'dark'
			? 'border-white/[0.08] bg-[#111]/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)]'
			: 'border-zinc-200 bg-white/95 shadow-[0_4px_24px_rgba(0,0,0,0.08)]'
	}`;
}
