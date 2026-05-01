<script lang="ts">
	import { Search, Zap, LogOut, SlidersHorizontal } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';
	import { inputClass, iconButtonClass, quickActionClass } from '$lib/ui-styles';

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
</script>

<header class={`sticky top-0 z-20 min-w-0 overflow-hidden border-b backdrop-blur-xl ${dark ? 'border-white/[0.04] bg-[#0b0b0b]/90' : 'border-zinc-100 bg-white/90'}`}>
	<!-- top bar: logo (mobile) / title (desktop) + search + actions -->
	<div class="flex min-w-0 items-center gap-2 px-4 py-2.5 sm:gap-3 sm:px-5">
		<!-- Mobile brand mark -->
		<div class="flex items-center gap-2.5 lg:hidden">
			<div class={`flex h-7 w-7 items-center justify-center rounded-md ${dark ? 'bg-white' : 'bg-black'}`}>
				<Zap class={`h-3.5 w-3.5 ${dark ? 'fill-black text-black' : 'fill-white text-white'}`} />
			</div>
			<span class={`text-[13px] font-black uppercase tracking-[2px] italic ${dark ? 'text-white' : 'text-black'}`}>Axon</span>
		</div>

		<!-- Desktop title -->
		<div class="hidden items-baseline gap-2.5 lg:flex">
			<h2 class={`text-[15px] font-bold ${dark ? 'text-white' : 'text-zinc-900'}`}>{title}</h2>
			<span class={`text-[11px] font-medium tabular-nums ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{articleCount}</span>
		</div>

		<div class="ml-auto flex min-w-0 items-center gap-2">
			<!-- Search -->
			<label class="group relative min-w-0 flex-1 sm:flex-none">
				<Search class={`pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 transition-colors lg:left-3 lg:h-4 lg:w-4 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
				<input
					type="text"
					value={searchQuery}
					oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
					placeholder="Search..."
					class={`${inputClass(theme)} w-full pl-8 pr-3 sm:w-36 sm:focus:w-52 lg:w-44 lg:pl-9 lg:focus:w-64`}
				/>
			</label>

			<!-- Mobile: sign out -->
			<button
				type="button"
				onclick={() => authClient.signOut()}
				class={`${iconButtonClass(theme)} lg:hidden ${dark ? 'hover:text-red-400 hover:border-red-400/30' : 'hover:text-red-600 hover:border-red-300'}`}
				aria-label="Sign out"
			>
				<LogOut class="h-4 w-4 sm:h-3.5 sm:w-3.5" />
			</button>

			<!-- Mobile: open filter sheet -->
			{#if onOpenFilters}
				<button
					onclick={onOpenFilters}
					class={`${iconButtonClass(theme, 'muted')} lg:hidden`}
					aria-label="Open filters"
				>
					<SlidersHorizontal class="h-4 w-4 sm:h-3.5 sm:w-3.5" />
				</button>
			{/if}
		</div>
	</div>

	<!-- Mobile: title + filter badge row -->
	<div class="flex min-w-0 items-baseline gap-2.5 overflow-hidden px-4 pb-2 sm:px-5 lg:hidden">
		<h2 class={`min-w-0 truncate text-[14px] font-bold ${dark ? 'text-white' : 'text-zinc-900'}`}>{title}</h2>
		<span class={`text-[10px] font-medium tabular-nums ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{articleCount}</span>
		{#if hasActiveFilters}
			<span class={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${dark ? 'bg-white/[0.08] text-zinc-300' : 'bg-zinc-100 text-zinc-600'}`}>Filtered</span>
		{/if}
		{#if hasSemanticSearch}
			<span class={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${dark ? 'bg-violet-500/15 text-violet-300' : 'bg-violet-100 text-violet-700'}`}>Semantic</span>
		{/if}
	</div>


	<!-- Desktop: quick-actions bar -->
	<div class={`hidden items-center gap-1.5 border-t px-4 py-2 lg:flex ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
		{#if hasSemanticSearch}
			<span class={`inline-flex items-center rounded-full px-2 py-1 text-[10px] font-semibold ${dark ? 'bg-violet-500/15 text-violet-300' : 'bg-violet-100 text-violet-700'}`}>
				Semantic search active
			</span>
		{/if}

		
	</div>
</header>
