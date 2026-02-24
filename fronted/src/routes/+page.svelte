<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Trend, type Article } from '../lib/api';
	import { Zap, RefreshCw, ExternalLink, Globe, Eye, Heart, TrendingUp } from 'lucide-svelte';

	// Svelte 5 uses "Runes" ($state) instead of let
	let trends = $state<Trend[]>([]);
	let articles = $state<Article[]>([]);
	let selectedTrend = $state<string | null>(null);
	let loading = $state(true);
	let refreshing = $state(false);

	async function loadDashboard(keyword: string | null = null) {
		loading = true;
		selectedTrend = keyword;
		const [tData, aData] = await Promise.all([
			api.getTrends(),
			api.getArticles(keyword || undefined)
		]);
		trends = tData;
		articles = aData;
		loading = false;
	}

	async function handleRefresh() {
		refreshing = true;
		await api.triggerRefresh();
		await loadDashboard();
		refreshing = false;
	}

	async function handleArticleClick(article: Article) {
		// Local update for UI responsiveness
		article.views += 1;
		
		// Await the backend update
		try {
			await api.trackView(article.id);
		} catch (e) {
			console.error("Failed to track view", e);
		}
		
		window.open(article.url, '_blank');
	}

	onMount(() => loadDashboard());
</script>

<div class="min-h-screen bg-[#09090b] text-zinc-400 font-sans selection:bg-emerald-500/30">
	<header class="border-b border-zinc-800 bg-[#09090b]/80 backdrop-blur-md sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
			<div class="flex items-center gap-2">
				<div class="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center text-black font-bold">A</div>
				<h1 class="text-white font-bold tracking-tight text-xl">AXON<span class="text-emerald-500">.</span>IO</h1>
			</div>

			<button 
				onclick={handleRefresh}
				disabled={refreshing}
				class="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900 border border-zinc-700 hover:border-emerald-500/50 transition-all disabled:opacity-50"
			>
				<RefreshCw class="w-4 h-4 {refreshing ? 'animate-spin' : ''}" />
				<span class="text-sm font-medium">Sync Intel</span>
			</button>
		</div>
	</header>

	<main class="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-8">
		<section class="col-span-12 lg:col-span-4 space-y-6">
			<h2 class="text-white font-semibold flex items-center gap-2">
				<Zap class="w-4 h-4 text-emerald-400" />
				Emerging Signals
			</h2>

			<div class="space-y-3">
				{#each trends as trend}
					<button 
						onclick={() => loadDashboard(trend.keyword)}
						class="w-full text-left p-4 rounded-xl border transition-all group {selectedTrend === trend.keyword ? 'bg-emerald-500/10 border-emerald-500/50' : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700'}"
					>
						<div class="flex justify-between items-start">
							<div>
								<p class="text-white font-medium group-hover:text-emerald-400 transition-colors capitalize">{trend.keyword}</p>
								<p class="text-xs mt-1 text-zinc-500">{trend.count} mentions</p>
							</div>
							<span class="px-2 py-1 rounded-md text-[10px] font-bold {trend.is_new ? 'bg-violet-500/20 text-violet-400' : 'bg-emerald-500/20 text-emerald-400'}">
								{trend.velocity}
							</span>
						</div>
					</button>
				{/each}
			</div>
		</section>

		<section class="col-span-12 lg:col-span-8 space-y-6">
			<div class="flex items-center justify-between">
				<h2 class="text-white font-semibold">
					{selectedTrend ? `Context: ${selectedTrend}` : 'Recent Intelligence Feed'}
				</h2>
				{#if selectedTrend}
					<button onclick={() => loadDashboard(null)} class="text-xs hover:text-white underline">Clear Filter</button>
				{/if}
			</div>

			<div class="grid gap-4">
				{#if loading}
					<div class="h-64 flex items-center justify-center border border-dashed border-zinc-800 rounded-2xl">
						Decrypting data...
					</div>
				{:else}
					{#each articles as article}
						<button 
							onclick={() => handleArticleClick(article)}
							class="w-full text-left p-5 rounded-2xl bg-zinc-900/30 border border-zinc-800 hover:border-zinc-700 transition-all group block"
						>
							<div class="flex justify-between items-start mb-3">
								<div class="flex items-center gap-3">
									<div class="flex items-center gap-2 text-[10px] font-bold uppercase text-emerald-500/80">
										<Globe class="w-3 h-3" /> {article.source}
									</div>
									<span class="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-500 border border-zinc-700">{article.category}</span>
								</div>
								<ExternalLink class="w-4 h-4 text-zinc-600 group-hover:text-white transition-colors" />
							</div>
							<h3 class="text-zinc-100 font-medium text-lg group-hover:text-emerald-400 transition-colors">{article.title}</h3>
							<p class="text-sm text-zinc-500 mt-2 line-clamp-2">{article.content_snippet}</p>
							
							<div class="flex items-center gap-6 mt-4 pt-4 border-t border-zinc-800/50">
								<div class="flex items-center gap-1.5 text-xs text-zinc-500">
									<Eye class="w-3.5 h-3.5" />
									<span>{article.views || 0}</span>
								</div>
								<div class="flex items-center gap-1.5 text-xs text-zinc-500">
									<Heart class="w-3.5 h-3.5" />
									<span>{article.likes || 0}</span>
								</div>
								<div class="flex items-center gap-1.5 text-xs font-medium text-emerald-500/80 ml-auto">
									<TrendingUp class="w-3.5 h-3.5" />
									<span>{article.engagement_score || 0}% Score</span>
								</div>
							</div>
						</button>
					{/each}
				{/if}
			</div>
		</section>
	</main>
</div>