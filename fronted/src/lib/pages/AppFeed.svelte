<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { renderMarkdown } from '$lib/markdown';
	import { fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { api, feedCache, type Article, type Trend } from '$lib/api';
	import FeedPanel from '$lib/components/feed/FeedPanel.svelte';
	import DesktopSidebar from '$lib/components/navigation/DesktopSidebar.svelte';
	import MobileBottomNav from '$lib/components/navigation/MobileBottomNav.svelte';
	import ReaderPanel from '$lib/components/reader/ReaderPanel.svelte';
	import { NAVIGATION, SECONDARY_CATEGORIES, SUGGESTIONS } from '$lib/ui';
	import { analytics } from '$lib/analytics';
	import OnboardingOverlay from '$lib/components/onboarding/OnboardingOverlay.svelte';
	import SignalLoader from '$lib/components/ui/SignalLoader.svelte';

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

		// The active category/GitHub tab is filtered server-side (see feedParams),
		// so `allArticles` already holds only that tab's articles. Here we apply
		// the lighter, client-side refinements layered on top of the loaded set.
		let list = allArticles;
		if (showSavedOnly) list = list.filter((a) => savedIdSet.has(a.id));
		if (activeSource) list = list.filter((a) => a.source === activeSource);
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
		// Keep the mobile browser chrome (status bar) in sync with the palette.
		document
			.querySelector('meta[name="theme-color"]')
			?.setAttribute('content', t === 'light' ? '#ffffff' : '#0b0b0b');
	}

	function toggleTheme(event?: MouseEvent) {
		const nextTheme = theme === 'dark' ? 'light' : 'dark';

		// Calm theme switch: the new palette is revealed with a quick circular wipe
		// growing from the toggle control via the View-Transitions API (snapshot →
		// flip palette → GPU-composite the new UI under an animated clip-path), so
		// there's no flash and no per-element transition cost. Reduced-motion /
		// unsupported browsers get an instant switch.
		const startViewTransition = (
			document as Document & {
				startViewTransition?: (
					cb: () => Promise<void> | void
				) => { ready: Promise<void>; finished: Promise<void> };
			}
		).startViewTransition?.bind(document);
		const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

		if (reduce || !startViewTransition) {
			applyTheme(nextTheme);
			return;
		}

		// Origin: the cursor for a real click, the control's centre for keyboard
		// activation (which reports 0,0), otherwise the viewport centre.
		let originX = window.innerWidth / 2;
		let originY = window.innerHeight / 2;
		if (event?.clientX || event?.clientY) {
			originX = event.clientX;
			originY = event.clientY;
		} else if (event?.currentTarget instanceof Element) {
			const rect = event.currentTarget.getBoundingClientRect();
			originX = rect.left + rect.width / 2;
			originY = rect.top + rect.height / 2;
		}

		// Final radius = distance to the farthest corner, so the circle always fills.
		const maxRadius = Math.hypot(
			Math.max(originX, window.innerWidth - originX),
			Math.max(originY, window.innerHeight - originY)
		);

		const transition = startViewTransition(() => {
			applyTheme(nextTheme);
		});

		transition.ready
			.then(() => {
				document.documentElement.animate(
					{
						clipPath: [
							`circle(0px at ${originX}px ${originY}px)`,
							`circle(${maxRadius}px at ${originX}px ${originY}px)`
						]
					},
					{ duration: 420, easing: 'ease-in-out', pseudoElement: '::view-transition-new(root)' }
				);
			})
			.catch(() => {});
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
		if (changed) activeSource = null;
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
		// Saved filters over the broad feed, so make sure the default feed is loaded
		// when arriving from a narrow tab.
		const wasFiltered = activeCategory !== null;
		showSavedOnly = true;
		activeCategory = null;
		activeSource = null;
		selectedArticle = null;
		showDigestView = false;
		if (wasFiltered) await loadDefaultFeed();
	}

	function selectSource(source: string | null) {
		activeSource = source;
	}

	async function clearCategoryOrSaved() {
		const wasFiltered = activeCategory !== null;
		showSavedOnly = false;
		activeCategory = null;
		if (wasFiltered) await loadDefaultFeed();
	}

	async function clearAllFilters() {
		const wasFiltered = activeCategory !== null;
		searchQuery = '';
		activeSource = null;
		activeCategory = null;
		showSavedOnly = false;
		sortBy = 'date';
		timeFilter = 'all';
		if (wasFiltered) await loadDefaultFeed();
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
		activeSource = null;
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

	onMount(() => {
		load();
		document.addEventListener('visibilitychange', handleVisibility);
	});
	onDestroy(() => {
		if (pollTimer) clearInterval(pollTimer);
		document.removeEventListener('visibilitychange', handleVisibility);
	});
</script>

<svelte:head>
	<title>AXON — Intelligence Platform</title>
	<meta name="theme-color" content={theme === 'dark' ? '#0b0b0b' : '#ffffff'} />
</svelte:head>

<div class={`relative flex h-screen overflow-hidden ${theme === 'dark' ? 'bg-[#070707] text-[#e4e4e7]' : 'bg-[#f8fafc] text-zinc-900'}`}>
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
					secondaryCategories={SECONDARY_CATEGORIES}
					onCategorySelect={selectCategory}
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
									<SignalLoader size={22} class={theme === 'dark' ? 'text-zinc-400' : 'text-zinc-500'} />
									<p class={`text-[12px] font-semibold ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>Loading digest…</p>
								</div>
							{:else if digestContent}
								<h1 class={`mb-2 text-2xl font-bold sm:text-4xl ${theme === 'dark' ? 'text-white' : 'text-black'}`}>Weekly Digest</h1>
								<p class={`mb-10 text-[12px] sm:text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
									Synthesized {digestContent.created_at ? new Date(digestContent.created_at).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : 'recently'}
								</p>

								<div class={`prose max-w-none text-[14px] leading-[1.8] sm:text-[16px] ${theme === 'dark' ? 'prose-invert prose-p:text-[#d4d4d8] prose-headings:text-white' : 'prose-p:text-zinc-700 prose-headings:text-black'}`}>
									{@html renderMarkdown(digestContent.content)}
								</div>

								<div class={`mt-10 flex items-center gap-3 border-t pt-6 ${theme === 'dark' ? 'border-white/[0.06]' : 'border-zinc-100'}`}>
									<button
										onclick={generateDigest}
										disabled={digestLoading}
										class={`inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-[13px] font-bold shadow-md transition-all disabled:opacity-60 ${theme === 'dark' ? 'bg-white text-black hover:bg-zinc-200' : 'bg-zinc-900 text-white hover:bg-zinc-700'}`}
									>
										{#if digestLoading}
											<SignalLoader size={14} />
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
	/* Theme toggle uses the View Transitions API (see toggleTheme): the new palette
	   is revealed by a circular clip-path (animated in JS) growing from the toggle
	   control. We disable the default opacity cross-fade so the clip wipe is the only
	   motion, and keep the new snapshot stacked above the old one so the growing
	   circle paints over the previous palette. No-op without the API (instant). */
	:global(::view-transition-old(root)),
	:global(::view-transition-new(root)) {
		animation: none;
		mix-blend-mode: normal;
	}
	:global(::view-transition-old(root)) {
		z-index: 0;
	}
	:global(::view-transition-new(root)) {
		z-index: 1;
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
