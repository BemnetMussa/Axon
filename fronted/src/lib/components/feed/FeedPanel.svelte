<script lang="ts">
	import type { Article } from '$lib/api';
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import FeedHeader from '$lib/components/feed/FeedHeader.svelte';

	type Props = {
		title: string;
		articles: Article[];
		sources: string[];
		activeSource: string | null;
		searchQuery: string;
		selectedArticleId: number | null;
		savedArticleIds: number[];
		loading: boolean;
		syncIndicator: boolean;
		onSearchChange: (value: string) => void;
		onSourceSelect: (source: string | null) => void;
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
		selectedArticleId,
		savedArticleIds,
		loading,
		syncIndicator,
		onSearchChange,
		onSourceSelect,
		onArticleOpen,
		onToggleSave,
		onRefresh
	}: Props = $props();
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

	<div class="border-b border-white/[0.04] px-4 py-2.5 sm:px-5">
		<div class="no-scrollbar flex items-center gap-1.5 overflow-x-auto">
			<button
				onclick={() => onSourceSelect(null)}
				class={`whitespace-nowrap rounded-md px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider transition-all ${activeSource === null ? 'bg-white text-black' : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300'}`}
			>
				All
			</button>

			{#each sources as source}
				<button
					onclick={() => onSourceSelect(source)}
					class={`whitespace-nowrap rounded-md px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider transition-all ${activeSource === source ? 'bg-zinc-200 text-black' : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300'}`}
				>
					{source}
				</button>
			{/each}
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
