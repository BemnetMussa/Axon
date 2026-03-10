<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Article, type Trend } from '$lib/api';
	import FeedPanel from '$lib/components/feed/FeedPanel.svelte';
	import DesktopSidebar from '$lib/components/navigation/DesktopSidebar.svelte';
	import MobileBottomNav from '$lib/components/navigation/MobileBottomNav.svelte';
	import ReaderPanel from '$lib/components/reader/ReaderPanel.svelte';
	import { NAVIGATION, SUGGESTIONS } from '$lib/ui';

	type ChatMessage = {
		role: 'user' | 'ai';
		content: string;
	};

	let allArticles = $state<Article[]>([]);
	let trends = $state<Trend[]>([]);
	let loading = $state(true);
	let syncIndicator = $state(false);
	let searchQuery = $state('');
	let activeSource = $state<string | null>(null);
	let activeCategory = $state<string | null>(null);
	let selectedArticle = $state<Article | null>(null);
	let savedArticleIds = $state<number[]>([]);
	let showSavedOnly = $state(false);
	let chatInput = $state('');
	let chatMessages = $state<ChatMessage[]>([]);
	let chatLoading = $state(false);
	let sortBy = $state<'date' | 'engagement' | 'views'>('date');
	let theme = $state<'dark' | 'light'>('dark');

	let nextCursor = $state<number | null>(null);
	let hasMore = $state(false);
	let loadingMore = $state(false);

	const CACHE_KEY = 'axon_premium_cache';
	const SAVED_KEY = 'axon_saved_signals';
	const THEME_KEY = 'axon_theme';
	const mobileNavItems = [NAVIGATION[0], NAVIGATION[1], NAVIGATION[3], NAVIGATION[4]];

	let sources = $derived([...new Set(allArticles.map((a) => a.source))].sort());
	let sourceCounts = $derived.by(() => {
		const counts: Record<string, number> = {};
		allArticles.forEach((a) => {
			counts[a.source] = (counts[a.source] || 0) + 1;
		});
		return counts;
	});
	let filtered = $derived.by(() => {
		let list = allArticles;
		if (showSavedOnly) list = list.filter((a) => savedArticleIds.includes(a.id));
		if (activeSource) list = list.filter((a) => a.source === activeSource);
		if (activeCategory) list = list.filter((a) => a.category === activeCategory);
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(a) =>
					a.title.toLowerCase().includes(q) ||
					a.source.toLowerCase().includes(q) ||
					(a.content_snippet || '').toLowerCase().includes(q)
			);
		}
		if (sortBy === 'engagement') list = [...list].sort((a, b) => (b.likes || 0) - (a.likes || 0));
		else if (sortBy === 'views') list = [...list].sort((a, b) => (b.views || 0) - (a.views || 0));
		return list;
	});
	let currentTitle = $derived(showSavedOnly ? 'Saved' : (activeCategory ?? 'Frontier'));

	function applyTheme(t: 'dark' | 'light') {
		theme = t;
		document.documentElement.classList.toggle('light', t === 'light');
		localStorage.setItem(THEME_KEY, t);
	}

	function toggleTheme() {
		applyTheme(theme === 'dark' ? 'light' : 'dark');
	}

	async function load() {
		const savedTheme = localStorage.getItem(THEME_KEY) as 'dark' | 'light' | null;
		if (savedTheme) applyTheme(savedTheme);

		const raw = localStorage.getItem(CACHE_KEY);
		if (raw) {
			try {
				const cached = JSON.parse(raw);
				allArticles = cached.articles ?? [];
				trends = cached.trends ?? [];
				nextCursor = cached.nextCursor ?? null;
				hasMore = cached.hasMore ?? false;
				loading = false;
			} catch { /* ignore corrupt cache */ }
		}

		const saved = localStorage.getItem(SAVED_KEY);
		if (saved) savedArticleIds = JSON.parse(saved);

		await smartSync();
	}

	function persistSaved() {
		localStorage.setItem(SAVED_KEY, JSON.stringify(savedArticleIds));
	}

	function selectCategory(id: string | null) {
		activeCategory = id;
		activeSource = null;
		selectedArticle = null;
		showSavedOnly = false;
	}

	function showSavedView() {
		showSavedOnly = true;
		activeCategory = null;
		activeSource = null;
		selectedArticle = null;
	}

	function selectSource(source: string | null) {
		activeSource = source;
	}

	function toggleSave(id: number) {
		savedArticleIds = savedArticleIds.includes(id)
			? savedArticleIds.filter((s) => s !== id)
			: [...savedArticleIds, id];
		persistSaved();
	}

	async function smartSync() {
		syncIndicator = true;
		try {
			await api.triggerRefresh();
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);
			allArticles = articleRes.articles;
			nextCursor = articleRes.next_cursor;
			hasMore = articleRes.has_more;
			trends = trendData;
			localStorage.setItem(CACHE_KEY, JSON.stringify({
				articles: allArticles, trends: trendData,
				nextCursor, hasMore
			}));
		} catch (error) {
			console.error('Sync failed', error);
		} finally {
			loading = false;
			syncIndicator = false;
		}
	}

	async function loadMore() {
		if (loadingMore || !hasMore || !nextCursor) return;
		loadingMore = true;
		try {
			const res = await api.getArticles(nextCursor);
			allArticles = [...allArticles, ...res.articles];
			nextCursor = res.next_cursor;
			hasMore = res.has_more;
		} catch (error) {
			console.error('Load more failed', error);
		} finally {
			loadingMore = false;
		}
	}

	function openArticle(article: Article) {
		selectedArticle = article;
		chatMessages = [];
		chatInput = '';
		api.trackView(article.id);
	}

	function closeReader() {
		selectedArticle = null;
	}

	async function sendChat(message?: string) {
		const text = message || chatInput;
		if (!text.trim() || !selectedArticle || chatLoading) return;

		const userMessage = text.trim();
		chatMessages = [...chatMessages, { role: 'user', content: userMessage }];
		chatInput = '';
		chatLoading = true;

		try {
			const response = await api.chatWithArticle(selectedArticle.id, userMessage);
			chatMessages = [...chatMessages, { role: 'ai', content: response.answer }];
		} catch {
			chatMessages = [...chatMessages, { role: 'ai', content: 'Intelligence layer unavailable.' }];
		} finally {
			chatLoading = false;
		}
	}

	onMount(load);
