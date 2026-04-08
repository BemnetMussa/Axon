<script lang="ts">
	import { RefreshCw, Search, Zap, Sun, Moon, LogOut, SlidersHorizontal, BellDot, Eraser } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';

	type Props = {
		title: string;
		articleCount: number;
		searchQuery: string;
		syncIndicator: boolean;
		theme: 'dark' | 'light';
		onSearchChange: (value: string) => void;
		onRefresh: () => void;
		onToggleTheme?: () => void;
		onOpenFilters?: () => void;
		hasActiveFilters?: boolean;
		hasNewSignals?: boolean;
		onCheckNew?: () => Promise<boolean>;
		onClearAllFilters?: () => void;
	};

	let {
		title, articleCount, searchQuery, syncIndicator, theme, onSearchChange, onRefresh, onToggleTheme,
		onOpenFilters, hasActiveFilters = false, hasNewSignals = false, onCheckNew, onClearAllFilters
	}: Props = $props();
	let dark = $derived(theme === 'dark');
	let checkingNew = $state(false);

	async function checkNewNow() {
		if (!onCheckNew || checkingNew) return;
		checkingNew = true;
		try {
			await onCheckNew();
		} finally {
			checkingNew = false;
		}
	}
</script>

<header class={`sticky top-0 z-20 min-w-0 overflow-hidden border-b backdrop-blur-xl ${dark ? 'border-white/[0.04] bg-[#0b0b0b]/90' : 'border-zinc-100 bg-white/90'}`}>
	<div class="flex min-w-0 items-center gap-3 px-4 py-3 sm:px-5">
		<div class="flex items-center gap-2.5 lg:hidden">
			<div class={`flex h-7 w-7 items-center justify-center rounded-md ${dark ? 'bg-white' : 'bg-black'}`}>
				<Zap class={`h-3.5 w-3.5 ${dark ? 'fill-black text-black' : 'fill-white text-white'}`} />
			</div>
			<span class={`text-[13px] font-black uppercase tracking-[2px] italic ${dark ? 'text-white' : 'text-black'}`}>Axon</span>
		</div>

		<div class="hidden items-baseline gap-2.5 lg:flex">
			<h2 class={`text-[14px] font-bold ${dark ? 'text-white' : 'text-zinc-900'}`}>{title}</h2>
			<span class={`text-[10px] font-medium tabular-nums ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{articleCount}</span>
		</div>

		<div class="ml-auto flex min-w-0 items-center gap-1.5 sm:gap-2">
			<label class="group relative min-w-0 flex-1 sm:flex-none">
				<Search class={`pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 transition-colors ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
				<input
					type="text"
					value={searchQuery}
					oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
					placeholder="Search..."
					class={`h-8 w-full rounded-md border pl-8 pr-3 text-[12px] outline-none transition-all sm:w-40 sm:focus:w-56 lg:w-44 lg:focus:w-64 ${dark ? 'border-white/[0.06] bg-white/[0.03] text-white placeholder:text-zinc-600 focus:border-white/15' : 'border-zinc-200 bg-zinc-50 text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-400'}`}
				/>
			</label>
			{#if onToggleTheme}
				<button
					onclick={onToggleTheme}
					class={`hidden lg:flex h-8 w-8 shrink-0 items-center justify-center rounded-md border transition-all ${dark ? 'border-white/[0.06] bg-white/[0.03] text-zinc-400 hover:text-white' : 'border-zinc-200 bg-zinc-50 text-zinc-500 hover:text-zinc-900'}`}
					aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
				>
					{#if dark}
						<Sun class="h-3.5 w-3.5" />
					{:else}
						<Moon class="h-3.5 w-3.5" />
					{/if}
				</button>
			{/if}
			<button
				type="button"
				onclick={() => authClient.signOut()}
				class={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md border transition-all lg:hidden ${dark ? 'border-white/[0.06] text-zinc-500 hover:text-red-400' : 'border-zinc-200 text-zinc-500 hover:text-red-600'}`}
				aria-label="Sign out"
			>
				<LogOut class="h-3.5 w-3.5" />
			</button>
			{#if onOpenFilters}
				<button
					onclick={onOpenFilters}
					class={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md border transition-all lg:hidden ${dark ? 'border-white/[0.06] bg-white/[0.03] text-zinc-300' : 'border-zinc-200 bg-zinc-50 text-zinc-600'}`}
					aria-label="Open filters"
				>
					<SlidersHorizontal class="h-3.5 w-3.5" />
				</button>
			{/if}
		</div>
	</div>

	<div class="flex min-w-0 items-baseline gap-2.5 overflow-hidden px-4 pb-2.5 sm:px-5 lg:hidden">
		<h2 class={`min-w-0 truncate text-[14px] font-bold ${dark ? 'text-white' : 'text-zinc-900'}`}>{title}</h2>
		<span class={`text-[10px] font-medium tabular-nums ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{articleCount}</span>
		{#if hasActiveFilters}
			<span class={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${dark ? 'bg-white/[0.08] text-zinc-300' : 'bg-zinc-100 text-zinc-600'}`}>Filtered</span>
		{/if}
	</div>

	<div class={`hidden items-center gap-1.5 border-t px-4 py-2 lg:flex ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
		<button
			type="button"
			onclick={onRefresh}
			class={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold ${dark ? 'border-white/[0.08] bg-white/[0.03] text-zinc-300 hover:bg-white/[0.08]' : 'border-zinc-200 bg-zinc-50 text-zinc-700 hover:bg-zinc-100'}`}
		>
			<RefreshCw class={`h-3 w-3 ${syncIndicator ? 'animate-spin' : ''}`} />
			Refresh
		</button>
		<button
			type="button"
			onclick={checkNewNow}
			disabled={checkingNew || !onCheckNew}
			class={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold disabled:opacity-60 ${dark ? 'border-white/[0.08] bg-white/[0.03] text-zinc-300 hover:bg-white/[0.08]' : 'border-zinc-200 bg-zinc-50 text-zinc-700 hover:bg-zinc-100'}`}
		>
			<BellDot class={`h-3 w-3 ${hasNewSignals ? 'text-emerald-500' : ''}`} />
			{hasNewSignals ? 'New available' : 'Check new'}
		</button>
		<button
			type="button"
			onclick={onClearAllFilters}
			disabled={!hasActiveFilters || !onClearAllFilters}
			class={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold disabled:opacity-50 ${dark ? 'border-white/[0.08] bg-white/[0.03] text-zinc-300 hover:bg-white/[0.08]' : 'border-zinc-200 bg-zinc-50 text-zinc-700 hover:bg-zinc-100'}`}
		>
			<Eraser class="h-3 w-3" />
			Clear filters
		</button>
	</div>
</header>
