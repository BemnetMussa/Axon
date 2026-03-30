<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api, feedCache, type Article, type Trend } from '$lib/api';
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
	let fetchError = $state<string | null>(null);
	let syncIndicator = $state(false);
	let searchQuery = $state('');
	let activeSource = $state<string | null>(null);
	let activeCategory = $state<string | null>(null);
	let selectedArticle = $state<Article | null>(null);
	let showDigestView = $state(false);
	let digestContent = $state<{content: string, created_at: string} | null>(null);
	let savedArticleIds = $state<number[]>([]);
	let showSavedOnly = $state(false);
	let chatInput = $state('');
	let chatMessages = $state<ChatMessage[]>([]);
	let chatLoading = $state(false);
	let chatSuggestions = $state<string[]>([...SUGGESTIONS]);
	let suggestionsLoading = $state(false);
	let sortBy = $state<'date' | 'engagement' | 'views'>('date');
	let timeFilter = $state<'all' | 'today' | 'week' | 'month'>('all');
	let theme = $state<'dark' | 'light'>('dark');

	let nextCursor = $state<number | null>(null);
	let hasMore = $state(false);
	let loadingMore = $state(false);
	let newArticleIds = $state<Set<number>>(new Set());
	let readArticleIds = $state<Set<number>>(new Set());
	let feedScrollArea = $state<HTMLDivElement | undefined>();

	const SAVED_KEY = 'axon_saved_signals';
	const SEEN_KEY = 'axon_seen_articles';
	const READ_KEY = 'axon_read_articles';
	const THEME_KEY = 'axon_theme';
	const POLL_INTERVAL_MS = 60_000;
	const mobileNavItems = NAVIGATION.slice(0, 4);

	let pollTimer: ReturnType<typeof setInterval> | null = null;

	let sources = $derived([...new Set(allArticles.map((a) => a.source))].sort());
	let sourceCounts = $derived.by(() => {
		const counts: Record<string, number> = {};
		allArticles.forEach((a) => {
			counts[a.source] = (counts[a.source] || 0) + 1;
		});
		return counts;
	});
	function parseDate(dateStr: string): number {
		let d = dateStr;
		if (!d.endsWith('Z') && !d.includes('+') && !d.includes('-', 10)) d += 'Z';
		return new Date(d).getTime();
	}

	let semanticSearchResults = $state<Article[] | null>(null);
	let searchingSemantic = $state(false);
	let searchTimeout: ReturnType<typeof setTimeout> | null = null;
	
	$effect(() => {
		if (searchQuery.trim().length > 2) {
			searchingSemantic = true;
			if (searchTimeout) clearTimeout(searchTimeout);
			searchTimeout = setTimeout(async () => {
				try {
					const res = await api.searchSemantic(searchQuery);
					semanticSearchResults = res.articles;
				} catch {
					semanticSearchResults = null;
				} finally {
					searchingSemantic = false;
				}
			}, 600);
		} else {
			semanticSearchResults = null;
			searchingSemantic = false;
		}
	});

	let filtered = $derived.by(() => {
		if (semanticSearchResults && searchQuery.trim().length > 2) return semanticSearchResults;
		
		let list = allArticles;
		if (showSavedOnly) list = list.filter((a) => savedArticleIds.includes(a.id));
		if (activeSource) list = list.filter((a) => a.source === activeSource);
		if (activeCategory) {
			if (activeCategory === 'GitHub') list = list.filter((a) => a.source === 'GitHub');
			else list = list.filter((a) => a.category === activeCategory);
		}
		if (timeFilter !== 'all') {
			const now = Date.now();
			const cutoff = timeFilter === 'today' ? now - 86_400_000
				: timeFilter === 'week' ? now - 7 * 86_400_000
				: now - 30 * 86_400_000;
			list = list.filter((a) => parseDate(a.published_date) >= cutoff);
		}
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

	// -----------------------------------------------------------------------
	// Boot: cache-first, then background revalidate
	// -----------------------------------------------------------------------

	async function load() {
		const savedTheme = localStorage.getItem(THEME_KEY) as 'dark' | 'light' | null;
		if (savedTheme) applyTheme(savedTheme);

		const saved = localStorage.getItem(SAVED_KEY);
		if (saved) savedArticleIds = JSON.parse(saved);

		readArticleIds = loadReadIds();

		const cached = feedCache.get();

		if (cached && feedCache.isUsable()) {
			fetchError = null;
			allArticles = cached.articles;
			trends = cached.trends;
			nextCursor = cached.nextCursor;
			hasMore = cached.hasMore;
			loading = false;

			if (!feedCache.isFresh()) {
				backgroundRevalidate();
			}
		} else {
			await fetchFirstPage();
		}

		startPolling();
	}

	async function fetchFirstPage() {
		loading = allArticles.length === 0;
		syncIndicator = true;
		fetchError = null;
		try {
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);
			allArticles = articleRes.articles;
			nextCursor = articleRes.next_cursor;
			hasMore = articleRes.has_more;
			trends = trendData;
			feedCache.set({ articles: allArticles, trends, nextCursor, hasMore });
		} catch (error) {
			console.error('Fetch failed', error);
			fetchError = error instanceof Error ? error.message : 'Failed to load articles.';
		} finally {
			loading = false;
			syncIndicator = false;
		}
	}

	async function backgroundRevalidate() {
		syncIndicator = true;
		try {
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);

			const existingIds = new Set(allArticles.map((a) => a.id));
			const freshArticles = articleRes.articles.filter((a) => !existingIds.has(a.id));

			if (freshArticles.length > 0) {
				const seen = loadSeenIds();
				const brandNew = freshArticles.filter((a) => !seen.has(a.id));
				if (brandNew.length > 0) {
					newArticleIds = new Set([...newArticleIds, ...brandNew.map((a) => a.id)]);
				}
			}

			const freshIds = new Set(articleRes.articles.map((a) => a.id));
			const kept = allArticles.filter((a) => !freshIds.has(a.id));
			allArticles = [...articleRes.articles, ...kept];

			nextCursor = articleRes.next_cursor;
			hasMore = articleRes.has_more;
			trends = trendData;
			feedCache.set({ articles: allArticles, trends, nextCursor, hasMore });

			if (freshArticles.length > 0) {
				scrollFeedToTop();
			}
		} catch {
			// silent — user still has cached data
		} finally {
			syncIndicator = false;
		}
	}

	// -----------------------------------------------------------------------
	// Poll for new signals every 60s — auto-fetch when found
	// -----------------------------------------------------------------------

	function startPolling() {
		pollTimer = setInterval(async () => {
			const latestId = feedCache.latestId();
			if (!latestId) return;
			try {
				const count = await api.countNewSince(latestId);
				if (count > 0) await backgroundRevalidate();
			} catch { /* silent */ }
		}, POLL_INTERVAL_MS);
	}

	function scrollFeedToTop() {
		feedScrollArea?.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function checkForNew(): Promise<boolean> {
		const latestId = feedCache.latestId();
		if (!latestId) return false;
		try {
			const count = await api.countNewSince(latestId);
			if (count > 0) {
				await backgroundRevalidate();
				return true;
			}
			return false;
		} catch {
			return false;
		}
	}

	function loadSeenIds(): Set<number> {
		try {
			const raw = localStorage.getItem(SEEN_KEY);
			return raw ? new Set(JSON.parse(raw)) : new Set();
		} catch { return new Set(); }
	}

	function markSeen(id: number) {
		newArticleIds.delete(id);
		newArticleIds = new Set(newArticleIds);
		const seen = loadSeenIds();
		seen.add(id);
		const kept = [...seen].slice(-500);
		localStorage.setItem(SEEN_KEY, JSON.stringify(kept));
	}

	function loadReadIds(): Set<number> {
		try {
			const raw = localStorage.getItem(READ_KEY);
			return raw ? new Set(JSON.parse(raw)) : new Set();
		} catch { return new Set(); }
	}

	function markRead(id: number) {
		if (readArticleIds.has(id)) return;
		readArticleIds.add(id);
		readArticleIds = new Set(readArticleIds);
		const kept = [...readArticleIds].slice(-1000);
		localStorage.setItem(READ_KEY, JSON.stringify(kept));
	}

	function persistSaved() {
		localStorage.setItem(SAVED_KEY, JSON.stringify(savedArticleIds));
	}

	function selectCategory(id: string | null) {
		activeCategory = id;
		activeSource = null;
		selectedArticle = null;
		showSavedOnly = false;
		showDigestView = false;
		
		setTimeout(() => {
			if (filtered.length === 0) {
				manualRefresh();
			}
		}, 10);
	}

	function showSavedView() {
		showSavedOnly = true;
		activeCategory = null;
		activeSource = null;
		selectedArticle = null;
		showDigestView = false;
	}

	function selectSource(source: string | null) {
		activeSource = source;
	}

	async function showDigest() {
		showDigestView = true;
		activeCategory = null;
		activeSource = null;
		selectedArticle = null;
		showSavedOnly = false;
		if (!digestContent) {
			try {
				digestContent = await api.getLatestDigest() || { content: 'No weekly digest available yet.', created_at: new Date().toISOString() };
			} catch (e) {
				console.error(e);
				digestContent = { content: 'No weekly digest available yet.', created_at: new Date().toISOString() };
			}
		}
	}

	async function generateDigest() {
		if (!digestContent) return;
		digestContent = { ...digestContent, content: 'Generating new Weekly Synthesis. Please wait roughly 10 seconds...' };
		try {
			const res = await fetch('/api/backend/digests/generate', { method: 'POST' });
			const data = await res.json();
			if (data.status === 'success') {
				const fresh = await api.getLatestDigest();
				if (fresh) digestContent = fresh;
			}
		} catch (e) {
			console.error(e);
			digestContent = { ...digestContent, content: 'Failed to generate. Please check server logs.' };
		}
	}

	function toggleSave(id: number) {
		savedArticleIds = savedArticleIds.includes(id)
			? savedArticleIds.filter((s) => s !== id)
			: [...savedArticleIds, id];
		persistSaved();
	}

	async function manualRefresh() {
		syncIndicator = true;
		fetchError = null;
		try {
			await api.triggerRefresh(activeCategory);
			if (activeCategory === 'GitHub') activeSource = 'GitHub';
			await fetchFirstPage();
		} catch (error) {
			console.error('Refresh failed', error);
			fetchError = error instanceof Error ? error.message : 'Failed to refresh feed.';
			syncIndicator = false;
		}
	}

	async function loadMore() {
		if (loadingMore || !hasMore || !nextCursor) return;
		loadingMore = true;
		try {
			const res = await api.getArticles(nextCursor);
			const existingIds = new Set(allArticles.map((a) => a.id));
			const newOnes = res.articles.filter((a) => !existingIds.has(a.id));
			allArticles = [...allArticles, ...newOnes];
			nextCursor = res.next_cursor;
			hasMore = res.has_more;
			feedCache.appendPage(newOnes, res.next_cursor, res.has_more);
		} catch (error) {
			console.error('Load more failed', error);
		} finally {
			loadingMore = false;
		}
	}

	function openArticle(article: Article) {
		selectedArticle = article;
		showDigestView = false;
		chatMessages = [];
		chatInput = '';
		markSeen(article.id);
		markRead(article.id);
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

	$effect(() => {
		const id = selectedArticle?.id;
		if (id == null) return;
		let cancelled = false;
		suggestionsLoading = true;
		chatSuggestions = [...SUGGESTIONS];
		api
			.getChatSuggestions(id)
			.then((res) => {
				if (cancelled) return;
				if (res.suggestions && res.suggestions.length >= 3) {
					chatSuggestions = res.suggestions;
				}
			})
			.catch(() => {
				/* keep fallback SUGGESTIONS */
			})
			.finally(() => {
				if (!cancelled) suggestionsLoading = false;
			});
		return () => {
			cancelled = true;
		};
	});

	onMount(load);
	onDestroy(() => { if (pollTimer) clearInterval(pollTimer); });
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
		onShowDigest={showDigest}
		onToggleTheme={toggleTheme}
	/>

	<div class="relative flex min-w-0 flex-1 overflow-hidden">
		<div class={`min-w-0 overflow-hidden ${selectedArticle || showDigestView ? 'hidden lg:flex lg:w-[340px] lg:shrink-0 xl:w-[400px]' : 'flex min-w-0 flex-1'}`}>
			<div class="flex min-w-0 flex-1 flex-col overflow-hidden">
				{#if fetchError}
					<div class={`mx-3 mt-3 rounded-md border px-3 py-2 text-xs ${theme === 'dark' ? 'border-red-400/40 bg-red-500/10 text-red-200' : 'border-red-200 bg-red-50 text-red-700'}`}>
						{fetchError}
					</div>
				{/if}
				<FeedPanel
					title={currentTitle}
					articles={filtered}
					{sources}
					{activeSource}
					{searchQuery}
					{sortBy}
					{timeFilter}
					{theme}
					{hasMore}
					{loadingMore}
					selectedArticleId={selectedArticle?.id ?? null}
					{savedArticleIds}
					{readArticleIds}
					{loading}
					{syncIndicator}
					{newArticleIds}
					onSearchChange={(value) => (searchQuery = value)}
					onSourceSelect={selectSource}
					onSortChange={(value) => (sortBy = value)}
					onTimeFilterChange={(value) => (timeFilter = value)}
					onArticleOpen={openArticle}
					onToggleSave={toggleSave}
					onRefresh={manualRefresh}
					onLoadMore={loadMore}
					onCheckNew={checkForNew}
					onToggleTheme={toggleTheme}
					bind:scrollArea={feedScrollArea}
				/>
			</div>
		</div>

		{#if selectedArticle || showDigestView}
			<div class={`absolute inset-0 z-30 flex overflow-hidden lg:relative lg:z-auto lg:w-0 lg:flex-1 lg:border-l ${theme === 'dark' ? 'bg-[#0a0a0a] lg:border-white/[0.04]' : 'bg-white lg:border-zinc-200'}`}>
				{#if showDigestView && digestContent}
					<div class="flex h-full w-full flex-col overflow-y-auto px-6 py-8 sm:px-12 sm:py-12">
						<div class="mx-auto w-full max-w-3xl">
							<button onclick={() => showDigestView = false} class="mb-8 flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-zinc-500 hover:text-zinc-300">
								&larr; Back to feed
							</button>
							<h1 class={`mb-4 text-3xl font-bold md:text-5xl ${theme === 'dark' ? 'text-white' : 'text-black'}`}>Weekly Synthesis</h1>
							<p class={`mb-12 text-sm ${theme === 'dark' ? 'text-zinc-400' : 'text-zinc-500'}`}>Synthesized roughly {digestContent.created_at ? new Date(digestContent.created_at).toLocaleDateString() : 'recently'}</p>
							
							<div class={`prose max-w-none text-[15px] leading-[1.8] sm:text-[17px] ${theme === 'dark' ? 'prose-invert prose-p:text-[#d4d4d8] prose-headings:text-white' : 'prose-p:text-zinc-700 prose-headings:text-black'}`}>
								{digestContent.content}
							</div>
							{#if digestContent.content.includes('No weekly digest available')}
								<button onclick={generateDigest} class={`mt-8 rounded-lg px-6 py-3 text-[13px] font-bold shadow-lg transition-all ${theme === 'dark' ? 'bg-white text-black hover:bg-zinc-200' : 'bg-black text-white hover:bg-zinc-800'}`}>
									Generate First Digest
								</button>
							{/if}
						</div>
					</div>
				{:else if selectedArticle}
					<ReaderPanel
						article={selectedArticle}
						isSaved={savedArticleIds.includes(selectedArticle.id)}
						{chatMessages}
						{chatInput}
						{chatLoading}
						{suggestionsLoading}
						{theme}
						suggestions={chatSuggestions}
						onBack={closeReader}
						onToggleSave={toggleSave}
						onOpenExternal={(url) => window.open(url, '_blank', 'noopener,noreferrer')}
						onChatInputChange={(value) => (chatInput = value)}
						onSendChat={sendChat}
					/>
				{/if}
			</div>
		{/if}
	</div>

	{#if !selectedArticle && !showDigestView}
		<MobileBottomNav
			items={NAVIGATION}
			{activeCategory}
			{showSavedOnly}
			{theme}
			onNavigate={selectCategory}
			onShowSaved={showSavedView}
			onShowDigest={showDigest}
			onToggleTheme={toggleTheme}
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