</script>

<svelte:head>
	<title>AXON — Intelligence Platform</title>
	<meta name="theme-color" content={theme === 'dark' ? '#0b0b0b' : '#ffffff'} />
</svelte:head>

<div class={`relative flex h-screen overflow-hidden transition-colors duration-300 ${theme === 'dark' ? 'bg-[#0b0b0b] text-[#e4e4e7]' : 'bg-white text-zinc-900'}`}>
	<DesktopSidebar
		navigation={NAVIGATION}
		{activeCategory}
		{showSavedOnly}
		{sourceCounts}
		{theme}
		onNavigate={selectCategory}
		onShowSaved={showSavedView}
		onToggleTheme={toggleTheme}
	/>

	<div class="relative flex min-w-0 flex-1">
		<div class={`min-w-0 overflow-hidden ${selectedArticle ? 'hidden lg:flex lg:w-[340px] lg:shrink-0 xl:w-[400px]' : 'flex flex-1'}`}>
			<FeedPanel
				title={currentTitle}
				articles={filtered}
				{sources}
				{activeSource}
				{searchQuery}
				{sortBy}
				{theme}
				{hasMore}
				{loadingMore}
				selectedArticleId={selectedArticle?.id ?? null}
				{savedArticleIds}
				{loading}
				{syncIndicator}
				onSearchChange={(value) => (searchQuery = value)}
				onSourceSelect={selectSource}
				onSortChange={(value) => (sortBy = value)}
				onArticleOpen={openArticle}
				onToggleSave={toggleSave}
				onRefresh={smartSync}
				onLoadMore={loadMore}
			/>
		</div>

		{#if selectedArticle}
			<div class={`absolute inset-0 z-30 flex overflow-hidden lg:relative lg:z-auto lg:min-w-0 lg:flex-1 lg:border-l ${theme === 'dark' ? 'bg-[#0a0a0a] lg:border-white/[0.04]' : 'bg-white lg:border-zinc-200'}`}>
				<ReaderPanel
					article={selectedArticle}
					isSaved={savedArticleIds.includes(selectedArticle.id)}
					{chatMessages}
					{chatInput}
					{chatLoading}
					{theme}
					suggestions={SUGGESTIONS}
					onBack={closeReader}
					onToggleSave={toggleSave}
					onOpenExternal={(url) => window.open(url, '_blank', 'noopener,noreferrer')}
					onChatInputChange={(value) => (chatInput = value)}
					onSendChat={sendChat}
				/>
			</div>
		{/if}
	</div>

	{#if !selectedArticle}
		<MobileBottomNav
			items={mobileNavItems}
			{activeCategory}
			{showSavedOnly}
			{theme}
			onNavigate={selectCategory}
			onShowSaved={showSavedView}
		/>
	{/if}
</div>

<style>
	:global(body) {
		overflow: hidden;
	}
	:global(html) {
		background: #0b0b0b;
		transition: background-color 0.3s;
	}
	:global(html.light) {
		background: #ffffff;
	}
	:global(html.light body) {
		background: #ffffff;
	}
	:global(button) {
		touch-action: manipulation;
	}
	:global(.no-scrollbar::-webkit-scrollbar) {
		display: none;
	}
	:global(.no-scrollbar) {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
	:global(.prose p) {
		margin-top: 0 !important;
		margin-bottom: 1rem !important;
	}
	:global(.prose p:last-child) {
		margin-bottom: 0 !important;
	}
	:global(.prose h1, .prose h2, .prose h3) {
		font-weight: 700 !important;
		margin-top: 1.5rem !important;
		margin-bottom: 0.75rem !important;
	}
	:global(.prose ul, .prose ol) {
		margin-bottom: 1rem !important;
		padding-left: 1.25rem !important;
	}
	:global(.prose li) {
		margin-bottom: 0.35rem !important;
	}
	:global(.prose a) {
		text-decoration: underline;
		text-underline-offset: 2px;
	}
</style>
