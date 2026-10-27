<script lang="ts">
	import { ArrowDownUp, Check, Clock, X } from 'lucide-svelte';
	import SignalLoader from '$lib/components/ui/SignalLoader.svelte';
	import { type Article } from '$lib/api';
	import type { NavItem } from '$lib/ui';
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import VirtualFeed from '$lib/components/feed/VirtualFeed.svelte';
	import FeedHeader from '$lib/components/feed/FeedHeader.svelte';
	import { chipButtonClass } from '$lib/ui-styles';

	type SortOption = 'date' | 'engagement' | 'views';
	type TimeFilter = 'all' | 'today' | 'week' | 'month';
	type PullStatus = 'idle' | 'pulling' | 'checking' | 'up-to-date' | 'new' | 'error';

	type Props = {
		title: string;
		articles: Article[];
		sources: string[];
		activeSource: string | null;
		searchQuery: string;
		sortBy: SortOption;
		timeFilter: TimeFilter;
		theme: 'dark' | 'light';
		hasMore: boolean;
		loadingMore: boolean;
		selectedArticleId: number | null;
		savedArticleIds: number[];
		readArticleIds: Set<number>;
		loading: boolean;
		syncIndicator: boolean;
		newArticleIds?: Set<number>;
		activeCategory: string | null;
		showSavedOnly: boolean;
		semanticSearchActive?: boolean;
		dbEmpty?: boolean;
		scrollArea?: HTMLDivElement;
		secondaryCategories?: NavItem[];
		onCategorySelect?: (id: string | null) => void;
		onSearchChange: (value: string) => void;
		onSourceSelect: (source: string | null) => void;
		onSortChange: (value: SortOption) => void;
		onTimeFilterChange: (value: TimeFilter) => void;
		onClearCategoryOrSaved: () => void;
		onClearAllFilters: () => void;
		onArticleOpen: (article: Article) => void;
		onArticleOpenWithChat: (article: Article, starterQuestion: string) => void;
		onToggleSave: (id: number) => void;
		onShowDigest: () => void;
		onLoadMore: () => void;
		onRefresh?: () => Promise<number>;
	};

	let {
		title, articles, sources, activeSource, searchQuery, sortBy, timeFilter, theme,
		hasMore, loadingMore, selectedArticleId, savedArticleIds, readArticleIds, loading,
		syncIndicator, newArticleIds = new Set(), scrollArea = $bindable(),
		activeCategory, showSavedOnly, semanticSearchActive = false, dbEmpty = false,
		secondaryCategories = [], onCategorySelect,
		onSearchChange, onSourceSelect, onSortChange, onTimeFilterChange,
		onClearCategoryOrSaved, onClearAllFilters, onArticleOpen, onArticleOpenWithChat, onToggleSave, onShowDigest, onLoadMore, onRefresh
	}: Props = $props();

	const sortOptions: { value: SortOption; label: string }[] = [
		{ value: 'date', label: 'Latest' },
		{ value: 'engagement', label: 'Top' },
		{ value: 'views', label: 'Most Read' },
	];

	const timeOptions: { value: TimeFilter; label: string }[] = [
		{ value: 'all', label: 'All' },
		{ value: 'today', label: 'Today' },
		{ value: 'week', label: 'Week' },
		{ value: 'month', label: 'Month' },
	];

	let dark = $derived(theme === 'dark');
	let pullStatus = $state<PullStatus>('idle');
	let newCount = $state(0);
	let showMobileFilters = $state(false);
	let touchStartY = 0;
	let pullDelta = 0;

	const PULL_THRESHOLD = 50;

	function dismissStatus() {
		setTimeout(() => { pullStatus = 'idle'; }, 2000);
	}

	function handleScroll(e: Event) {
		const el = e.target as HTMLDivElement;
		if (el.scrollTop + el.clientHeight >= el.scrollHeight - 200) {
			onLoadMore();
		}
	}

	function handleTouchStart(e: TouchEvent) {
		if (!scrollArea || scrollArea.scrollTop > 5 || pullStatus === 'checking') return;
		touchStartY = e.touches[0].clientY;
		pullDelta = 0;
	}

	function handleTouchMove(e: TouchEvent) {
		if (!scrollArea || scrollArea.scrollTop > 5 || pullStatus === 'checking') return;
		pullDelta = e.touches[0].clientY - touchStartY;
	}

	// A user refresh only READS the latest articles from the database — it never
	// triggers a scrape. Ingestion is owned by the backend scheduler. Pulling to
	// refresh re-fetches page 1 and reports the real outcome: how many new signals
	// arrived, "up to date" when there are none, or an error if the fetch failed.
	async function runRefresh() {
		pullStatus = 'checking';
		try {
			const count = onRefresh ? await onRefresh() : 0;
			newCount = count;
			pullStatus = count > 0 ? 'new' : 'up-to-date';
		} catch {
			pullStatus = 'error';
		}
		dismissStatus();
	}

	async function handleTouchEnd() {
		if (pullDelta >= PULL_THRESHOLD && pullStatus !== 'checking') {
			await runRefresh();
		}
		pullDelta = 0;
	}

	function handleWheel(e: WheelEvent) {
		if (!scrollArea || scrollArea.scrollTop > 0 || e.deltaY >= 0 || pullStatus !== 'idle') return;
		runRefresh();
	}

	function sourceBtnClass(active: boolean) {
		return chipButtonClass(theme, active);
	}

	let rule = $derived(dark ? 'border-white/10' : 'border-black/10');
	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');
	const chip = 'axon-label whitespace-nowrap px-2 py-1 transition-colors';

	function sortBtnClass(active: boolean) {
		return chipButtonClass(theme, active);
	}

	let activeFilterChips = $derived.by(() => {
		const chips: { key: string; label: string; clear: () => void }[] = [];
		if (showSavedOnly || activeCategory) {
			chips.push({
				key: 'mode',
				label: showSavedOnly ? 'Saved' : `Category: ${activeCategory}`,
				clear: onClearCategoryOrSaved
			});
		}
		if (activeSource) chips.push({ key: 'source', label: `Source: ${activeSource}`, clear: () => onSourceSelect(null) });
		if (timeFilter !== 'all') chips.push({ key: 'time', label: `Time: ${timeFilter}`, clear: () => onTimeFilterChange('all') });
		if (sortBy !== 'date') chips.push({ key: 'sort', label: `Sort: ${sortBy}`, clear: () => onSortChange('date') });
		if (searchQuery.trim()) chips.push({ key: 'search', label: `Search: ${searchQuery.trim()}`, clear: () => onSearchChange('') });
		return chips;
	});
