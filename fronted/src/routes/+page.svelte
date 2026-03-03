<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api, type Trend, type Article } from '../lib/api';
	import { Zap, RefreshCw, ExternalLink, Globe, Eye, Heart, TrendingUp, Bot, ArrowRight, Activity, Command } from 'lucide-svelte';
	import DeepBriefModal from '$lib/components/DeepBriefModal.svelte';

	let trends = $state<Trend[]>([]);
	let articles = $state<Article[]>([]);
	let selectedTrend = $state<string | null>(null);
	let loading = $state(true);
	let refreshing = $state(false);

	// Keyboard Navigation state
	let selectedIndex = $state<number>(-1);

	// Deep Brief Modal state
	let briefModalOpen = $state(false);
	let loadingBrief = $state(false);
	let currentBriefTitle = $state("");
	let currentBriefData = $state<string | null>(null);

	async function loadDashboard(keyword: string | null = null) {
		loading = true;
		selectedTrend = keyword;
		selectedIndex = -1; // reset selection on load
		try {
			const [tData, aData] = await Promise.all([
				api.getTrends(),
				api.getArticles(keyword || undefined)
			]);
			trends = tData;
			articles = aData;
		} catch (e) {
			console.error("Failed to load dashboard data", e);
		} finally {
			loading = false;
		}
	}

	async function handleRefresh() {
		refreshing = true;
		try {
			await api.triggerRefresh();
			await loadDashboard(selectedTrend);
		} finally {
			refreshing = false;
		}
	}

	async function handleArticleClick(article: Article, index: number) {
		selectedIndex = index;
		article.views += 1;
		try {
			await api.trackView(article.id);
		} catch (e) {
			console.error("Failed to track view", e);
		}
		window.open(article.url, '_blank');
	}

	async function triggerDeepBrief(article: Article, index?: number) {
		if (index !== undefined) selectedIndex = index;
		
		briefModalOpen = true;
		loadingBrief = true;
		currentBriefTitle = article.title;
		currentBriefData = null;

		try {
			const res = await api.getBrief(article.id);
			currentBriefData = res.brief;
		} catch (e) {
			console.error("Failed to fetch deep brief", e);
			currentBriefData = "Failed to load Deep Briefing. Please try again later.";
		} finally {
			loadingBrief = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		// Don't intercept if modal is open or typing in input
		if (briefModalOpen || e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
			return;
		}

		if (articles.length === 0) return;

		switch (e.key) {
			case 'ArrowDown':
			case 'j':
				e.preventDefault();
				selectedIndex = Math.min(selectedIndex + 1, articles.length - 1);
				scrollToSelected();
				break;
			case 'ArrowUp':
			case 'k':
				e.preventDefault();
				selectedIndex = Math.max(selectedIndex - 1, 0);
				scrollToSelected();
				break;
			case 'o':
			case 'Enter':
				if (selectedIndex >= 0 && selectedIndex < articles.length) {
					e.preventDefault();
					handleArticleClick(articles[selectedIndex], selectedIndex);
				}
				break;
			case 'x':
			case 'X':
				if (selectedIndex >= 0 && selectedIndex < articles.length) {
					e.preventDefault();
					triggerDeepBrief(articles[selectedIndex]);
				}
				break;
			case 's':
			case 'S':
				e.preventDefault();
				handleRefresh();
				break;
			case 'Escape':
				selectedIndex = -1;
				selectedTrend = null;
				loadDashboard();
				break;
		}
	}

	function scrollToSelected() {
		// Small delay to let DOM update if needed, but in Svelte 5 runes it's synchronous mostly
		setTimeout(() => {
			const activeEl = document.getElementById(`article-${selectedIndex}`);
			if (activeEl) {
				activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
			}
		}, 10);
	}

	onMount(() => loadDashboard());
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="min-h-screen bg-[#060608] text-zinc-400 font-sans selection:bg-emerald-500/30">
	<!-- Top Navigation -->
	<header class="border-b border-zinc-900 bg-[#060608]/80 backdrop-blur-xl sticky top-0 z-40">
		<div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="w-8 h-8 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-center text-emerald-400">
					<Activity class="w-5 h-5" />
				</div>
				<h1 class="text-white font-bold tracking-tight text-xl">AXON<span class="text-emerald-500">_</span></h1>
				<span class="ml-4 px-2 py-0.5 text-[10px] font-mono tracking-widest text-emerald-400 bg-emerald-500/10 rounded uppercase border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
					Intelligence Layer
				</span>
			</div>

			<div class="flex items-center gap-6">
				<div class="hidden md:flex items-center gap-4 text-xs font-mono text-zinc-500">
					<span class="flex items-center gap-1.5"><kbd class="px-1.5 py-0.5 bg-zinc-900 rounded border border-zinc-800 text-zinc-400">↑↓</kbd> Nav</span>
					<span class="flex items-center gap-1.5"><kbd class="px-1.5 py-0.5 bg-zinc-900 rounded border border-zinc-800 text-zinc-400">O</kbd> Open</span>
					<span class="flex items-center gap-1.5"><kbd class="px-1.5 py-0.5 border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 rounded shadow-[0_0_8px_rgba(16,185,129,0.15)]">X</kbd> AI Brief</span>
				</div>

				<button 
					onclick={handleRefresh}
					disabled={refreshing}
					class="group flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900/50 border border-zinc-800 hover:border-emerald-500/30 hover:bg-emerald-500/5 transition-all outline-none focus:ring-2 focus:ring-emerald-500/50 disabled:opacity-50"
				>
					<RefreshCw class="w-4 h-4 text-zinc-400 group-hover:text-emerald-400 transition-colors {refreshing ? 'animate-spin text-emerald-500' : ''}" />
					<span class="text-sm font-medium text-white group-hover:text-emerald-400 transition-colors">Sync Intel</span>
					<span class="hidden lg:inline-flex ml-2 text-[10px] font-mono text-zinc-600">S</span>
				</button>
			</div>
		</div>
	</header>

	<main class="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-8 lg:gap-12 relative">
		
		<!-- Left Sidebar: Trends -->
		<section class="col-span-12 lg:col-span-3 space-y-6">
			<div class="flex items-center justify-between">
				<h2 class="text-white font-medium flex items-center gap-2 tracking-wide text-sm uppercase text-zinc-400">
					<Zap class="w-4 h-4 text-emerald-400" />
					Signal Momentum
				</h2>
			</div>

			<div class="space-y-2 relative">
				<!-- Gradient fade at bottom of list -->
				<div class="absolute bottom-0 inset-x-0 h-12 bg-gradient-to-t from-[#060608] to-transparent z-10 pointer-events-none fade-out"></div>
				
				<div class="max-h-[calc(100vh-200px)] overflow-y-auto no-scrollbar pb-12 space-y-2">
					{#each trends as trend}
						<button 
							onclick={() => loadDashboard(trend.keyword)}
							class="w-full text-left p-4 rounded-xl transition-all group relative overflow-hidden outline-none {selectedTrend === trend.keyword ? 'border-emerald-500/50 bg-emerald-500/5' : 'bg-transparent border border-transparent hover:bg-zinc-900/50'}"
						>
							{#if selectedTrend === trend.keyword}
								<div class="absolute left-0 inset-y-0 w-1 bg-emerald-500"></div>
							{/if}
							
							<div class="flex justify-between items-center ml-1">
								<div>
									<p class="text-[15px] font-medium transition-colors capitalize {selectedTrend === trend.keyword ? 'text-emerald-400' : 'text-zinc-300 group-hover:text-white'}">
										{trend.keyword}
									</p>
									<p class="text-xs mt-1 text-zinc-600 font-mono">{trend.count} signals</p>
								</div>
								<div class="flex items-center">
									<TrendingUp class="w-3 h-3 mr-1 {trend.is_new ? 'text-violet-400' : 'text-emerald-400'}" />
								</div>
							</div>
						</button>
					{/each}
				</div>
			</div>
		</section>

		<!-- Right Content: The Feed -->
		<section class="col-span-12 lg:col-span-9 space-y-6">
			<div class="flex items-center justify-between border-b border-zinc-900 pb-4">
				<div class="flex items-center gap-3">
					<h2 class="text-white text-xl font-medium tracking-tight">
						{selectedTrend ? `Vector Intersect: ${selectedTrend}` : 'Global Intelligence Stream'}
					</h2>
					<span class="px-2 py-0.5 rounded-full bg-zinc-900 text-xs text-zinc-500 font-mono">
						{articles.length} active
					</span>
				</div>
				
				{#if selectedTrend}
					<button 
						onclick={() => loadDashboard(null)} 
						class="text-xs hover:text-white text-zinc-500 flex items-center gap-1 transition-colors px-3 py-1.5 rounded-full hover:bg-zinc-900"
					>
						Clear Filter <kbd class="ml-1 text-[9px] bg-zinc-800 px-1 rounded uppercase">Esc</kbd>
					</button>
				{/if}
			</div>

			<div class="grid gap-3 relative">
				{#if loading}
					<div class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#060608]/50 backdrop-blur-sm pt-20">
						<div class="w-12 h-12 border border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin"></div>
						<p class="mt-4 text-emerald-500 font-mono text-xs uppercase tracking-widest animate-pulse">Scanning Grid...</p>
					</div>
					<!-- Skeleton loaders -->
					{#each Array(5) as _}
						<div class="h-40 rounded-xl bg-zinc-900/30 border border-zinc-900 animate-pulse"></div>
					{/each}
				{:else}
					{#each articles as article, index}
						<div 
							id="article-{index}"
							class="group relative w-full text-left p-5 xl:p-6 rounded-2xl transition-all block ring-1 outline-none isolate overflow-hidden {selectedIndex === index ? 'bg-zinc-900/80 ring-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.05)] scale-[1.01] z-10' : 'bg-transparent ring-zinc-800/50 hover:bg-zinc-900/40 hover:ring-zinc-700/50'}"
						>
							{#if selectedIndex === index}
								<!-- Active Selection Highlight Elements -->
								<div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-emerald-400 to-emerald-600 rounded-l-2xl"></div>
								<div class="absolute top-0 right-0 p-3 opacity-20">
									<Command class="w-24 h-24 text-emerald-500 animate-pulse-slow" />
								</div>
							{/if}

							<div class="relative z-10 flex justify-between items-start mb-3">
								<div class="flex items-center gap-3">
									<div class="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-emerald-500/90">
										<Globe class="w-3.5 h-3.5" /> {article.source}
									</div>
									<div class="w-1 h-1 rounded-full bg-zinc-700"></div>
									<span class="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-800">
										{article.category}
									</span>
								</div>
								
								<!-- Hover Action Menu -->
								<div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
									<button 
										onclick={() => triggerDeepBrief(article, index)}
										class="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-emerald-500/10 text-zinc-400 hover:text-emerald-400 transition-colors bg-black/40 border border-zinc-800 backdrop-blur"
										title="AI Deep Briefing (Press X)"
									>
										<Bot class="w-3.5 h-3.5" />
										<span class="text-xs font-medium">Analyze</span>
									</button>
									<button 
										onclick={() => handleArticleClick(article, index)}
										class="p-1.5 rounded hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors bg-black/40 border border-zinc-800 backdrop-blur"
										title="Open Source (Press O)"
									>
										<ExternalLink class="w-4 h-4" />
									</button>
								</div>
							</div>
							
							<h3 
								class="cursor-pointer text-zinc-100 font-medium text-lg lg:text-xl leading-tight mt-1 transition-colors {selectedIndex === index ? 'text-white' : 'group-hover:text-emerald-50'}" 
								onclick={() => handleArticleClick(article, index)}
								onkeydown={(e) => { if (e.key === 'Enter') handleArticleClick(article, index); }}
								role="button"
								tabindex="0"
							>
								{article.title}
							</h3>
							
							<p class="text-sm text-zinc-500 mt-2.5 line-clamp-2 leading-relaxed max-w-4xl">
								{article.content_snippet}
							</p>
							
							<div class="flex items-center gap-6 mt-5 pt-5 border-t border-zinc-800/50">
								<div class="flex items-center gap-1.5 text-xs text-zinc-500">
									<Eye class="w-4 h-4 text-zinc-600" />
									<span class="font-mono">{article.views || 0}</span>
								</div>
								<div class="flex items-center gap-1.5 text-xs text-zinc-500">
									<Heart class="w-4 h-4 text-zinc-600" />
									<span class="font-mono">{article.likes || 0}</span>
								</div>
								
								<button 
									onclick={() => triggerDeepBrief(article, index)}
									class="ml-auto inline-flex items-center gap-2 text-xs font-medium group/btn"
								>
									{#if article.insight}
										<span class="text-emerald-500/70 group-hover/btn:text-emerald-400 transition-colors">Has Insight</span>
										<div class="w-6 h-6 rounded-full bg-emerald-500/10 flex items-center justify-center group-hover/btn:bg-emerald-500/20 transition-colors">
											<Bot class="w-3 h-3 text-emerald-500" />
										</div>
									{:else}
										<span class="text-zinc-600 group-hover/btn:text-emerald-500 transition-colors hidden sm:inline-block">Generate Briefing</span>
										<ArrowRight class="w-4 h-4 text-zinc-700 group-hover/btn:text-emerald-500 transition-colors group-hover/btn:translate-x-1 duration-300" />
									{/if}
								</button>
							</div>

							<!-- Visual indicator for selected article -->
							{#if selectedIndex === index}
								<div class="absolute bottom-4 right-4 text-[10px] font-mono text-zinc-600 bg-zinc-950/80 px-2 py-1 rounded">PRESS O TO OPEN</div>
							{/if}
						</div>
					{/each}
				{/if}
			</div>
		</section>
	</main>
</div>

<!-- Modal Component -->
<DeepBriefModal 
	open={briefModalOpen}
	loading={loadingBrief}
	title={currentBriefTitle}
	briefData={currentBriefData}
	onClose={() => briefModalOpen = false}
/>

<style>
  .no-scrollbar::-webkit-scrollbar { display: none; }
  .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
	
	/* Slow pulse for selected background accent */
	@keyframes pulse-slow {
		0%, 100% { opacity: 0.1; }
		50% { opacity: 0.2; }
	}
	:global(.animate-pulse-slow) {
		animation: pulse-slow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
</style>