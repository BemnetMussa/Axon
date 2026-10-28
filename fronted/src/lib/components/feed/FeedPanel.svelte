<script lang="ts">
	import { Check } from 'lucide-svelte';
	import SignalLoader from '$lib/components/ui/SignalLoader.svelte';
	import { type Article } from '$lib/api';
	import type { NavItem } from '$lib/ui';
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import VirtualFeed from '$lib/components/feed/VirtualFeed.svelte';
	import FeedHeader from '$lib/components/feed/FeedHeader.svelte';

	type PullStatus = 'idle' | 'pulling' | 'checking' | 'up-to-date' | 'new' | 'error';

	type Props = {
		title: string;
		articles: Article[];
		searchQuery: string;
		theme: 'dark' | 'light';
		hasMore: boolean;
		loadingMore: boolean;
		selectedArticleId: number | null;
		savedArticleIds: number[];
		readArticleIds: Set<number>;
		loading: boolean;
		syncIndicator: boolean;
		newArticleIds?: Set<number>;
		tabs: NavItem[];
		activeTab: string | null;
		showSavedOnly: boolean;
		semanticSearchActive?: boolean;
		dbEmpty?: boolean;
		scrollArea?: HTMLDivElement;
		onTabSelect: (id: string | null) => void;
		onSearchChange: (value: string) => void;
		onArticleOpen: (article: Article) => void;
		onToggleSave: (id: number) => void;
		onLoadMore: () => void;
		onRefresh?: () => Promise<number>;
	};

	let {
		title, articles, searchQuery, theme, hasMore, loadingMore, selectedArticleId,
		savedArticleIds, readArticleIds, loading, syncIndicator, newArticleIds = new Set(),
		tabs, activeTab, showSavedOnly, semanticSearchActive = false, dbEmpty = false,
		scrollArea = $bindable(), onTabSelect, onSearchChange, onArticleOpen, onToggleSave,
		onLoadMore, onRefresh
	}: Props = $props();

	let dark = $derived(theme === 'dark');
	let pullStatus = $state<PullStatus>('idle');
	let newCount = $state(0);
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

	let rule = $derived(dark ? 'border-white/10' : 'border-black/10');
	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');

	function tabClass(active: boolean) {
		if (active) return dark ? 'border-white text-white' : 'border-black text-black';
		return dark ? 'border-transparent text-white/45' : 'border-transparent text-black/45';
	}
</script>

<section class={`relative flex h-full min-h-0 min-w-0 flex-1 flex-col overflow-hidden ${dark ? 'bg-[#0a0a0a]' : 'bg-[#fafafa]'}`}>
	<FeedHeader {title} articleCount={articles.length} {searchQuery} {syncIndicator} {theme} {onSearchChange} hasSemanticSearch={semanticSearchActive} />

	<!-- Mobile tabs: desktop lists the same tabs in the sidebar -->
	<nav class={`no-scrollbar flex shrink-0 gap-5 overflow-x-auto border-b px-4 lg:hidden ${rule}`} aria-label="Feeds">
		{#each tabs as tab (tab.id)}
			{@const active = activeTab === tab.id && !showSavedOnly}
			<button
				type="button"
				onclick={() => onTabSelect(tab.id)}
				class={`axon-label shrink-0 border-b-2 py-2.5 transition-colors ${tabClass(active)}`}
				aria-current={active ? 'page' : undefined}
			>{tab.label}</button>
		{/each}
	</nav>

	{#if pullStatus !== 'idle' && pullStatus !== 'pulling'}
		<div class={`axon-label flex items-center justify-center gap-2 border-b py-2 ${rule} ${muted}`}>
			{#if pullStatus === 'checking'}
				<SignalLoader size={14} />
				<span>Checking</span>
			{:else if pullStatus === 'new'}
				<Check class={`h-3.5 w-3.5 ${dark ? 'text-white' : 'text-black'}`} />
				<span class={dark ? 'text-white' : 'text-black'}>{newCount} new {newCount === 1 ? 'story' : 'stories'}</span>
			{:else if pullStatus === 'error'}
				<span>Couldn't refresh — check your connection</span>
			{:else}
				<Check class="h-3.5 w-3.5" />
				<span>You're up to date</span>
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
			<div class="flex h-full flex-col gap-2 px-2.5 py-3 sm:px-4">
				{#each [1, 2, 3, 4, 5] as _}
					<div class={`h-36 w-full animate-pulse rounded-2xl ${dark ? 'bg-white/5' : 'bg-black/5'}`}></div>
				{/each}
			</div>
		{:else if articles.length === 0}
			<div class="flex h-full items-center justify-center px-8 text-center">
				<div class="max-w-xs">
					{#if searchQuery.trim()}
						<p class="text-[15px] font-semibold">No matches for “{searchQuery.trim()}”</p>
						<p class={`mt-1.5 text-[13px] leading-relaxed ${muted}`}>Try a broader word, or a company or project name.</p>
						<button type="button" onclick={() => onSearchChange('')} class={`axon-label mt-5 px-3 py-2 ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}>Clear search</button>
					{:else if showSavedOnly}
						<p class="text-[15px] font-semibold">Nothing saved yet</p>
						<p class={`mt-1.5 text-[13px] leading-relaxed ${muted}`}>Tap the bookmark on any story to keep it here.</p>
					{:else if dbEmpty}
						<p class="text-[15px] font-semibold">The first sweep is still running</p>
						<p class={`mt-1.5 text-[13px] leading-relaxed ${muted}`}>Stories appear here as soon as it finishes.</p>
					{:else}
						<p class="text-[15px] font-semibold">Nothing here yet</p>
						<p class={`mt-1.5 text-[13px] leading-relaxed ${muted}`}>New stories land every few hours.</p>
					{/if}
				</div>
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
							onToggleSave={onToggleSave}
						/>
					{/snippet}
				</VirtualFeed>
			</div>
			{#if loadingMore}
				<div class="flex justify-center py-4">
					<SignalLoader size={16} class={muted} />
				</div>
			{/if}
			{#if hasMore && !loadingMore}
				<div class="flex justify-center py-4">
					<button onclick={onLoadMore} class={`axon-label px-3 py-2 transition-colors ${muted} ${dark ? 'hover:text-white' : 'hover:text-black'}`}>Load more</button>
				</div>
			{/if}
			{#if !hasMore && !loadingMore}
				<div class={`axon-label flex flex-col items-center gap-1.5 py-8 ${muted}`}>
					<Check class="h-4 w-4" />
					<p>You're all caught up</p>
				</div>
			{/if}
		{/if}
	</div>
</section>
