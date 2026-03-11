<script lang="ts">
	import { ArrowDownUp, Loader2 } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import FeedHeader from '$lib/components/feed/FeedHeader.svelte';

	type SortOption = 'date' | 'engagement' | 'views';

	type Props = {
		title: string;
		articles: Article[];
		sources: string[];
		activeSource: string | null;
		searchQuery: string;
		sortBy: SortOption;
		theme: 'dark' | 'light';
		hasMore: boolean;
		loadingMore: boolean;
		selectedArticleId: number | null;
		savedArticleIds: number[];
		loading: boolean;
		syncIndicator: boolean;
		onSearchChange: (value: string) => void;
		onSourceSelect: (source: string | null) => void;
		onSortChange: (value: SortOption) => void;
		onArticleOpen: (article: Article) => void;
		onToggleSave: (id: number) => void;
		onRefresh: () => void;
		onLoadMore: () => void;
	};

	let {
		title, articles, sources, activeSource, searchQuery, sortBy, theme,
		hasMore, loadingMore, selectedArticleId, savedArticleIds, loading,
		syncIndicator, onSearchChange, onSourceSelect, onSortChange,
		onArticleOpen, onToggleSave, onRefresh, onLoadMore
	}: Props = $props();

	const sortOptions: { value: SortOption; label: string }[] = [
		{ value: 'date', label: 'Latest' },
		{ value: 'engagement', label: 'Top' },
		{ value: 'views', label: 'Most Read' },
	];

	let dark = $derived(theme === 'dark');

	function handleScroll(e: Event) {
		const el = e.target as HTMLDivElement;
		if (el.scrollTop + el.clientHeight >= el.scrollHeight - 200) {
			onLoadMore();
		}
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

<section class={`flex h-full min-h-0 flex-1 flex-col ${dark ? 'bg-[#0b0b0b]' : 'bg-white'}`}>
	<FeedHeader {title} articleCount={articles.length} {searchQuery} {syncIndicator} {theme} onSearchChange={onSearchChange} onRefresh={onRefresh} />

	<div class={`border-b px-3 py-2 sm:px-5 ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
		<div class="flex items-center gap-2 sm:gap-3">
			<div class="no-scrollbar flex min-w-0 flex-1 items-center gap-1 overflow-x-auto sm:gap-1.5">
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
			<div class={`flex shrink-0 items-center gap-0.5 border-l pl-2 sm:gap-1 sm:pl-3 ${dark ? 'border-white/[0.04]' : 'border-zinc-200'}`}>
				<ArrowDownUp class={`hidden h-3 w-3 sm:block ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
				{#each sortOptions as opt}
					<button
						onclick={() => onSortChange(opt.value)}
						class={`whitespace-nowrap rounded-md px-1.5 py-1 text-[9px] font-semibold transition-all sm:px-2 sm:text-[10px] ${sortBtnClass(sortBy === opt.value)}`}
					>{opt.label}</button>
				{/each}
			</div>
		</div>
	</div>

	<div class="no-scrollbar min-h-0 flex-1 overflow-y-auto pb-20 lg:pb-0" onscroll={handleScroll}>
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
			<div class="flex flex-col gap-0.5 px-2 py-2 sm:px-3 sm:py-3">
				{#each articles as article (article.id)}
					<ArticleCard
						{article}
						selected={selectedArticleId === article.id}
						isSaved={savedArticleIds.includes(article.id)}
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
		{/if}
	</div>
</section>
