<script lang="ts">
	import { Search, X } from 'lucide-svelte';
	import { tick } from 'svelte';
	import { chipButtonClass, iconButtonClass, inputClass } from '$lib/ui-styles';
	import AxonMark from '$lib/components/ui/AxonMark.svelte';

	type FeedOrder = 'latest' | 'highest';

	type Props = {
		title: string;
		articleCount: number;
		searchQuery: string;
		syncIndicator: boolean;
		theme: 'dark' | 'light';
		onSearchChange: (value: string) => void;
		hasSemanticSearch?: boolean;
		feedOrder?: FeedOrder;
		showOrder?: boolean;
		onOrderChange?: (order: FeedOrder) => void;
	};

	let {
		title,
		articleCount,
		searchQuery,
		syncIndicator,
		theme,
		onSearchChange,
		hasSemanticSearch = false,
		feedOrder = 'latest',
		showOrder = false,
		onOrderChange = () => {}
	}: Props = $props();

	let dark = $derived(theme === 'dark');
	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');
	let searchOpen = $state(false);
	let searchInput = $state<HTMLInputElement | null>(null);
	let showSearch = $derived(searchOpen || searchQuery.trim().length > 0);

	async function toggleSearch() {
		if (showSearch && !searchQuery.trim()) {
			searchOpen = false;
			return;
		}
		searchOpen = true;
		await tick();
		searchInput?.focus();
	}

	function clearSearch() {
		onSearchChange('');
		searchOpen = false;
	}
</script>

<header class={`sticky top-0 z-20 min-w-0 border-b ${dark ? 'border-white/10 bg-[#0a0a0a]/95' : 'border-black/10 bg-[#fafafa]/95'}`}>
	<div class="flex h-14 min-w-0 items-center gap-3 px-4 sm:px-5">
		<div class="flex shrink-0 items-center gap-2.5 lg:hidden">
			<span class={`flex h-6 w-6 items-center justify-center ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}>
				<AxonMark class="h-4 w-4" />
			</span>
			<span class={`text-[12px] font-semibold uppercase tracking-[0.24em] ${dark ? 'text-white' : 'text-black'}`}>Axon</span>
		</div>

		<div class="hidden min-w-0 items-baseline gap-3 lg:flex">
			<h2 class={`truncate text-[15px] font-semibold tracking-tight ${dark ? 'text-white' : 'text-black'}`}>{title}</h2>
			<span class={`axon-label shrink-0 tabular-nums ${muted}`}>{articleCount} shown</span>
			{#if syncIndicator}
				<span class={`axon-label shrink-0 ${dark ? 'text-white/70' : 'text-black/70'}`}>Syncing</span>
			{/if}
			{#if hasSemanticSearch}
				<span class={`axon-label shrink-0 border px-1.5 py-0.5 ${dark ? 'border-white/20 text-white/70' : 'border-black/20 text-black/70'}`}>Semantic</span>
			{/if}
		</div>

		<div class="ml-auto flex shrink-0 items-center gap-2">
			{#if showOrder}
				<div class="flex items-center gap-0.5" role="group" aria-label="Feed order">
					<button
						type="button"
						class={`axon-label px-2 py-1 ${chipButtonClass(theme, feedOrder === 'latest')}`}
						aria-pressed={feedOrder === 'latest'}
						onclick={() => onOrderChange('latest')}
					>Latest</button>
					<button
						type="button"
						class={`axon-label px-2 py-1 ${chipButtonClass(theme, feedOrder === 'highest')}`}
						aria-pressed={feedOrder === 'highest'}
						onclick={() => onOrderChange('highest')}
					>Highest</button>
				</div>
			{/if}
			<button
				type="button"
				class={iconButtonClass(theme, searchQuery.trim() ? 'muted' : 'default')}
				aria-label="Search the feed"
				aria-expanded={showSearch}
				onclick={toggleSearch}
			>
				<Search class="h-4 w-4" />
			</button>
		</div>
	</div>

	{#if showSearch}
		<div class={`border-t px-4 py-2.5 sm:px-5 ${dark ? 'border-white/10' : 'border-black/10'}`}>
			<label class="relative block">
				<Search class={`pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 ${muted}`} />
				<input
					bind:this={searchInput}
					type="search"
					value={searchQuery}
					oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
					onkeydown={(event) => {
						if (event.key === 'Escape') clearSearch();
					}}
					placeholder="Search the feed"
					class={`${inputClass(theme)} w-full pl-8 pr-8 [&::-webkit-search-cancel-button]:hidden`}
				/>
				{#if searchQuery}
					<button
						type="button"
						onclick={clearSearch}
						class={`absolute right-1.5 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center ${muted} ${dark ? 'hover:text-white' : 'hover:text-black'}`}
						aria-label="Clear search"
					>
						<X class="h-3.5 w-3.5" />
					</button>
				{/if}
			</label>
		</div>
	{/if}
</header>
