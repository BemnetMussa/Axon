<script lang="ts">
	import { ArrowDownUp } from 'lucide-svelte';
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
	};

	let {
		title,
		articles,
		sources,
		activeSource,
		searchQuery,
		sortBy,
		selectedArticleId,
		savedArticleIds,
		loading,
		syncIndicator,
		onSearchChange,
		onSourceSelect,
		onSortChange,
		onArticleOpen,
		onToggleSave,
		onRefresh
	}: Props = $props();

	const sortOptions: { value: SortOption; label: string }[] = [
		{ value: 'date', label: 'Latest' },
		{ value: 'engagement', label: 'Top' },
		{ value: 'views', label: 'Most Read' },
	];
</script>

<section class="flex h-full min-h-0 flex-1 flex-col bg-[#0b0b0b]">
	<FeedHeader
		{title}
		articleCount={articles.length}
		{searchQuery}
		{syncIndicator}
		onSearchChange={onSearchChange}
		onRefresh={onRefresh}
	/>

	<div class="border-b border-white/[0.04] px-3 py-2 sm:px-5">
		<div class="flex items-center gap-2 sm:gap-3">
			<div class="no-scrollbar flex min-w-0 flex-1 items-center gap-1 overflow-x-auto sm:gap-1.5">
				<button
					onclick={() => onSourceSelect(null)}
					class={`whitespace-nowrap rounded-md px-2 py-1 text-[9px] font-bold uppercase tracking-wider transition-all sm:px-2.5 sm:py-1.5 sm:text-[10px] ${activeSource === null ? 'bg-white text-black' : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300'}`}
				>
					All
				</button>

				{#each sources as source}
					<button
						onclick={() => onSourceSelect(source)}
						class={`whitespace-nowrap rounded-md px-2 py-1 text-[9px] font-bold uppercase tracking-wider transition-all sm:px-2.5 sm:py-1.5 sm:text-[10px] ${activeSource === source ? 'bg-zinc-200 text-black' : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300'}`}
					>
						{source}
					</button>
				{/each}
			</div>

			<div class="flex shrink-0 items-center gap-0.5 border-l border-white/[0.04] pl-2 sm:gap-1 sm:pl-3">
				<ArrowDownUp class="hidden h-3 w-3 text-zinc-600 sm:block" />
				{#each sortOptions as opt}
					<button
						onclick={() => onSortChange(opt.value)}
						class={`whitespace-nowrap rounded-md px-1.5 py-1 text-[9px] font-semibold transition-all sm:px-2 sm:text-[10px] ${sortBy === opt.value ? 'bg-white/[0.08] text-zinc-200' : 'text-zinc-600 hover:text-zinc-400'}`}
					>
						{opt.label}
					</button>
				{/each}
			</div>
		</div>
	</div>

	<div class="no-scrollbar min-h-0 flex-1 overflow-y-auto pb-28 lg:pb-0">
		{#if loading && articles.length === 0}
			<div class="flex h-full items-center justify-center px-6 text-center">
				<div>
					<p class="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Syncing feed</p>
					<p class="mt-2 text-[13px] text-zinc-500">Gathering the latest signals...</p>
				</div>
			</div>
		{:else if articles.length === 0}
			<div class="flex h-full items-center justify-center px-6 text-center">
				<div>
					<p class="text-[10px] font-bold uppercase tracking-widest text-zinc-600">No signals found</p>
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
						onOpen={onArticleOpen}
						onToggleSave={onToggleSave}
					/>
				{/each}
			</div>
		{/if}
	</div>
</section>
