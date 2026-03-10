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

	const CACHE_KEY = 'axon_premium_cache';
	const SAVED_KEY = 'axon_saved_signals';
	const mobileNavItems = [NAVIGATION[0], NAVIGATION[1], NAVIGATION[3]];

	let sources = $derived([...new Set(allArticles.map((article) => article.source))].sort());
	let sourceCounts = $derived.by(() => {
		const counts: Record<string, number> = {};
		allArticles.forEach((article) => {
			counts[article.source] = (counts[article.source] || 0) + 1;
		});
		return counts;
	});
	let filtered = $derived.by(() => {
		let list = allArticles;
		if (showSavedOnly) {
			list = list.filter((article) => savedArticleIds.includes(article.id));
		}
		if (activeSource) list = list.filter((article) => article.source === activeSource);
		if (activeCategory) list = list.filter((article) => article.category === activeCategory);
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			list = list.filter(
				(article) =>
					article.title.toLowerCase().includes(query) ||
					article.source.toLowerCase().includes(query) ||
					(article.content_snippet || '').toLowerCase().includes(query)
			);
		}
		return list;
	});
	let currentTitle = $derived(showSavedOnly ? 'Saved' : (activeCategory ?? 'Frontier'));

	async function load() {
		const raw = localStorage.getItem(CACHE_KEY);
		if (raw) {
			const cached = JSON.parse(raw);
			allArticles = cached.articles;
			trends = cached.trends;
			loading = false;
		}

		const saved = localStorage.getItem(SAVED_KEY);
		if (saved) {
			savedArticleIds = JSON.parse(saved);
		}

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

	function showSaved() {
		showSavedOnly = true;
		activeCategory = null;
		activeSource = null;
		selectedArticle = null;
	}

	function selectSource(source: string | null) {
		activeSource = source;
	}

	function toggleSave(id: number) {
		if (savedArticleIds.includes(id)) {
			savedArticleIds = savedArticleIds.filter((savedId) => savedId !== id);
		} else {
			savedArticleIds = [...savedArticleIds, id];
		}
		persistSaved();
	}

	async function smartSync() {
		syncIndicator = true;
		try {
			await api.triggerRefresh();
			const [articles, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);
			allArticles = articles;
			trends = trendData;
			localStorage.setItem(CACHE_KEY, JSON.stringify({ articles, trends: trendData }));
		} catch (error) {
			console.error('Sync failed', error);
		} finally {
			loading = false;
			syncIndicator = false;
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
</svelte:head>

<div class="relative flex h-screen overflow-hidden bg-[#0b0b0b] text-[#e4e4e7]">
	<DesktopSidebar
		navigation={NAVIGATION}
		{activeCategory}
		{showSavedOnly}
		{sourceCounts}
		onNavigate={selectCategory}
		onShowSaved={showSaved}
	/>

	<div class="relative flex min-w-0 flex-1 overflow-hidden">
		<div class={`min-w-0 flex-1 ${selectedArticle ? 'hidden' : 'flex'} lg:flex ${selectedArticle ? 'lg:max-w-md xl:max-w-lg' : ''}`}>
			<FeedPanel
				title={currentTitle}
				articles={filtered}
				{sources}
				{activeSource}
				{searchQuery}
				selectedArticleId={selectedArticle?.id ?? null}
				{savedArticleIds}
				{loading}
				{syncIndicator}
				onSearchChange={(value) => (searchQuery = value)}
				onSourceSelect={selectSource}
				onArticleOpen={openArticle}
				onToggleSave={toggleSave}
				onRefresh={smartSync}
			/>
		</div>

		{#if selectedArticle}
			<div class="absolute inset-0 z-30 flex bg-[#0a0a0a] lg:static lg:z-auto lg:min-w-0 lg:flex-1 lg:border-l lg:border-white/[0.04] lg:bg-transparent">
				<ReaderPanel
					article={selectedArticle}
					isSaved={savedArticleIds.includes(selectedArticle.id)}
					{chatMessages}
					{chatInput}
					{chatLoading}
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
			onNavigate={selectCategory}
			onShowSaved={showSaved}
		/>
	{/if}
</div>

<style>
	:global(body) {
		background: #0b0b0b;
		overflow: hidden;
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
		color: white !important;
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
		color: #a1a1aa !important;
	}
	:global(.prose a) {
		color: white;
	}
</style>
