<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { marked } from 'marked';
	import { fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { api, feedCache, type Article, type Trend } from '$lib/api';
	import FeedPanel from '$lib/components/feed/FeedPanel.svelte';
	import DesktopSidebar from '$lib/components/navigation/DesktopSidebar.svelte';
	import MobileBottomNav from '$lib/components/navigation/MobileBottomNav.svelte';
	import ReaderPanel from '$lib/components/reader/ReaderPanel.svelte';
	import { NAVIGATION, SUGGESTIONS } from '$lib/ui';
	import { analytics } from '$lib/analytics';
	import OnboardingOverlay from '$lib/components/onboarding/OnboardingOverlay.svelte';

	type ChatMessage = {
		role: 'user' | 'ai';
		content: string;
	};

	let allArticles = $state<Article[]>([]);
	let trendingArticles = $state<Article[]>([]);
	let trends = $state<Trend[]>([]);
	let loading = $state(true);
	let fetchError = $state<string | null>(null);
	let syncIndicator = $state(false);
	let searchQuery = $state('');
	let activeSource = $state<string | null>(null);
	let activeCategory = $state<string | null>(null);
	let selectedArticle = $state<Article | null>(null);
	let showDigestView = $state(false);
	let digestContent = $state<{ content: string; created_at: string } | null>(null);
	let digestLoading = $state(false);
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
	let loadMoreLock = $state(false);
	let newArticleIds = $state<Set<number>>(new Set());
	let readArticleIds = $state<Set<number>>(new Set());
	let feedScrollArea = $state<HTMLDivElement | undefined>();
    let pendingNewArticlesCount = $state(0);

	const SAVED_KEY = 'axon_saved_signals';
	const SEEN_KEY = 'axon_seen_articles';
	const READ_KEY = 'axon_read_articles';
	const THEME_KEY = 'axon_theme';
	const ONBOARDED_KEY = 'axon_onboarded';

	let showOnboarding = $state(false);
	const POLL_INTERVAL_MS = 60_000;

	let pollTimer: ReturnType<typeof setInterval> | null = null;

	let sources = $derived([...new Set(allArticles.map((a) => a.source))].sort());
	let sourceCounts = $derived.by(() => {
		const counts: Record<string, number> = {};
		// Using allArticles ensuring we count from the full session set
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
	let uiNotice = $state<string | null>(null);
	let semanticSearchActive = $derived(searchQuery.trim().length > 2);

	function flashNotice(message: string) {
		uiNotice = message;
		setTimeout(() => {
			if (uiNotice === message) uiNotice = null;
		}, 2500);
	}

	function friendlyIngestError(error: unknown): string {
		const msg = error instanceof Error ? error.message : String(error);
		if (/\bAPI 429\b/.test(msg)) {
			return 'You’re syncing too often. Wait about a minute, then try again.';
		}
		return 'Couldn’t fetch new articles from the web. Your feed below shows what’s already saved — try again shortly.';
	}

	function friendlyListError(error: unknown): string {
		const msg = error instanceof Error ? error.message : String(error);
		if (/\bAPI 429\b/.test(msg)) {
			return 'Too many requests. Wait a minute and try again.';
		}
		return 'Couldn’t refresh the feed from the server. Check your connection and try again.';
	}

	function clearFetchError() {
		fetchError = null;
	}

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

	let savedIdSet = $derived(new Set(savedArticleIds));

	let filtered = $derived.by(() => {
		if (semanticSearchResults && searchQuery.trim().length > 2) return semanticSearchResults;
		if (activeCategory === 'Trending' && !showSavedOnly) return trendingArticles;

		let list = allArticles;
		if (showSavedOnly) list = list.filter((a) => savedIdSet.has(a.id));
		if (activeSource) list = list.filter((a) => a.source === activeSource);
		if (activeCategory && activeCategory !== 'Trending') {
			if (activeCategory === 'GitHub') list = list.filter((a) => a.source === 'GitHub');
			else list = list.filter((a) => a.category === activeCategory);
		}
		if (timeFilter !== 'all') {
			const now = Date.now();
			const cutoff =
				timeFilter === 'today'
					? now - 86_400_000
					: timeFilter === 'week'
						? now - 7 * 86_400_000
						: now - 30 * 86_400_000;
			list = list.filter((a) => parseDate(a.published_date) >= cutoff);
		}
		const q = searchQuery.trim().toLowerCase();
		if (q) {
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
	let dbEmpty = $derived(!loading && allArticles.length === 0 && !fetchError);
	let hasActiveFilters = $derived(
		!!searchQuery.trim() ||
		!!activeSource ||
		!!activeCategory ||
		showSavedOnly ||
		timeFilter !== 'all' ||
		sortBy !== 'date'
	);

	function applyTheme(t: 'dark' | 'light') {
		theme = t;
		document.documentElement.classList.toggle('light', t === 'light');
		localStorage.setItem(THEME_KEY, t);
	}

	function toggleTheme(e: MouseEvent) {
		const nextTheme = theme === 'dark' ? 'light' : 'dark';

		// Respect reduced-motion — instant switch, no overlay
		if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
			applyTheme(nextTheme);
			return;
		}

		const el = e.currentTarget as HTMLElement;
		const rect = el.getBoundingClientRect();
		const ox = rect.left + rect.width / 2;
		const oy = rect.top + rect.height / 2;

		// Radius just large enough to cover every viewport corner from the origin
		const maxR =
			Math.ceil(
				Math.hypot(
					Math.max(ox, window.innerWidth - ox),
					Math.max(oy, window.innerHeight - oy)
				)
			) + 10;

		// Overlay in the NEW theme's color — starts at size 0 and grows to cover the page.
		// This is a "growing iris" reveal.
		const nextBg = nextTheme === 'dark' ? '#0b0b0b' : '#ffffff';
		const overlay = document.createElement('div');
		overlay.style.cssText = [
			'position:fixed',
			`top:${oy}px`,
			`left:${ox}px`,
			`width:${maxR * 2}px`,
			`height:${maxR * 2}px`,
			'border-radius:50%',
			'transform:translate(-50%,-50%) scale(0)',
			`background:${nextBg}`,
			'z-index:99999',
			'pointer-events:none',
			'will-change:transform',
		].join(';');
		document.body.appendChild(overlay);

		// Force a reflow so the browser acknowledges the starting state (scale: 0)
		overlay.getBoundingClientRect();

		// Wait for next frame to start growth
		requestAnimationFrame(() => {
			overlay.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
			overlay.style.transform = 'translate(-50%,-50%) scale(1)';
			
			// Fallback timeout in case transitionend fails to fire
			let fired = false;
			const cleanup = () => {
				if (fired) return;
				fired = true;
				applyTheme(nextTheme);
				overlay.remove();
			};
			
			overlay.addEventListener('transitionend', cleanup, { once: true });
			setTimeout(cleanup, 550); // Fallback exactly when transition should end
		});
	}

	function finishOnboarding() {
		showOnboarding = false;
		localStorage.setItem(ONBOARDED_KEY, '1');
	}

	async function load() {
		const savedTheme = localStorage.getItem(THEME_KEY) as 'dark' | 'light' | null;
		if (savedTheme) applyTheme(savedTheme);

		if (!localStorage.getItem(ONBOARDED_KEY)) {
			showOnboarding = true;
		}

		try {
			const savedRes = await api.getSavedArticles();
			savedArticleIds = savedRes.articles.map(a => a.id);
		} catch {
			const saved = localStorage.getItem(SAVED_KEY);
			if (saved) savedArticleIds = JSON.parse(saved);
		}

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

	async function fetchFirstPage(options?: { skipClearError?: boolean }) {
		syncIndicator = true;
		if (!options?.skipClearError) fetchError = null;
		try {
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);
			
			// Prepend instead of replace to avoid "disappearing" data
			const existingIds = new Set(allArticles.map(a => a.id));
			const fresh = articleRes.articles.filter(a => !existingIds.has(a.id));
			
			if (fresh.length > 0) {
				allArticles = [...fresh, ...allArticles];
			} else if (allArticles.length === 0) {
				allArticles = articleRes.articles;
			}
			
			nextCursor = articleRes.next_cursor;
			hasMore = articleRes.has_more;
			trends = trendData;
			feedCache.set({ articles: allArticles, trends, nextCursor, hasMore });
		} catch (error) {
			console.error('Fetch failed', error);
			fetchError = friendlyListError(error);
		} finally {
			loading = false;
			syncIndicator = false;
		}
	}

	async function refreshNewArticles() {
		// Lightweight fetch that only prepends new articles to the top
		try {
			const res = await api.getArticles();
			const existingIds = new Set(allArticles.map((a) => a.id));
			const fresh = res.articles.filter((a) => !existingIds.has(a.id));

			if (fresh.length > 0) {
				// Prepend to top - no full refresh, just adds new ones
				allArticles = [...fresh, ...allArticles];
				newArticleIds = new Set([...newArticleIds, ...fresh.map(a => a.id)]);
				feedCache.set({ articles: allArticles, trends, nextCursor, hasMore });
			}
		} catch {
			// New-article fetch is best-effort; ignore failures
		}
	}

	async function backgroundRevalidate() {
		syncIndicator = true;
		try {
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);

			const existingIds = new Set(allArticles.map((a) => a.id));
			const freshArticles = articleRes.articles.filter((a) => !existingIds.has(a.id));

			if (freshArticles.length > 0) {
				const isAtTop = feedScrollArea ? feedScrollArea.scrollTop < 20 : true;
				
				if (isAtTop) {
					allArticles = [...freshArticles, ...allArticles];
					pendingNewArticlesCount = 0;
					newArticleIds = new Set([...newArticleIds, ...freshArticles.map(a => a.id)]);
				} else {
					pendingNewArticlesCount += freshArticles.length;
					// Add them to the array so they are there, but we'll show the bubble
					allArticles = [...freshArticles, ...allArticles];
				}
			}

			trends = trendData;
			feedCache.set({ articles: allArticles, trends, nextCursor, hasMore });
		} catch {
			// silent — user still has cached data
		} finally {
			syncIndicator = false;
		}
	}

	function startPolling() {
		pollTimer = setInterval(async () => {
			const latestId = feedCache.latestId();
			if (!latestId) return;
			try {
				const count = await api.countNewSince(latestId);
				if (count > 0) {
					// Check if we should auto-insert based on scroll
					const isAtTop = feedScrollArea ? feedScrollArea.scrollTop < 20 : true;
					if (isAtTop) {
						await backgroundRevalidate();
					} else {
						pendingNewArticlesCount = count;
					}
				}
			} catch {
				/* silent */
			}
		}, POLL_INTERVAL_MS);
	}

	function scrollFeedToTop() {
		feedScrollArea?.scrollTo({ top: 0, behavior: 'smooth' });
		pendingNewArticlesCount = 0;
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
		} catch {
			return new Set();
		}
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
		} catch {
			return new Set();
		}
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

	async function selectCategory(id: string | null) {
		const changed = activeCategory !== id || showSavedOnly || showDigestView;
		activeCategory = id;
		if (changed) activeSource = null;
		selectedArticle = null;
		showSavedOnly = false;
		showDigestView = false;

		if (id === 'Trending') {
			await fetchTrendingPage();
		}
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

	function clearCategoryOrSaved() {
		showSavedOnly = false;
		activeCategory = null;
	}

	function clearAllFilters() {
		searchQuery = '';
		activeSource = null;
		activeCategory = null;
		showSavedOnly = false;
		sortBy = 'date';
		timeFilter = 'all';
	}

	async function fetchTrendingPage() {
		loading = true;
		syncIndicator = true;
		fetchError = null;
		try {
			const res = await api.getTrending();
			trendingArticles = res.articles;
		} catch (error) {
			console.error('Fetch trending failed', error);
			fetchError = friendlyListError(error);
		} finally {
			loading = false;
			syncIndicator = false;
		}
	}

	async function showDigest() {
		analytics.digestOpened();
		showDigestView = true;
		activeCategory = null;
		activeSource = null;
		selectedArticle = null;
		showSavedOnly = false;
		if (!digestContent) {
			digestLoading = true;
			try {
				digestContent = await api.getLatestDigest();
			} catch (e) {
				console.error(e);
				digestContent = { content: 'No weekly digest available yet.', created_at: new Date().toISOString() };
			} finally {
				digestLoading = false;
			}
		}

	}

	async function generateDigest() {
		if (!digestContent || digestLoading) return;
		digestLoading = true;
		digestContent = { ...digestContent, content: 'Generating new Weekly Synthesis. Please wait roughly 10 seconds...' };
		try {
			const data = await api.generateDigest();
			if (data.status === 'success') {
				const fresh = await api.getLatestDigest();
				if (fresh) digestContent = fresh;
			} else {
				digestContent = { ...digestContent, content: data.detail || 'Unable to generate digest right now.' };
			}
		} catch (e) {
			console.error(e);
			digestContent = { ...digestContent, content: 'Failed to generate. Please check server logs.' };
		} finally {
			digestLoading = false;
		}
	}

	async function toggleSave(id: number) {
		const isCurrentlySaved = savedArticleIds.includes(id);
		savedArticleIds = isCurrentlySaved
			? savedArticleIds.filter((s) => s !== id)
			: [...savedArticleIds, id];
		persistSaved();
		
		try {
			await api.toggleSave(id);
		} catch (e) {
			console.error("Failed to sync save status to backend", e);
			flashNotice('Save failed to sync. Reverted.');
			savedArticleIds = isCurrentlySaved
				? [...savedArticleIds, id]
				: savedArticleIds.filter((s) => s !== id);
			persistSaved();
		}
	}


	async function loadMore() {
		if (loadingMore || loadMoreLock || !hasMore || !nextCursor) return;
		loadingMore = true;
		loadMoreLock = true;
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
			setTimeout(() => {
				loadMoreLock = false;
			}, 350);
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
		analytics.articleOpened(article.id, article.source, article.category);
	}

	function openArticleWithChat(article: Article, starterQuestion: string) {
		openArticle(article);
		// Pre-fill and immediately send the starter question so the user lands in an active chat
		chatInput = starterQuestion;
		// Small delay so the reader panel + suggestions have time to mount before the send
		setTimeout(() => sendChat(starterQuestion), 80);
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
	onDestroy(() => {
		if (pollTimer) clearInterval(pollTimer);
	});
</script>

<svelte:head>
	<title>AXON — Intelligence Platform</title>
	<meta name="theme-color" content={theme === 'dark' ? '#0b0b0b' : '#ffffff'} />
</svelte:head>

<div class={`relative flex h-screen overflow-hidden transition-colors duration-300 ${theme === 'dark' ? 'bg-[#070707] text-[#e4e4e7]' : 'bg-[#f8fafc] text-zinc-900'}`}>
	<div class={`app-bg pointer-events-none absolute inset-0 ${theme === 'dark' ? 'bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.045),transparent_42%)]' : 'bg-[radial-gradient(circle_at_top,rgba(15,23,42,0.06),transparent_45%)]'}`}></div>
	<div class="mx-auto flex h-full w-full max-w-[1500px] min-w-0 overflow-hidden px-0 lg:px-4">
	<DesktopSidebar
		navigation={NAVIGATION}
		{activeCategory}
		{showSavedOnly}
		{showDigestView}
		{sourceCounts}
		{trends}
		{theme}
		newSignalCount={newArticleIds.size}
		onNavigate={selectCategory}
		onShowSaved={showSavedView}
		onShowDigest={showDigest}
		onToggleTheme={toggleTheme}
		onTopicSearch={(kw) => { searchQuery = kw; }}
	/>

	<div class="relative flex min-w-0 flex-1 overflow-hidden lg:rounded-2xl lg:border lg:border-white/5">
		<div class={`min-w-0 overflow-hidden ${selectedArticle || showDigestView ? 'hidden lg:flex lg:w-[340px] lg:shrink-0 xl:w-[400px]' : 'flex min-w-0 flex-1'}`}>
			<div class={`flex min-w-0 flex-1 flex-col overflow-hidden ${theme === 'dark' ? 'bg-[#0b0b0b]' : 'bg-white'}`}>
				{#if fetchError}
					<div class={`mx-3 mt-3 flex flex-col gap-2 rounded-xl border px-3 py-2.5 text-xs sm:flex-row sm:items-center sm:justify-between ${theme === 'dark' ? 'border-amber-400/35 bg-amber-500/10 text-amber-100' : 'border-amber-200 bg-amber-50 text-amber-950'}`}>
						<p class="min-w-0 flex-1 leading-relaxed">{fetchError}</p>
						<div class="flex shrink-0 gap-2">
							<button
								type="button"
								onclick={clearFetchError}
								class={`rounded-lg px-2.5 py-1.5 text-[11px] font-semibold ${theme === 'dark' ? 'text-amber-200/80 hover:text-white' : 'text-amber-900/80 hover:text-amber-950'}`}
							>Dismiss</button>
						</div>
					</div>
				{/if}
				{#if uiNotice}
					<div class={`mx-3 mt-3 rounded-xl border px-3 py-2 text-xs ${theme === 'dark' ? 'border-amber-400/40 bg-amber-500/10 text-amber-200' : 'border-amber-200 bg-amber-50 text-amber-700'}`}>
						{uiNotice}
					</div>
				{/if}
                
                {#if pendingNewArticlesCount > 0}
                    <div class="flex justify-center mt-3 absolute left-0 right-0 z-20 pointer-events-none">
                        <button
                            onclick={scrollFeedToTop}
                            class={`pointer-events-auto flex items-center gap-2 rounded-full border px-4 py-1.5 text-[11px] font-bold shadow-xl transition-all hover:scale-105 active:scale-95 ${theme === 'dark' ? 'bg-white text-black border-white' : 'bg-zinc-900 border-zinc-700 text-white shadow-black/20'}`}
                        >
                            <span class="relative flex h-2 w-2">
                                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                <span class="relative inline-flex h-2 w-2 rounded-full bg-blue-500"></span>
                            </span>
                            {pendingNewArticlesCount} new signals detection
                        </button>
                    </div>
                {/if}
				<FeedPanel
					title={currentTitle}
					articles={filtered}
					{dbEmpty}
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
					{activeCategory}
					{showSavedOnly}
					{semanticSearchActive}
					onSearchChange={(value) => (searchQuery = value)}
					onSourceSelect={selectSource}
					onSortChange={(value) => (sortBy = value)}
					onTimeFilterChange={(value) => (timeFilter = value)}
					onClearCategoryOrSaved={clearCategoryOrSaved}
					onClearAllFilters={clearAllFilters}
				onArticleOpen={openArticle}
				onArticleOpenWithChat={openArticleWithChat}
				onToggleSave={toggleSave}
					onShowDigest={showDigest}
					onLoadMore={loadMore}
					onRefresh={refreshNewArticles}
					bind:scrollArea={feedScrollArea}
				/>
			</div>
		</div>

		{#if selectedArticle || showDigestView}
			<div transition:fly={{ x: 50, duration: 400, easing: quintOut }} class={`absolute inset-0 z-30 flex overflow-hidden lg:relative lg:z-auto lg:w-0 lg:flex-1 lg:border-l ${theme === 'dark' ? 'bg-[#0a0a0a] lg:border-white/[0.04]' : 'bg-white lg:border-zinc-200'}`}>
				{#if showDigestView}
					<div class="flex h-full w-full flex-col overflow-y-auto pb-24 lg:pb-0">
						<!-- sticky back header on mobile -->
						<div class={`sticky top-0 z-10 flex items-center gap-3 border-b px-4 py-3 sm:px-6 ${theme === 'dark' ? 'border-white/[0.05] bg-[#0a0a0a]' : 'border-zinc-100 bg-white'}`}>
							<button
								onclick={() => (showDigestView = false)}
								class={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border transition-all sm:h-8 sm:w-8 sm:rounded-md ${theme === 'dark' ? 'border-white/[0.06] text-zinc-400 hover:bg-white/[0.06] hover:text-zinc-200' : 'border-zinc-200 text-zinc-500 hover:bg-zinc-50 hover:text-zinc-700'}`}
								aria-label="Back to feed"
							>
								←
							</button>
							<span class={`text-[13px] font-semibold ${theme === 'dark' ? 'text-zinc-300' : 'text-zinc-700'}`}>Weekly Digest</span>
						</div>

						<div class="mx-auto w-full max-w-3xl px-5 pt-8 pb-12 sm:px-10 sm:pt-12">
							{#if digestLoading && !digestContent}
								<div class="flex flex-col items-center justify-center py-24 gap-3">
									<div class="h-5 w-5 animate-spin rounded-full border-2 border-zinc-600 border-t-transparent"></div>
									<p class={`text-[12px] font-semibold ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>Loading digest…</p>
								</div>
							{:else if digestContent}
								<h1 class={`mb-2 text-2xl font-bold sm:text-4xl ${theme === 'dark' ? 'text-white' : 'text-black'}`}>Weekly Digest</h1>
								<p class={`mb-10 text-[12px] sm:text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
									Synthesized {digestContent.created_at ? new Date(digestContent.created_at).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : 'recently'}
								</p>

								<div class={`prose max-w-none text-[14px] leading-[1.8] sm:text-[16px] ${theme === 'dark' ? 'prose-invert prose-p:text-[#d4d4d8] prose-headings:text-white' : 'prose-p:text-zinc-700 prose-headings:text-black'}`}>
									{@html marked.parse(digestContent.content || '')}
								</div>

								<div class={`mt-10 flex items-center gap-3 border-t pt-6 ${theme === 'dark' ? 'border-white/[0.06]' : 'border-zinc-100'}`}>
									<button
										onclick={generateDigest}
										disabled={digestLoading}
										class={`inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-[13px] font-bold shadow-md transition-all disabled:opacity-60 ${theme === 'dark' ? 'bg-white text-black hover:bg-zinc-200' : 'bg-zinc-900 text-white hover:bg-zinc-700'}`}
									>
										{#if digestLoading}
											<div class="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
											Generating…
										{:else if digestContent.content.includes('No weekly digest available')}
											Generate first digest
										{:else}
											Regenerate digest
										{/if}
									</button>
									<span class={`text-[11px] ${theme === 'dark' ? 'text-zinc-600' : 'text-zinc-400'}`}>Takes ~10 seconds</span>
								</div>
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

	{#if showOnboarding}
		<OnboardingOverlay {theme} onDone={finishOnboarding} />
	{/if}

	{#if !selectedArticle}
		<MobileBottomNav
			items={NAVIGATION}
			{activeCategory}
			{showSavedOnly}
			{showDigestView}
			{theme}
			onNavigate={selectCategory}
			onShowSaved={showSavedView}
			onShowDigest={showDigest}
			onToggleTheme={toggleTheme}
		/>
	{/if}
	</div>
</div>

<style>
	:global(body) {
		overflow: hidden;
	}
	:global(html) {
		background: #0b0b0b;
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
	/* backdrop-filter removed: it re-blurred the whole feed/reader region on
	   every scroll frame (and was nested under blurred sticky headers), which
	   was the main source of scroll jank. Panels now use near-solid backgrounds
	   that look the same but cost nothing to composite. */
</style>