</script>

<section class={`relative flex h-full min-h-0 min-w-0 flex-1 flex-col overflow-hidden ${dark ? 'bg-[#0a0a0a]' : 'bg-[#fafafa]'}`}>
	<FeedHeader
		{title}
		articleCount={articles.length}
		{searchQuery}
		{syncIndicator}
		{theme}
		onSearchChange={onSearchChange}
		onOpenFilters={() => (showMobileFilters = true)}
		hasActiveFilters={activeFilterChips.length > 0}
		hasSemanticSearch={semanticSearchActive}
	/>

	<!-- Desktop filter bar: sources on top, topic + time + sort below -->
	<div class={`hidden border-b px-5 py-2 lg:block ${rule}`}>
		<div class="no-scrollbar flex items-center gap-1 overflow-x-auto">
			<span class={`axon-label w-14 shrink-0 ${muted}`}>Source</span>
			<button onclick={() => onSourceSelect(null)} class={`${chip} ${sourceBtnClass(activeSource === null)}`}>All</button>
			{#each sources as source}
				<button onclick={() => onSourceSelect(source)} class={`${chip} ${sourceBtnClass(activeSource === source)}`}>{source}</button>
			{/each}
		</div>
	</div>

	<div class={`hidden items-center gap-4 border-b px-5 py-2 lg:flex ${rule}`}>
		{#if secondaryCategories.length > 0 && onCategorySelect}
			<div class="no-scrollbar flex min-w-0 items-center gap-1 overflow-x-auto">
				<span class={`axon-label w-14 shrink-0 ${muted}`}>Topic</span>
				<button onclick={() => onCategorySelect?.(null)} class={`${chip} ${sortBtnClass(activeCategory === null)}`}>All</button>
				{#each secondaryCategories as cat}
					<button onclick={() => onCategorySelect?.(cat.id)} class={`${chip} ${sortBtnClass(activeCategory === cat.id)}`}>{cat.label}</button>
				{/each}
			</div>
		{/if}
		<div class={`ml-auto flex shrink-0 items-center gap-1 border-l pl-4 ${rule}`}>
			<Clock class={`mr-1 h-3 w-3 ${muted}`} />
			{#each timeOptions as opt}
				<button onclick={() => onTimeFilterChange(opt.value)} class={`${chip} ${sortBtnClass(timeFilter === opt.value)}`}>{opt.label}</button>
			{/each}
		</div>
		<div class={`flex shrink-0 items-center gap-1 border-l pl-4 ${rule}`}>
			<ArrowDownUp class={`mr-1 h-3 w-3 ${muted}`} />
			{#each sortOptions as opt}
				<button onclick={() => onSortChange(opt.value)} class={`${chip} ${sortBtnClass(sortBy === opt.value)}`}>{opt.label}</button>
			{/each}
		</div>
	</div>

	<div class={`border-b px-3 py-2 lg:hidden ${rule} ${activeFilterChips.length === 0 ? 'hidden' : ''}`}>
		<div class="flex items-center justify-end gap-2">
			{#if activeFilterChips.length > 0}
				<button
					onclick={onClearAllFilters}
					class={`text-[10px] font-semibold uppercase tracking-wider ${dark ? 'text-zinc-500 hover:text-zinc-300' : 'text-zinc-500 hover:text-zinc-700'}`}
				>
					Clear all
				</button>
			{/if}
		</div>
		{#if activeFilterChips.length > 0}
			<div class="no-scrollbar mt-2 flex items-center gap-1.5 overflow-x-auto">
				{#each activeFilterChips as chip (chip.key)}
					<button
						onclick={chip.clear}
						class={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[10px] font-semibold ${dark ? 'border-white/[0.08] bg-white/[0.05] text-zinc-300' : 'border-zinc-200 bg-white text-zinc-700'}`}
					>
						{chip.label}
						<X class="h-3 w-3" />
					</button>
				{/each}
			</div>
		{/if}
	</div>

	{#if pullStatus !== 'idle' && pullStatus !== 'pulling'}
		<div class={`flex items-center justify-center gap-2 py-2 ${dark ? 'bg-white/[0.03]' : 'bg-zinc-50'}`}>
			{#if pullStatus === 'checking'}
				<SignalLoader size={14} class={dark ? 'text-zinc-500' : 'text-zinc-400'} />
				<span class={`text-[11px] font-semibold ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>Checking...</span>
			{:else if pullStatus === 'new'}
				<Check class={`h-3.5 w-3.5 ${dark ? 'text-white' : 'text-black'}`} />
				<span class={`axon-label ${dark ? 'text-white' : 'text-black'}`}>{newCount} new {newCount === 1 ? 'story' : 'stories'} kept</span>
			{:else if pullStatus === 'error'}
				<span class="text-[11px] font-semibold text-red-400">Couldn't refresh — check your connection</span>
			{:else}
				<Check class={`h-3.5 w-3.5 ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} />
				<span class={`text-[11px] font-semibold ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>You're up to date</span>
			{/if}
		</div>
	{/if}

	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		bind:this={scrollArea}
		class="no-scrollbar min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto pb-[calc(4.5rem+env(safe-area-inset-bottom,0px))] lg:pb-0"
		onscroll={handleScroll}
		ontouchstart={handleTouchStart}
		ontouchmove={handleTouchMove}
		ontouchend={handleTouchEnd}
		onwheel={handleWheel}
	>
		{#if loading && articles.length === 0}
			<div class="flex h-full flex-col gap-4 px-3.5 py-4 sm:px-4">
				{#each [1, 2, 3, 4, 5] as _}
					<div class={`h-36 w-full animate-pulse rounded-xl ${dark ? 'bg-white/5' : 'bg-black/5'}`}></div>
				{/each}
			</div>
		{:else if articles.length === 0}
			<div class="flex h-full items-center justify-center px-6 text-center">
				{#if dbEmpty}
					<!-- First-run: database has no articles yet -->
					<div class="max-w-xs">
						<div class={`mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl ${dark ? 'bg-white/[0.06]' : 'bg-zinc-100'}`}>
							<svg class={`h-6 w-6 ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.338-2.32 5.75 5.75 0 0 1 1.048 11.09" /></svg>
						</div>
						<p class={`text-[13px] font-bold ${dark ? 'text-zinc-200' : 'text-zinc-800'}`}>Your feed is empty</p>
						<p class="mt-1.5 text-[12px] leading-relaxed text-zinc-500">No signals have been fetched yet. The app will automatically fetch content in the background.</p>
					</div>
				{:else}
					<!-- Filtered to empty -->
					<div>
						<p class={`text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>No signals found</p>
						<p class="mt-2 text-[13px] text-zinc-500">Try broadening your filters or search.</p>
						<button
							type="button"
							onclick={onClearAllFilters}
							class={`mt-4 inline-flex rounded-lg px-3 py-1.5 text-[11px] font-semibold ${dark ? 'bg-white/[0.08] text-zinc-200 hover:bg-white/[0.12]' : 'bg-zinc-100 text-zinc-800 hover:bg-zinc-200'}`}
						>
							Clear all filters
						</button>
					</div>
				{/if}
			</div>
		{:else}
			<div class="w-full min-w-0 max-w-full overflow-hidden px-2.5 py-1 sm:px-4">
				<VirtualFeed items={articles} scrollEl={scrollArea}>
					{#snippet item(article)}
						<ArticleCard
							{article}
							selected={selectedArticleId === article.id}
							isSaved={savedArticleIds.includes(article.id)}
							isNew={newArticleIds.has(article.id)}
							isRead={readArticleIds.has(article.id)}
							{theme}
							onOpen={onArticleOpen}
							onOpenWithChat={onArticleOpenWithChat}
							onToggleSave={onToggleSave}
						/>
					{/snippet}
				</VirtualFeed>
			</div>
			{#if loadingMore}
				<div class="flex justify-center py-4">
					<SignalLoader size={16} class="text-zinc-500" />
				</div>
			{/if}
			{#if hasMore && !loadingMore}
				<div class="flex justify-center py-4">
					<button onclick={onLoadMore} class={`text-[11px] font-semibold transition-colors ${dark ? 'text-zinc-500 hover:text-zinc-300' : 'text-zinc-400 hover:text-zinc-600'}`}>Load more</button>
				</div>
			{/if}
			{#if !hasMore && !loadingMore && articles.length > 0}
				<div class="flex flex-col items-center gap-1 py-6">
					<Check class={`h-4 w-4 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
					<p class={`text-[11px] font-semibold ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>You're all caught up</p>
				</div>
			{/if}
		{/if}
	</div>

	{#if showMobileFilters}
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="fixed inset-0 z-[51] bg-black/55 lg:hidden" onclick={() => (showMobileFilters = false)}></div>
		<div
			class={`fixed inset-x-0 z-[52] max-h-[min(88vh,calc(100dvh-5rem))] overflow-y-auto rounded-t-3xl border px-4 pt-4 lg:hidden ${dark ? 'border-white/[0.06] bg-[#111214]' : 'border-zinc-200 bg-white'}`}
			style="bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)); padding-bottom: calc(1rem + env(safe-area-inset-bottom, 0px));"
		>
			<div class="mb-3 flex items-center justify-between">
				<p class={`text-sm font-bold ${dark ? 'text-zinc-100' : 'text-zinc-900'}`}>Feed filters</p>
				<button onclick={() => (showMobileFilters = false)} class={`${dark ? 'text-zinc-500' : 'text-zinc-400'}`} aria-label="Close filters">
					<X class="h-4 w-4" />
				</button>
			</div>

			{#if secondaryCategories.length > 0 && onCategorySelect}
				<p class={`mb-1 text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Topic</p>
				<div class="mb-3 flex flex-wrap gap-1.5">
					<button onclick={() => { onCategorySelect?.(null); showMobileFilters = false; }} class={`rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${sortBtnClass(activeCategory === null)}`}>All</button>
					{#each secondaryCategories as cat}
						<button onclick={() => { onCategorySelect?.(cat.id); showMobileFilters = false; }} class={`rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${sortBtnClass(activeCategory === cat.id)}`}>{cat.label}</button>
					{/each}
				</div>
			{/if}

			<p class={`mb-1 text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Source</p>
			<div class="no-scrollbar mb-3 flex items-center gap-1.5 overflow-x-auto">
				<button onclick={() => onSourceSelect(null)} class={`whitespace-nowrap rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${sourceBtnClass(activeSource === null)}`}>All</button>
				{#each sources as source}
					<button onclick={() => onSourceSelect(source)} class={`whitespace-nowrap rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${sourceBtnClass(activeSource === source)}`}>{source}</button>
				{/each}
			</div>

			<p class={`mb-1 text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Time</p>
			<div class="mb-3 flex flex-wrap gap-1.5">
				{#each timeOptions as opt}
					<button onclick={() => onTimeFilterChange(opt.value)} class={`rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${sortBtnClass(timeFilter === opt.value)}`}>{opt.label}</button>
				{/each}
			</div>

			<p class={`mb-1 text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Sort</p>
			<div class="mb-4 flex flex-wrap gap-1.5">
				{#each sortOptions as opt}
					<button onclick={() => onSortChange(opt.value)} class={`rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${sortBtnClass(sortBy === opt.value)}`}>{opt.label}</button>
				{/each}
			</div>

			<div class="flex items-center justify-between gap-2">
				<button
					onclick={onClearAllFilters}
					class={`rounded-xl border px-3 py-2 text-[11px] font-semibold ${dark ? 'border-white/[0.08] text-zinc-300' : 'border-zinc-200 text-zinc-700'}`}
				>
					Reset all
				</button>
				<button
					onclick={() => (showMobileFilters = false)}
					class={`rounded-xl px-3 py-2 text-[11px] font-semibold ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}
				>
					Done
				</button>
			</div>
		</div>
	{/if}
</section>
