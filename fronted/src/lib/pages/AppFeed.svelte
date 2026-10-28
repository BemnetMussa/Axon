<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { api, feedCache, type Article, type Trend } from '$lib/api';
	import FeedPanel from '$lib/components/feed/FeedPanel.svelte';
	import DesktopSidebar from '$lib/components/navigation/DesktopSidebar.svelte';
	import MobileBottomNav from '$lib/components/navigation/MobileBottomNav.svelte';
	import ReaderPanel from '$lib/components/reader/ReaderPanel.svelte';
	import DigestView from '$lib/components/reader/DigestView.svelte';
	import { NAVIGATION, SUGGESTIONS } from '$lib/ui';
	import { analytics } from '$lib/analytics';
	import OnboardingOverlay from '$lib/components/onboarding/OnboardingOverlay.svelte';
	import NotificationPrompt from '$lib/components/ui/NotificationPrompt.svelte';
	import { pulseStore } from '$lib/pulse-store.svelte';
	import '$lib/app-shell.css';

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
	let activeCategory = $state<string | null>(null);
	let selectedArticle = $state<Article | null>(null);
	let showDigestView = $state(false);
	let digestContent = $state<{ content: string; created_at: string } | null>(null);
	let digestLoading = $state(false);
	let savedArticleIds = $state<number[]>([]);
	// Full saved stories from the server — Saved must not depend on which feed pages are loaded.
	let savedArticles = $state<Article[]>([]);
	let showSavedOnly = $state(false);
	let chatInput = $state('');
	let chatMessages = $state<ChatMessage[]>([]);
	let chatLoading = $state(false);
	let chatSuggestions = $state<string[]>([...SUGGESTIONS]);
	let suggestionsLoading = $state(false);
	let theme = $state<'dark' | 'light'>('dark');

	let nextCursor = $state<string | null>(null);
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

	let filtered = $derived.by(() => {
		if (semanticSearchResults && searchQuery.trim().length > 2) return semanticSearchResults;

		// The active tab is filtered server-side (see feedParams), so `allArticles`
		// already holds only that tab's articles; only the search box narrows it here.
		let list = showSavedOnly ? savedArticles : activeCategory === 'Trending' ? trendingArticles : allArticles;
		const q = searchQuery.trim().toLowerCase();
		if (q) {
			list = list.filter(
				(a) =>
					a.title.toLowerCase().includes(q) ||
					a.source.toLowerCase().includes(q) ||
					(a.content_snippet || '').toLowerCase().includes(q)
			);
		}
		return list;
	});
	let currentTitle = $derived(
		showSavedOnly ? 'Saved' : (NAVIGATION.find((n) => n.id === activeCategory)?.label ?? 'Frontier')
	);
	let dbEmpty = $derived(!loading && allArticles.length === 0 && !fetchError && activeCategory === null);

	function applyTheme(t: 'dark' | 'light') {
		theme = t;
		document.documentElement.classList.toggle('light', t === 'light');
		localStorage.setItem(THEME_KEY, t);
		// Keep the mobile browser chrome (status bar) in sync with the palette.
		document
			.querySelector('meta[name="theme-color"]')
			?.setAttribute('content', t === 'light' ? '#fafafa' : '#0a0a0a');
	}

	function toggleTheme() {
		applyTheme(theme === 'dark' ? 'light' : 'dark');
	}

	function sortNewestFirst(list: Article[]): Article[] {
		return [...list].sort((a, b) => b.published_date.localeCompare(a.published_date));
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
			savedArticles = sortNewestFirst(savedRes.articles);
			savedArticleIds = savedRes.articles.map(a => a.id);
		} catch {
			const saved = localStorage.getItem(SAVED_KEY);
			if (saved) savedArticleIds = JSON.parse(saved);
		}

		readArticleIds = loadReadIds();

		await loadDefaultFeed();

		startPolling();
	}

	// The active tab maps to backend filter params, so each tab is its own
	// server-paginated feed: "Load more" pulls the next page *of that tab*, not
	// the next page of the global feed. GitHub is a source filter; the other
	// category tabs filter by category; Frontier/Trending carry no filter.
	// `isDefaultFeed` gates the persistent cache + background polling, which only
	// apply to the unfiltered Frontier feed (the invariant: activeCategory === null
	// ⟺ allArticles holds the default feed).
	let isDefaultFeed = $derived(activeCategory === null);
	function feedParams(): { category: string | null; source: string | null } {
		if (activeCategory === 'GitHub') return { category: null, source: 'GitHub' };
		if (activeCategory && activeCategory !== 'Trending') return { category: activeCategory, source: null };
		return { category: null, source: null };
	}

	// Loads the Frontier feed — from cache when usable (instant), otherwise the
	// network. Used on first load and whenever we return to an unfiltered feed.
	async function loadDefaultFeed() {
		const cached = feedCache.get();
		if (cached && feedCache.isUsable()) {
			fetchError = null;
			allArticles = cached.articles;
			trends = cached.trends;
			nextCursor = cached.nextCursor;
			hasMore = cached.hasMore;
			loading = false;
			if (!feedCache.isFresh()) backgroundRevalidate();
		} else {
			await fetchFirstPage();
		}
	}

	// Loads page 1 of a filtered tab (category or source). No cache/poll — those
	// are reserved for the Frontier feed.
	async function loadCategoryFeed() {
		loading = true;
		syncIndicator = true;
		fetchError = null;
		allArticles = [];
		nextCursor = null;
		hasMore = false;
		pendingNewArticlesCount = 0;
		try {
			const res = await api.getArticles(null, undefined, feedParams());
			allArticles = res.articles;
			nextCursor = res.next_cursor;
			hasMore = res.has_more;
		} catch (error) {
			console.error('Fetch feed failed', error);
			fetchError = friendlyListError(error);
		} finally {
			loading = false;
			syncIndicator = false;
		}
	}

	// --- Single merge path: dedupe an incoming page against what's already
	// --- loaded, plus one place that writes the persistent feed cache so it
	// --- always stays consistent with the in-memory list. ---
	function dedupeNew(incoming: Article[]): Article[] {
		const have = new Set(allArticles.map((a) => a.id));
		return incoming.filter((a) => !have.has(a.id));
	}

	function saveFeedCache() {
		feedCache.set({ articles: allArticles, trends, nextCursor, hasMore });
	}

	async function fetchFirstPage(options?: { skipClearError?: boolean }) {
		syncIndicator = true;
		if (!options?.skipClearError) fetchError = null;
		try {
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);

			// Prepend instead of replace to avoid "disappearing" data
			const fresh = dedupeNew(articleRes.articles);
			if (fresh.length > 0) {
				allArticles = [...fresh, ...allArticles];
			} else if (allArticles.length === 0) {
				allArticles = articleRes.articles;
			}

			nextCursor = articleRes.next_cursor;
			hasMore = articleRes.has_more;
			trends = trendData;
			saveFeedCache();
		} catch (error) {
			console.error('Fetch failed', error);
			fetchError = friendlyListError(error);
		} finally {
			loading = false;
			syncIndicator = false;
		}
	}

	async function refreshNewArticles(): Promise<number> {
		// Fetches page 1 of the *current* tab and prepends any articles we don't
		// already have. Returns the count of new ones so the UI can show real
		// feedback, and lets errors propagate so a failed refresh shows an error
		// instead of a fake "up to date".
		const res = await api.getArticles(null, undefined, feedParams());
		const fresh = dedupeNew(res.articles);

		if (fresh.length > 0) {
			allArticles = [...fresh, ...allArticles];
			newArticleIds = new Set([...newArticleIds, ...fresh.map(a => a.id)]);
			if (isDefaultFeed) saveFeedCache();
		}
		return fresh.length;
	}

	async function backgroundRevalidate() {
		// Cache + background prepend are Frontier-only; filtered tabs fetch fresh.
		if (!isDefaultFeed) return;
		syncIndicator = true;
		try {
			const [articleRes, trendData] = await Promise.all([api.getArticles(), api.getTrends()]);

			const freshArticles = dedupeNew(articleRes.articles);

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
			saveFeedCache();
		} catch {
			// silent — user still has cached data
		} finally {
			syncIndicator = false;
		}
	}

	function startPolling() {
		if (pollTimer) return;
		pollTimer = setInterval(async () => {
			// Only poll the Frontier feed — filtered tabs aren't cached and the
			// new-signals bubble prepends into the default list.
			if (!isDefaultFeed) return;
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

	// Pause polling while the tab is backgrounded (saves battery/network); on
	// return, do an immediate freshness check before resuming the interval.
	function handleVisibility() {
		if (typeof document === 'undefined') return;
		if (document.hidden) {
			if (pollTimer) {
				clearInterval(pollTimer);
				pollTimer = null;
			}
		} else {
			checkForNew();
			startPolling();
		}
	}

	function scrollFeedToTop() {
		feedScrollArea?.scrollTo({ top: 0, behavior: 'smooth' });
		pendingNewArticlesCount = 0;
	}

	async function checkForNew(): Promise<boolean> {
		if (!isDefaultFeed) return false;
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
		selectedArticle = null;
		showSavedOnly = false;
		showDigestView = false;
		if (!changed) return;

		// Each tab is its own server-paginated feed; (re)load page 1 for it.
		if (id === 'Trending') await fetchTrendingPage();
		else if (id === null) await loadDefaultFeed();
		else await loadCategoryFeed();
		feedScrollArea?.scrollTo({ top: 0 });
	}

	async function showSavedView() {
		showSavedOnly = true;
		selectedArticle = null;
		showDigestView = false;
		feedScrollArea?.scrollTo({ top: 0 });
		try {
			// Saves made on another device show up without a reload.
			const res = await api.getSavedArticles();
			savedArticles = sortNewestFirst(res.articles);
			savedArticleIds = res.articles.map((a) => a.id);
			persistSaved();
		} catch {
			/* keep what we have */
		}
	}

	async function fetchTrendingPage() {
		loading = true;
		syncIndicator = true;
		fetchError = null;
		// Trending is a fixed top-N list, not paginated — clear any leftover cursor
		// so the "Load more" affordance doesn't appear or fire here.
		hasMore = false;
		nextCursor = null;
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
		const wasFiltered = activeCategory !== null;
		showDigestView = true;
		activeCategory = null;
		selectedArticle = null;
		showSavedOnly = false;
		// Keep the underlying feed = Frontier so closing the digest lands on it.
		if (wasFiltered) loadDefaultFeed();
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

	function findLoadedArticle(id: number): Article | undefined {
		if (selectedArticle?.id === id) return selectedArticle;
		return (
			allArticles.find((a) => a.id === id) ??
			trendingArticles.find((a) => a.id === id) ??
			semanticSearchResults?.find((a) => a.id === id)
		);
	}

	function applySaved(id: number, saved: boolean) {
		savedArticleIds = saved ? [...savedArticleIds, id] : savedArticleIds.filter((s) => s !== id);
		if (saved) {
			const article = findLoadedArticle(id);
			if (article && !savedArticles.some((a) => a.id === id)) savedArticles = [article, ...savedArticles];
		} else {
			savedArticles = savedArticles.filter((a) => a.id !== id);
		}
		persistSaved();
	}

	async function toggleSave(id: number) {
		const isCurrentlySaved = savedArticleIds.includes(id);
		applySaved(id, !isCurrentlySaved);

		try {
			await api.toggleSave(id);
		} catch (e) {
			console.error("Failed to sync save status to backend", e);
			flashNotice('Save failed to sync. Reverted.');
			applySaved(id, isCurrentlySaved);
		}
	}


	async function loadMore() {
		if (loadingMore || loadMoreLock || !hasMore || !nextCursor) return;
		loadingMore = true;
		loadMoreLock = true;
		try {
			// Paginate within the current tab — the cursor + filter together yield
			// the next page *of this tab*, not the next page of the global feed.
			const res = await api.getArticles(nextCursor, undefined, feedParams());
			const newOnes = dedupeNew(res.articles);
			allArticles = [...allArticles, ...newOnes];
			nextCursor = res.next_cursor;
			hasMore = res.has_more;
			if (isDefaultFeed) feedCache.appendPage(newOnes, res.next_cursor, res.has_more);
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

	// Keep teardown inside onMount's return — onDestroy also runs during SSR
	// close_render, where `document` does not exist and used to 500 /app on refresh.
	onMount(() => {
		document.body.classList.add('app-shell-lock');
		load();
		pulseStore.start();
		document.addEventListener('visibilitychange', handleVisibility);
		return () => {
			document.body.classList.remove('app-shell-lock');
			if (pollTimer) clearInterval(pollTimer);
			pulseStore.stop();
			document.removeEventListener('visibilitychange', handleVisibility);
		};
	});
</script>

<svelte:head>
	<title>AXON — {currentTitle}</title>
	<meta name="theme-color" content={theme === 'dark' ? '#0a0a0a' : '#fafafa'} />
</svelte:head>

<div class={`relative flex h-dvh overflow-hidden ${theme === 'dark' ? 'bg-[#0a0a0a] text-[#ededed]' : 'bg-[#fafafa] text-[#0a0a0a]'}`}>
	<div class="mx-auto flex h-full w-full max-w-[1600px] min-w-0 overflow-hidden">
	<DesktopSidebar
		navigation={NAVIGATION}
		{activeCategory}
		{showSavedOnly}
		{showDigestView}
		{trends}
		{theme}
		newSignalCount={newArticleIds.size}
		onNavigate={selectCategory}
		onShowSaved={showSavedView}
		onShowDigest={showDigest}
		onToggleTheme={toggleTheme}
		onTopicSearch={(kw) => { searchQuery = kw; }}
	/>

	<div class={`relative flex min-w-0 flex-1 overflow-hidden lg:border-r ${theme === 'dark' ? 'lg:border-white/10' : 'lg:border-black/10'}`}>
		<div class={`min-w-0 overflow-hidden ${selectedArticle || showDigestView ? 'hidden lg:flex lg:w-[340px] lg:shrink-0 xl:w-[400px]' : 'flex min-w-0 flex-1'}`}>
			<div class={`flex min-w-0 flex-1 flex-col overflow-hidden ${theme === 'dark' ? 'bg-[#0a0a0a]' : 'bg-[#fafafa]'}`}>
				{#if fetchError}
					<div class={`mx-3 mt-3 flex flex-col gap-2 border px-3 py-2.5 text-xs sm:flex-row sm:items-center sm:justify-between ${theme === 'dark' ? 'border-white/20 bg-white/[0.04] text-white/80' : 'border-black/20 bg-black/[0.03] text-black/80'}`}>
						<p class="min-w-0 flex-1 leading-relaxed">{fetchError}</p>
						<div class="flex shrink-0 gap-2">
							<button
								type="button"
								onclick={clearFetchError}
								class={`axon-label px-2.5 py-1.5 ${theme === 'dark' ? 'text-white/60 hover:text-white' : 'text-black/60 hover:text-black'}`}
							>Dismiss</button>
						</div>
					</div>
				{/if}
				{#if uiNotice}
					<div class={`mx-3 mt-3 border px-3 py-2 text-xs ${theme === 'dark' ? 'border-white/20 bg-white/[0.04] text-white/80' : 'border-black/20 bg-black/[0.03] text-black/80'}`}>
						{uiNotice}
					</div>
				{/if}
                
                {#if pendingNewArticlesCount > 0}
                    <div class="flex justify-center mt-3 absolute left-0 right-0 z-20 pointer-events-none">
                        <button
                            onclick={scrollFeedToTop}
                            class={`axon-label pointer-events-auto mt-24 flex items-center gap-2 px-4 py-2 shadow-xl transition-transform active:scale-95 lg:mt-36 ${theme === 'dark' ? 'bg-white text-black' : 'bg-black text-white'}`}
                        >
                            {pendingNewArticlesCount} new {pendingNewArticlesCount === 1 ? 'story' : 'stories'} kept · show
                        </button>
                    </div>
                {/if}
				<FeedPanel
					title={currentTitle}
					articles={filtered}
					{dbEmpty}
					{searchQuery}
					{theme}
					hasMore={hasMore && !showSavedOnly && !semanticSearchActive}
					{loadingMore}
					selectedArticleId={selectedArticle?.id ?? null}
					{savedArticleIds}
					{readArticleIds}
					{loading}
					{syncIndicator}
					{newArticleIds}
					tabs={NAVIGATION}
					activeTab={activeCategory}
					{showSavedOnly}
					{semanticSearchActive}
					onTabSelect={selectCategory}
					onSearchChange={(value) => (searchQuery = value)}
					onArticleOpen={openArticle}
					onToggleSave={toggleSave}
					onLoadMore={loadMore}
					onRefresh={refreshNewArticles}
					bind:scrollArea={feedScrollArea}
				/>
			</div>
		</div>

		{#if selectedArticle || showDigestView}
			<div transition:fly={{ x: 50, duration: 400, easing: quintOut }} class={`absolute inset-0 z-30 flex overflow-hidden lg:relative lg:z-auto lg:w-0 lg:flex-1 lg:border-l ${theme === 'dark' ? 'bg-[#0a0a0a] lg:border-white/10' : 'bg-white lg:border-black/10'}`}>
				{#if showDigestView}
					<DigestView
						digest={digestContent}
						loading={digestLoading}
						{theme}
						onBack={() => (showDigestView = false)}
						onGenerate={generateDigest}
					/>
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

	<NotificationPrompt {theme} suppressed={showOnboarding || !!selectedArticle} />

	{#if !selectedArticle}
		<MobileBottomNav
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
