<script lang="ts">
	import { Search, Zap, LogOut, SlidersHorizontal } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';
	import { inputClass, iconButtonClass } from '$lib/ui-styles';
	import { pulseStore } from '$lib/pulse-store.svelte';
	import { sweepAgo, pulseWindow, formatCount } from '$lib/pulse';

	type Props = {
		title: string;
		articleCount: number;
		searchQuery: string;
		syncIndicator: boolean;
		theme: 'dark' | 'light';
		onSearchChange: (value: string) => void;
		onOpenFilters?: () => void;
		hasActiveFilters?: boolean;
		hasSemanticSearch?: boolean;
	};

	let {
		title, articleCount, searchQuery, syncIndicator, theme, onSearchChange,
		onOpenFilters, hasActiveFilters = false, hasSemanticSearch = false
	}: Props = $props();

	let dark = $derived(theme === 'dark');
	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');
	let win = $derived(pulseWindow(pulseStore.value));
	let lastAgo = $derived(sweepAgo(pulseStore.value?.last_sweep_at, pulseStore.now));
</script>

<header class={`sticky top-0 z-20 min-w-0 overflow-hidden border-b ${dark ? 'border-white/10 bg-[#0a0a0a]/95' : 'border-black/10 bg-[#fafafa]/95'}`}>
	<div class="flex h-14 min-w-0 items-center gap-2 px-4 sm:gap-3 sm:px-5">
		<!-- Mobile brand mark -->
		<div class="flex items-center gap-2.5 lg:hidden">
			<span class={`flex h-6 w-6 items-center justify-center ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}>
				<Zap class="h-3 w-3 fill-current" />
			</span>
			<span class={`text-[12px] font-semibold uppercase tracking-[0.24em] ${dark ? 'text-white' : 'text-black'}`}>Axon</span>
		</div>

		<!-- Desktop title -->
		<div class="hidden min-w-0 items-baseline gap-3 lg:flex">
			<h2 class={`text-[15px] font-semibold tracking-tight ${dark ? 'text-white' : 'text-black'}`}>{title}</h2>
			<span class={`axon-label tabular-nums ${muted}`}>{articleCount} shown</span>
			{#if syncIndicator}
				<span class={`axon-label flex items-center gap-2 ${dark ? 'text-white/70' : 'text-black/70'}`}>
					<span class="axon-live"></span>Syncing
				</span>
			{/if}
			{#if hasSemanticSearch}
				<span class={`axon-label border px-1.5 py-0.5 ${dark ? 'border-white/20 text-white/70' : 'border-black/20 text-black/70'}`}>Semantic</span>
			{/if}
		</div>

		<div class="ml-auto flex min-w-0 items-center gap-2">
			<label class="group relative min-w-0 flex-1 sm:flex-none">
				<Search class={`pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 lg:left-3 ${muted}`} />
				<input
					type="text"
					value={searchQuery}
					oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
					placeholder="Search the feed"
					class={`${inputClass(theme)} w-full pl-8 pr-3 sm:w-40 sm:focus:w-52 lg:w-48 lg:pl-9 lg:focus:w-64`}
				/>
			</label>

			<button
				type="button"
				onclick={() => authClient.signOut()}
				class={`${iconButtonClass(theme)} lg:hidden ${dark ? 'hover:text-red-400' : 'hover:text-red-600'}`}
				aria-label="Sign out"
			>
				<LogOut class="h-4 w-4 sm:h-3.5 sm:w-3.5" />
			</button>

			{#if onOpenFilters}
				<button onclick={onOpenFilters} class={`${iconButtonClass(theme, 'muted')} lg:hidden`} aria-label="Open filters">
					<SlidersHorizontal class="h-4 w-4 sm:h-3.5 sm:w-3.5" />
				</button>
			{/if}
		</div>
	</div>

	<!-- Mobile: title + filter readout -->
	<div class="flex min-w-0 items-center gap-3 overflow-hidden px-4 pb-2.5 sm:px-5 lg:hidden">
		<h2 class={`min-w-0 truncate text-[14px] font-semibold ${dark ? 'text-white' : 'text-black'}`}>{title}</h2>
		{#if hasActiveFilters}
			<span class={`axon-label border px-1.5 py-0.5 ${dark ? 'border-white/20 text-white/70' : 'border-black/20 text-black/70'}`}>Filtered</span>
		{/if}
		{#if hasSemanticSearch}
			<span class={`axon-label border px-1.5 py-0.5 ${dark ? 'border-white/20 text-white/70' : 'border-black/20 text-black/70'}`}>Semantic</span>
		{/if}
		<span class={`axon-label ml-auto flex shrink-0 items-center gap-2 tabular-nums ${muted}`}>
			<span class={`axon-live ${dark ? 'text-white' : 'text-black'} ${syncIndicator ? '' : 'opacity-70'}`}></span>
			{#if win}
				{formatCount(win.kept)}/{formatCount(win.scanned)} kept · {lastAgo}
			{:else}
				Live
			{/if}
		</span>
	</div>
</header>
