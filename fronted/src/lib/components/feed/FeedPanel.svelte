<script lang="ts">
	import { ArrowDownUp, Loader2, Check, Clock } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import FeedHeader from '$lib/components/feed/FeedHeader.svelte';

	type SortOption = 'date' | 'engagement' | 'views';
	type TimeFilter = 'all' | 'today' | 'week' | 'month';
	type PullStatus = 'idle' | 'pulling' | 'checking' | 'up-to-date';

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
		scrollArea?: HTMLDivElement;
		onSearchChange: (value: string) => void;
		onSourceSelect: (source: string | null) => void;
		onSortChange: (value: SortOption) => void;
		onTimeFilterChange: (value: TimeFilter) => void;
		onArticleOpen: (article: Article) => void;
		onToggleSave: (id: number) => void;
		onRefresh: () => void;
		onLoadMore: () => void;
		onCheckNew?: () => Promise<boolean>;
		onToggleTheme?: () => void;
	};

	let {
		title, articles, sources, activeSource, searchQuery, sortBy, timeFilter, theme,
		hasMore, loadingMore, selectedArticleId, savedArticleIds, readArticleIds, loading,
		syncIndicator, newArticleIds = new Set(), scrollArea = $bindable(),
		onSearchChange, onSourceSelect, onSortChange, onTimeFilterChange,
		onArticleOpen, onToggleSave, onRefresh, onLoadMore, onCheckNew, onToggleTheme
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

	async function handleTouchEnd() {
		if (pullDelta >= PULL_THRESHOLD && pullStatus !== 'checking' && onCheckNew) {
			pullStatus = 'checking';
			const hadNew = await onCheckNew();
			pullStatus = hadNew ? 'idle' : 'up-to-date';
			if (!hadNew) dismissStatus();
		}
		pullDelta = 0;
	}

	function handleWheel(e: WheelEvent) {
		if (!scrollArea || scrollArea.scrollTop > 0 || e.deltaY >= 0 || pullStatus !== 'idle') return;
		if (!onCheckNew) return;
		pullStatus = 'checking';
		onCheckNew().then((hadNew) => {
			pullStatus = hadNew ? 'idle' : 'up-to-date';
			if (!hadNew) dismissStatus();
		});
	}

	function sourceBtnClass(active: boolean) {
		if (active && dark) return 'bg-white text-black';
		if (active && !dark) return 'bg-black text-white';
		return dark ? 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300' : 'text-zinc-500 hover:bg-zinc-50 hover:text-zinc-700';
	}

	function sortBtnClass(active: boolean) {
		if (active && dark) return 'bg-white/[0.08] text-zinc-200';
		if (active && !dark) return 'bg-zinc-100 text-zinc-800';
		return dark ? 'text-zinc-600 hover:text-zinc-400' : 'text-zinc-400 hover:text-zinc-600';
	}
</script>

<section class={`relative flex h-full min-h-0 min-w-0 flex-1 flex-col overflow-hidden ${dark ? 'bg-[#0b0b0b]' : 'bg-white'}`}>
	<FeedHeader {title} articleCount={articles.length} {searchQuery} {syncIndicator} {theme} onSearchChange={onSearchChange} onRefresh={onRefresh} {onToggleTheme} />

	<div class={`border-b px-3 py-1.5 sm:px-5 sm:py-2 ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
		<div class="no-scrollbar flex items-center gap-1 overflow-x-auto sm:gap-1.5">
			<button
				onclick={() => onSourceSelect(null)}
				class={`whitespace-nowrap rounded-md px-2 py-1 text-[9px] font-bold uppercase tracking-wider transition-all sm:px-2.5 sm:py-1.5 sm:text-[10px] ${sourceBtnClass(activeSource === null)}`}
			>All</button>
			{#each sources as source}
				<button
					onclick={() => onSourceSelect(source)}
					class={`whitespace-nowrap rounded-md px-2 py-1 text-[9px] font-bold uppercase tracking-wider transition-all sm:px-2.5 sm:py-1.5 sm:text-[10px] ${sourceBtnClass(activeSource === source)}`}
				>{source}</button>
			{/each}
		</div>
	</div>

	<div class={`flex items-center gap-1 border-b px-3 py-1.5 sm:gap-2 sm:px-5 sm:py-2 ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
		<div class="flex items-center gap-0.5 sm:gap-1">
			<Clock class={`h-3 w-3 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
			{#each timeOptions as opt}
				<button
					onclick={() => onTimeFilterChange(opt.value)}
					class={`whitespace-nowrap rounded-md px-1.5 py-1 text-[9px] font-semibold transition-all sm:px-2 sm:text-[10px] ${sortBtnClass(timeFilter === opt.value)}`}
				>{opt.label}</button>
			{/each}
		</div>
		<div class={`ml-auto flex items-center gap-0.5 border-l pl-2 sm:gap-1 sm:pl-3 ${dark ? 'border-white/[0.04]' : 'border-zinc-200'}`}>
			<ArrowDownUp class={`h-3 w-3 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
			{#each sortOptions as opt}
				<button
					onclick={() => onSortChange(opt.value)}
					class={`whitespace-nowrap rounded-md px-1.5 py-1 text-[9px] font-semibold transition-all sm:px-2 sm:text-[10px] ${sortBtnClass(sortBy === opt.value)}`}
				>{opt.label}</button>
			{/each}
		</div>
	</div>

	{#if pullStatus === 'up-to-date' || pullStatus === 'checking'}
		<div class={`flex items-center justify-center gap-2 py-2 ${dark ? 'bg-white/[0.03]' : 'bg-zinc-50'}`}>
			{#if pullStatus === 'checking'}
				<Loader2 class={`h-3.5 w-3.5 animate-spin ${dark ? 'text-zinc-500' : 'text-zinc-400'}`} />
				<span class={`text-[11px] font-semibold ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>Checking...</span>
			{:else}
				<Check class={`h-3.5 w-3.5 ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} />
				<span class={`text-[11px] font-semibold ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>You're up to date</span>
			{/if}
		</div>
	{/if}

	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		bind:this={scrollArea}
		class="no-scrollbar min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto pb-20 lg:pb-0"
		onscroll={handleScroll}
		ontouchstart={handleTouchStart}
		ontouchmove={handleTouchMove}
		ontouchend={handleTouchEnd}
		onwheel={handleWheel}
	>
		{#if loading && articles.length === 0}
			<div class="flex h-full items-center justify-center px-6 text-center">
				<div>
					<p class={`text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Syncing feed</p>
					<p class="mt-2 text-[13px] text-zinc-500">Gathering the latest signals...</p>
				</div>
			</div>
		{:else if articles.length === 0}
			<div class="flex h-full items-center justify-center px-6 text-center">
				<div>
					<p class={`text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>No signals found</p>
					<p class="mt-2 text-[13px] text-zinc-500">Adjust your filters or search to widen the feed.</p>
				</div>
			</div>
		{:else}
			<div class="flex w-full min-w-0 max-w-full flex-col gap-0.5 overflow-hidden px-2 py-2 sm:px-3 sm:py-3">
				{#each articles as article (article.id)}
					<ArticleCard
						{article}
						selected={selectedArticleId === article.id}
						isSaved={savedArticleIds.includes(article.id)}
						isNew={newArticleIds.has(article.id)}
						isRead={readArticleIds.has(article.id)}
						{theme}
						onOpen={onArticleOpen}
						onToggleSave={onToggleSave}
					/>
				{/each}
			</div>
			{#if loadingMore}
				<div class="flex justify-center py-4">
					<Loader2 class="h-4 w-4 animate-spin text-zinc-500" />
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
</section>
