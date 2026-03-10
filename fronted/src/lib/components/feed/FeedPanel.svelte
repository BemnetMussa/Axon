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

<section class="flex h-full min-h-0 flex-1 flex-col bg-[#0b0b0b] lg:border-r lg:border-white/4">
	<FeedHeader
		{title}
		articleCount={articles.length}
		{searchQuery}
		{syncIndicator}
		onSearchChange={onSearchChange}
		onRefresh={onRefresh}
	/>

	<div class="border-b border-white/4 px-4 pb-4 pt-3 sm:px-6 lg:px-10">
		<div class="no-scrollbar flex gap-2 overflow-x-auto sm:gap-3">
			<button
				onclick={() => onSourceSelect(null)}
				class={`min-h-10 whitespace-nowrap rounded-full border px-4 py-2 text-[10px] font-black uppercase tracking-[1.8px] transition-all ${activeSource === null ? 'border-white bg-white text-black' : 'border-white/5 bg-transparent text-zinc-500 hover:border-white/20 hover:text-zinc-300'}`}
			>
				Meta
			</button>

			{#each sources as source}
				<button
					onclick={() => onSourceSelect(source)}
					class={`min-h-10 whitespace-nowrap rounded-full border px-4 py-2 text-[10px] font-black uppercase tracking-[1.8px] transition-all ${activeSource === source ? 'border-zinc-100 bg-zinc-100 text-black' : 'border-white/5 bg-transparent text-zinc-500 hover:border-white/20 hover:text-zinc-300'}`}
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
					<p class="text-[11px] font-bold uppercase tracking-[2px] text-zinc-600">Syncing feed</p>
					<p class="mt-3 text-sm text-zinc-400">Gathering the latest signals and rebuilding the frontier view.</p>
				</div>
			</div>
		{:else if articles.length === 0}
			<div class="flex h-full items-center justify-center px-6 text-center">
				<div class="max-w-sm">
					<p class="text-[11px] font-bold uppercase tracking-[2px] text-zinc-600">No matching signals</p>
					<p class="mt-3 text-sm leading-6 text-zinc-400">Adjust your filters or search query to widen the feed again.</p>
				</div>
			</div>
		{:else}
			<div class="mx-auto w-full max-w-152 space-y-2 px-3 py-4 sm:px-4 sm:py-6 lg:px-6 lg:py-10">
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