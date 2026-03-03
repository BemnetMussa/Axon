<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Article, type Trend } from '../lib/api';
	import { RefreshCw, ExternalLink, Bot, Zap, Search, ChevronRight, X, SlidersHorizontal } from 'lucide-svelte';
	import DeepBriefModal from '$lib/components/DeepBriefModal.svelte';

	// ── State ────────────────────────────────────────────────
	let allArticles = $state<Article[]>([]);
	let trends = $state<Trend[]>([]);
	let loading = $state(true);
	let syncing = $state(false);
	let searchQuery = $state('');
	let activeSource = $state<string | null>(null);
	let activeCategory = $state<string | null>(null);
	let lastSynced = $state<string | null>(null);

	// Brief
	let briefOpen = $state(false);
	let briefLoading = $state(false);
	let briefTitle = $state('');
	let briefData = $state<string | null>(null);

	// ── Derived ──────────────────────────────────────────────
	let sources = $derived([...new Set(allArticles.map(a => a.source))].sort());
	// Category names matching backend vision
	const categories = ['AI', 'Signal', 'Momentum', 'Concerns'];

	let filtered = $derived.by(() => {
		let list = allArticles;
		if (activeSource) list = list.filter(a => a.source === activeSource);
		if (activeCategory) list = list.filter(a => a.category === activeCategory);
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(a =>
				a.title.toLowerCase().includes(q) ||
				a.source.toLowerCase().includes(q) ||
				(a.content_snippet || '').toLowerCase().includes(q)
			);
		}
		return list;
	});

	const activeFilters = $derived(
		(activeSource ? 1 : 0) + (activeCategory ? 1 : 0) + (searchQuery ? 1 : 0)
	);

	// ── Helpers ──────────────────────────────────────────────
	function stripHtml(s: string): string {
		return (s ?? '').replace(/<[^>]*>/g, '').replace(/&[a-z#0-9]+;/gi, ' ').replace(/\s+/g, ' ').trim();
	}

	function relativeTime(dateStr: string): string {
		if (!dateStr) return '';
		const diff = Date.now() - new Date(dateStr).getTime();
		const h = Math.floor(diff / 3_600_000);
		if (h < 1) return `${Math.floor(diff / 60_000)}m`;
		if (h < 24) return `${h}h`;
		return `${Math.floor(h / 24)}d`;
	}

	const CAT_STYLE: Record<string, string> = {
		AI: 'text-violet-400 bg-violet-400/10 border-violet-400/25',
		Signal: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/25',
		Momentum: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/25',
		Concerns: 'text-amber-400 bg-amber-400/10 border-amber-400/25',
		// Legacy support for old data
		Breakthrough: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/25',
		Project: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/25',
		Problem: 'text-amber-400 bg-amber-400/10 border-amber-400/25',
	};
	const CAT_BAR: Record<string, string> = {
		AI: 'bg-violet-500',
		Signal: 'bg-cyan-500',
		Momentum: 'bg-emerald-500',
		Concerns: 'bg-amber-500',
		// Legacy
		Breakthrough: 'bg-cyan-500',
		Project: 'bg-emerald-500',
		Problem: 'bg-amber-500',
	};
	function catStyle(c: string) { return CAT_STYLE[c] ?? 'text-zinc-400 bg-zinc-400/10 border-zinc-400/25'; }
	function catBar(c: string) { return CAT_BAR[c] ?? 'bg-zinc-500'; }

	const SOURCE_INITIALS: Record<string, string> = {
		HackerNews: 'HN', ArXiv: 'AX', GitHub: 'GH', Reddit: 'RD',
		OpenAI: 'OA', DeepMind: 'DM', Karpathy: 'KP', NVIDIA: 'NV',
		SimonW: 'SW', Lobsters: 'LB',
	};
	function sourceInitial(s: string) {
		return SOURCE_INITIALS[s] ?? s.slice(0, 2).toUpperCase();
	}

	function clearFilters() {
		activeSource = null;
		activeCategory = null;
		searchQuery = '';
	}

	// ── API ──────────────────────────────────────────────────
	const CACHE_KEY = 'axon_articles_cache';
	const CACHE_TTL = 15 * 60 * 1000; // 15 minutes

	function saveToCache(articles: Article[], trendData: Trend[]) {
		try {
			localStorage.setItem(CACHE_KEY, JSON.stringify({
				articles, trends: trendData,
				timestamp: Date.now()
			}));
		} catch {}
	}

	function loadFromCache(): { articles: Article[], trends: Trend[] } | null {
		try {
			const raw = localStorage.getItem(CACHE_KEY);
			if (!raw) return null;
			const cached = JSON.parse(raw);
			if (Date.now() - cached.timestamp > CACHE_TTL) return null;
			return cached;
		} catch { return null; }
	}

	async function load() {
		// Show cached data instantly
		const cached = loadFromCache();
		if (cached && cached.articles.length > 0) {
			allArticles = cached.articles;
			trends = cached.trends;
			loading = false;
			lastSynced = 'from cache';
			// Refresh in background
			fetchFresh();
			return;
		}
		loading = true;
		await fetchFresh();
	}

	async function fetchFresh() {
		try {
			const [a, t] = await Promise.all([api.getArticles(), api.getTrends()]);
			allArticles = a;
			trends = t;
			saveToCache(a, t);
			const now = new Date();
			lastSynced = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
		} catch (e) { console.error(e); }
		finally { loading = false; }
	}

	async function sync() {
		syncing = true;
		try {
			await api.triggerRefresh();
			// Clear cache and reload fresh
			try { localStorage.removeItem(CACHE_KEY); } catch {}
			await fetchFresh();
		}
		finally { syncing = false; }
	}

	async function openBrief(article: Article, e: MouseEvent) {
		e.stopPropagation();
		briefOpen = true;
		briefLoading = true;
		briefTitle = article.title;
		briefData = null;
		api.trackView(article.id).catch(() => {});
		try {
			const r = await api.getBrief(article.id);
			briefData = r.brief;
		} catch { briefData = 'Failed to generate briefing.'; }
		finally { briefLoading = false; }
	}

	onMount(load);
</script>

<div class="min-h-screen bg-[#0d0d0d] text-[#e2e2e2]" style="font-family: 'Inter', -apple-system, sans-serif;">

	<!-- ══ TOPBAR ════════════════════════════════════════════ -->
	<header class="sticky top-0 z-50 bg-[#0d0d0d]/95 backdrop-blur-sm border-b border-white/[0.06]">
		<div class="max-w-[1400px] mx-auto px-6 h-14 flex items-center gap-6">

			<!-- Brand -->
			<div class="flex items-center gap-2.5 shrink-0">
				<div class="w-6 h-6 rounded-md bg-white flex items-center justify-center shrink-0">
					<Zap class="w-3.5 h-3.5 text-black fill-black" />
				</div>
				<span class="text-white font-bold text-[15px] tracking-tight">AXON</span>
			</div>

			<div class="w-px h-5 bg-white/10 hidden sm:block"></div>

			<!-- Search -->
			<div class="flex-1 relative hidden sm:block">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Filter signals…"
					class="w-full max-w-md bg-white/[0.04] border border-white/[0.07] text-[13px] text-white placeholder-zinc-600 rounded-lg pl-9 pr-3 py-2 outline-none focus:border-white/20 focus:bg-white/[0.06] transition-all"
					style="font-family: inherit;"
				/>
			</div>

			<!-- Right controls -->
			<div class="flex items-center gap-3 ml-auto shrink-0">
				{#if activeFilters > 0}
					<button onclick={clearFilters} class="flex items-center gap-1.5 text-[12px] text-zinc-500 hover:text-white transition-colors">
						<X class="w-3.5 h-3.5" /> Clear filters
					</button>
				{/if}
				<span class="hidden sm:flex items-center gap-1.5 text-[12px] text-zinc-600">
					<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
					{filtered.length} of {allArticles.length}
				</span>
				<button
					onclick={sync}
					disabled={syncing}
					class="flex items-center gap-1.5 px-3.5 py-2 bg-white text-black text-[12px] font-semibold rounded-lg hover:bg-zinc-100 disabled:opacity-40 transition-colors"
				>
					<RefreshCw class="w-3.5 h-3.5 {syncing ? 'animate-spin' : ''}" />
					{syncing ? 'Syncing…' : 'Sync'}
				</button>
			</div>
		</div>
	</header>

	<!-- ══ BODY: SIDEBAR + FEED ══════════════════════════════ -->
	<div class="max-w-[1400px] mx-auto px-6 py-6 flex gap-7 items-start">

		<!-- ── LEFT SIDEBAR ──────────────────────────────────── -->
		<aside class="shrink-0 w-56 sticky top-[72px] hidden lg:flex flex-col gap-7">

			<!-- Filter by source -->
			<div>
				<p class="text-[10px] font-semibold text-zinc-600 uppercase tracking-[0.15em] mb-3 px-1">Source</p>
				<div class="flex flex-col gap-0.5">
					{#each sources as src}
						<button
							onclick={() => activeSource = activeSource === src ? null : src}
							class="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-left transition-all group
								{activeSource === src ? 'bg-white/8 text-white' : 'text-zinc-500 hover:bg-white/4 hover:text-zinc-200'}"
						>
							<div class="w-5 h-5 rounded-[4px] bg-white/6 border border-white/8 flex items-center justify-center shrink-0 text-[8px] font-bold text-zinc-400 group-hover:border-white/15 {activeSource === src ? 'border-white/20 bg-white/10 text-white' : ''}">
								{sourceInitial(src)}
							</div>
							<span class="text-[12px] font-medium truncate">{src}</span>
							<span class="ml-auto text-[10px] text-zinc-700">{allArticles.filter(a => a.source === src).length}</span>
						</button>
					{/each}
				</div>
			</div>

			<!-- Filter by category -->
			<div>
				<p class="text-[10px] font-semibold text-zinc-600 uppercase tracking-[0.15em] mb-3 px-1">Category</p>
				<div class="flex flex-col gap-0.5">
					{#each categories as cat}
						<button
							onclick={() => activeCategory = activeCategory === cat ? null : cat}
							class="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-left transition-all
								{activeCategory === cat ? 'bg-white/8' : 'hover:bg-white/4'}"
						>
							<div class="w-1.5 h-1.5 rounded-full {catBar(cat)} shrink-0"></div>
							<span class="text-[12px] font-medium {activeCategory === cat ? 'text-white' : 'text-zinc-500 hover:text-zinc-200'}">
								{cat}
							</span>
							<span class="ml-auto text-[10px] text-zinc-700">{allArticles.filter(a => a.category === cat).length}</span>
						</button>
					{/each}
				</div>
			</div>

			<!-- Trending -->
			{#if trends.length > 0}
				<div>
					<p class="text-[10px] font-semibold text-zinc-600 uppercase tracking-[0.15em] mb-3 px-1">Trending</p>
					<div class="flex flex-col gap-0.5">
						{#each trends.slice(0, 8) as trend}
							<button
								onclick={() => searchQuery = searchQuery === trend.keyword ? '' : trend.keyword}
								class="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left group hover:bg-white/4 transition-colors {searchQuery === trend.keyword ? 'bg-white/8' : ''}"
							>
								<span class="text-[12px] text-zinc-500 group-hover:text-zinc-200 truncate {searchQuery === trend.keyword ? 'text-white' : ''}">{trend.keyword}</span>
								<span class="text-[10px] text-zinc-700 ml-2">{trend.count}</span>
							</button>
						{/each}
					</div>
				</div>
			{/if}
		</aside>

		<!-- ── MAIN FEED ─────────────────────────────────────── -->
		<main class="flex-1 min-w-0">

			<!-- Active filter chips (mobile + desktop) -->
			{#if activeFilters > 0}
				<div class="flex items-center gap-2 mb-5 flex-wrap">
					<SlidersHorizontal class="w-3.5 h-3.5 text-zinc-600" />
					{#if activeSource}
						<button onclick={() => activeSource = null} class="flex items-center gap-1.5 px-2.5 py-1 bg-white/8 border border-white/12 rounded-full text-[11px] text-white hover:bg-white/12 transition-colors">
							{activeSource} <X class="w-3 h-3 text-zinc-400" />
						</button>
					{/if}
					{#if activeCategory}
						<button onclick={() => activeCategory = null} class="flex items-center gap-1.5 px-2.5 py-1 bg-white/8 border border-white/12 rounded-full text-[11px] text-white hover:bg-white/12 transition-colors">
							{activeCategory} <X class="w-3 h-3 text-zinc-400" />
						</button>
					{/if}
					{#if searchQuery}
						<button onclick={() => searchQuery = ''} class="flex items-center gap-1.5 px-2.5 py-1 bg-white/8 border border-white/12 rounded-full text-[11px] text-white hover:bg-white/12 transition-colors">
							"{searchQuery}" <X class="w-3 h-3 text-zinc-400" />
						</button>
					{/if}
				</div>
			{/if}

			{#if loading}
				<div class="py-24 flex flex-col items-center gap-4">
					<RefreshCw class="w-5 h-5 text-zinc-700 animate-spin" />
					<p class="text-zinc-600 text-[13px]">Fetching intelligence…</p>
				</div>
			{:else if filtered.length === 0}
				<div class="py-24 flex flex-col items-center gap-2 text-center">
					<p class="text-zinc-400 text-[14px] font-medium">No signals match your filters</p>
					<button onclick={clearFilters} class="mt-3 text-[12px] text-zinc-600 hover:text-white transition-colors underline underline-offset-2">Clear all filters</button>
				</div>
			{:else}
				<!-- Feed list -->
				<div class="border border-white/[0.06] rounded-xl overflow-hidden">
					{#each filtered as article, i}
						<div class="group relative flex gap-4 px-5 py-4 border-b border-white/[0.05] last:border-0 hover:bg-white/[0.02] transition-colors">

							<!-- Source avatar -->
							<div class="shrink-0 pt-0.5">
								<div class="w-7 h-7 rounded-lg bg-white/[0.05] border border-white/[0.07] flex items-center justify-center text-[9px] font-bold text-zinc-500 group-hover:border-white/[0.12] transition-colors">
									{sourceInitial(article.source)}
								</div>
							</div>

							<!-- Content -->
							<div class="flex-1 min-w-0 flex flex-col gap-1.5">

								<!-- Top meta -->
								<div class="flex items-center gap-2 flex-wrap">
									<button
										onclick={() => { if (activeSource === article.source) activeSource = null; else activeSource = article.source; }}
										class="text-[11px] font-semibold text-zinc-500 hover:text-zinc-200 transition-colors uppercase tracking-wide"
									>{article.source}</button>
									<span class="text-zinc-800">·</span>
									<button
										onclick={() => { if (activeCategory === article.category) activeCategory = null; else activeCategory = article.category; }}
										class="px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase border transition-colors cursor-pointer {catStyle(article.category)}"
									>{article.category}</button>
									{#if article.published_date}
										<span class="text-zinc-700 text-[11px] ml-0.5">{relativeTime(article.published_date)}</span>
									{/if}
									{#if article.insight}
										<div class="flex items-center gap-1 ml-0.5 text-violet-400/70 text-[10px] font-medium">
											<div class="w-1 h-1 rounded-full bg-violet-500"></div>
											AI Brief
										</div>
									{/if}
								</div>

								<!-- Title -->
								<button
									onclick={() => { api.trackView(article.id); window.open(article.url, '_blank'); }}
									class="text-left outline-none group/title"
								>
									<h3 class="text-white text-[14px] font-semibold leading-snug group-hover/title:text-zinc-300 transition-colors tracking-tight">
										{article.title}
									</h3>
								</button>

								<!-- Snippet / Insight -->
								{#if article.insight || article.content_snippet}
									<p class="text-zinc-500 text-[12px] leading-relaxed line-clamp-2 max-w-3xl">
										{stripHtml(article.insight || article.content_snippet || '')}
									</p>
								{/if}

								<!-- Actions (visible on hover) -->
								<div class="flex items-center gap-0.5 pt-0.5 opacity-0 group-hover:opacity-100 transition-opacity h-6">
									<button
										onclick={() => { api.trackView(article.id); window.open(article.url, '_blank'); }}
										class="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium text-zinc-600 hover:text-zinc-200 hover:bg-white/6 transition-all"
									>
										<ExternalLink class="w-3 h-3" /> Source
									</button>
									<button
										onclick={(e) => openBrief(article, e)}
										class="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium text-violet-400/70 hover:text-violet-300 hover:bg-violet-400/8 transition-all"
									>
										<Bot class="w-3 h-3" />
										{article.insight ? 'Full Brief' : 'AI Brief'}
										<ChevronRight class="w-3 h-3" />
									</button>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</main>
	</div>
</div>

<!-- Deep Brief Modal -->
<DeepBriefModal
	open={briefOpen}
	loading={briefLoading}
	title={briefTitle}
	briefData={briefData}
	onClose={() => briefOpen = false}
/>