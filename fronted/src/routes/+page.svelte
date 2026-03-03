<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { api, type Article, type Trend } from '../lib/api';
	import { 
		Zap, Search, X, SlidersHorizontal, ArrowLeft, 
		Send, MessageSquare, ExternalLink, RefreshCw,
		ChevronRight, Sparkles 
	} from 'lucide-svelte';

	// ── State ────────────────────────────────────────────────
	let allArticles = $state<Article[]>([]);
	let trends = $state<Trend[]>([]);
	let loading = $state(true);
	let syncIndicator = $state(false);
	let searchQuery = $state('');
	let activeSource = $state<string | null>(null);
	let activeCategory = $state<string | null>(null);

	// Navigation / View State
	let selectedArticle = $state<Article | null>(null);
	
	// Chat State
	let chatInput = $state('');
	let chatMessages = $state<{role: 'user' | 'ai', content: string}[]>([]);
	let chatLoading = $state(false);
	let chatContainer: HTMLElement;

	// Suggested Prompts
	const SUGGESTIONS = [
		"Summarize key technical primitives",
		"What is the strategic impact for founders?",
		"Identify potential risks or concerns",
		"What should a developer build with this?"
	];

	// ── Derived ──────────────────────────────────────────────
	let sources = $derived([...new Set(allArticles.map(a => a.source))].sort());
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

	// Brand Colors (Minimal left accents)
	const BRAND_COLORS: Record<string, string> = {
		HackerNews: '#FF6600',
		OpenAI: '#FFFFFF',
		NVIDIA: '#76B900',
		GitHub: '#EDEDED',
		Reddit: '#FF4500',
		ArXiv: '#B31B1B',
		DeepMind: '#2D3436', 
		Anthropic: '#D97757'
	};
	function getBrandColor(s: string) { return BRAND_COLORS[s] || '#3f3f46'; }

	// ── Logic ───────────────────────────────────────────────
	const CACHE_KEY = 'axon_premium_cache';

	async function load() {
		const raw = localStorage.getItem(CACHE_KEY);
		if (raw) {
			const c = JSON.parse(raw);
			allArticles = c.articles;
			trends = c.trends;
			loading = false;
		}
		
		// Always trigger smart sync on load
		smartSync();
	}

	async function smartSync() {
		syncIndicator = true;
		try {
			await api.triggerRefresh();
			const [a, t] = await Promise.all([api.getArticles(), api.getTrends()]);
			allArticles = a;
			trends = t;
			localStorage.setItem(CACHE_KEY, JSON.stringify({ articles: a, trends: t }));
		} catch (e) {
			console.error("Sync failed", e);
		} finally {
			syncIndicator = false;
			setTimeout(() => { /* clear indicator after a while */ }, 3000);
		}
	}

	function openArticle(a: Article) {
		selectedArticle = a;
		chatMessages = [];
		chatInput = '';
		api.trackView(a.id);
	}

	async function sendChat(msg?: string) {
		const text = msg || chatInput;
		if (!text.trim() || !selectedArticle || chatLoading) return;

		const userMsg = text.trim();
		chatMessages = [...chatMessages, { role: 'user', content: userMsg }];
		chatInput = '';
		chatLoading = true;

		// Scroll to bottom
		await tick();
		chatContainer?.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });

		try {
			const res = await api.chatWithArticle(selectedArticle.id, userMsg);
			chatMessages = [...chatMessages, { role: 'ai', content: res.answer }];
		} catch {
			chatMessages = [...chatMessages, { role: 'ai', content: 'Intelligence layer unavailable.' }];
		} finally {
			chatLoading = false;
			await tick();
			chatContainer?.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
		}
	}

	onMount(load);
</script>

<div class="min-h-screen bg-[#0a0a0a] text-[#f4f4f5] selection:bg-white selection:text-black" style="font-family: 'Inter', sans-serif;">

	{#if !selectedArticle}
		<!-- ══ FEED VIEW ════════════════════════════════════════ -->
		<div in:fade={{duration: 200}} out:fade={{duration: 200}} class="max-w-3xl mx-auto px-6 py-20 pb-40">
			
			<!-- Header -->
			<header class="mb-16 flex items-center justify-between">
				<div>
					<div class="flex items-center gap-2 mb-2">
						<div class="w-5 h-5 rounded bg-white flex items-center justify-center">
							<Zap class="w-3 h-3 text-black fill-black" />
						</div>
						<h1 class="text-[13px] font-bold tracking-widest text-white uppercase italic">Axon Intelligence</h1>
					</div>
					<p class="text-[13px] text-zinc-500 font-medium">Tracking the frontier of emerging technology.</p>
				</div>
				
				{#if syncIndicator}
					<div in:fade class="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10">
						<RefreshCw class="w-3 h-3 text-emerald-500 animate-spin" />
						<span class="text-[11px] text-zinc-400 font-medium">Syncing signals…</span>
					</div>
				{:else}
					<div class="text-[11px] text-zinc-600 font-medium uppercase tracking-tighter">Updated just now</div>
				{/if}
			</header>

			<!-- Filter Bar (Minimalist) -->
			<div class="flex items-center gap-6 mb-12 overflow-x-auto no-scrollbar pb-2 border-b border-white/[0.03]">
				<button 
					onclick={() => { activeSource = null; activeCategory = null; }}
					class="text-[13px] font-semibold transition-colors {(!activeSource && !activeCategory) ? 'text-white' : 'text-zinc-600 hover:text-zinc-400'}"
				>All Signals</button>
				
				{#each sources.slice(0, 5) as src}
					<button 
						onclick={() => activeSource = activeSource === src ? null : src}
						class="text-[13px] font-semibold transition-colors whitespace-nowrap {activeSource === src ? 'text-white' : 'text-zinc-600 hover:text-zinc-400'}"
					>{src}</button>
				{/each}

				<div class="flex-1 flex justify-end items-center relative min-w-[200px]">
					<Search class="absolute left-3 w-3.5 h-3.5 text-zinc-700" />
					<input 
						type="text" 
						bind:value={searchQuery}
						placeholder="Search frontier…"
						class="w-full bg-transparent border-0 text-[13px] pl-9 outline-none text-white placeholder-zinc-800"
					/>
				</div>
			</div>

			<!-- Feed List -->
			<div class="space-y-12">
				{#each filtered as article (article.id)}
					<button 
						onclick={() => openArticle(article)}
						in:fly={{ y: 20, duration: 400, delay: 50 }}
						class="group relative w-full text-left flex flex-col gap-3 transition-all duration-300 hover:-translate-y-1"
					>
						<!-- Left Accent -->
						<div 
							class="absolute -left-6 top-1 bottom-1 w-[2px] opacity-0 group-hover:opacity-100 transition-opacity rounded-full shadow-[0_0_8px_rgba(255,255,255,0.2)]"
							style="background-color: {getBrandColor(article.source)}"
						></div>

						<h3 class="text-[17px] font-semibold text-white leading-tight pr-10 group-hover:text-zinc-200 transition-colors">
							{article.title}
						</h3>
						
						<p class="text-[13px] text-zinc-500 leading-relaxed line-clamp-2 max-w-2xl font-medium">
							{stripHtml(article.insight || article.content_snippet || '')}
						</p>

						<div class="flex items-center gap-3 text-[11px] font-bold uppercase tracking-wider text-zinc-700 mt-1">
							<span class="text-zinc-500" style="color: {getBrandColor(article.source)}">{article.source}</span>
							<span>·</span>
							<span>{article.category}</span>
							<span>·</span>
							<span>{relativeTime(article.published_date)}</span>
							<div class="ml-auto opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1.5 text-zinc-600">
								<Zap class="w-3 h-3 fill-current" />
								{article.views + Math.floor(Math.random()*10)} views
							</div>
						</div>
					</button>
				{/each}

				{#if loading}
					<div class="py-20 flex justify-center">
						<RefreshCw class="w-6 h-6 text-zinc-800 animate-spin" />
					</div>
				{/if}
			</div>

		</div>
	{:else}
		<!-- ══ READER VIEW ═════════════════════════════════════ -->
		<div in:fly={{ x: 100, duration: 400 }} out:fade={{ duration: 200 }} class="fixed inset-0 bg-[#0a0a0a] z-[100] flex flex-col">
			
			<!-- Sticky Header -->
			<header class="h-16 border-b border-white/[0.05] flex items-center justify-between px-6 bg-[#0a0a0a]/80 backdrop-blur-md shrink-0">
				<button 
					onclick={() => selectedArticle = null}
					class="flex items-center gap-2 text-zinc-500 hover:text-white transition-colors"
				>
					<ArrowLeft class="w-4 h-4" />
					<span class="text-[11px] font-bold uppercase tracking-widest">Back to Feed</span>
				</button>

				<div class="flex items-center gap-4">
					<div class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.08] bg-white/[0.02]">
						<div class="w-1.5 h-1.5 rounded-full" style="background-color: {getBrandColor(selectedArticle.source)}"></div>
						<span class="text-[10px] font-bold uppercase tracking-wider text-zinc-400">{selectedArticle.source}</span>
					</div>
					<button 
						onclick={() => window.open(selectedArticle?.url, '_blank')}
						class="w-9 h-9 flex items-center justify-center rounded-full border border-white/[0.1] hover:bg-white hover:text-black transition-all"
					>
						<ExternalLink class="w-4 h-4" />
					</button>
				</div>
			</header>

			<!-- Scrollable Content -->
			<div class="flex-1 overflow-y-auto no-scrollbar">
				<div class="max-w-2xl mx-auto px-6 py-20 pb-40">
					
					<div class="flex items-center gap-2 mb-6 text-[10px] font-black uppercase tracking-[2px] text-zinc-600">
						<span>{selectedArticle.category}</span>
						<span>·</span>
						<span>{new Date(selectedArticle.published_date).toLocaleDateString()}</span>
					</div>

					<h2 class="text-3xl font-bold text-white leading-[1.15] mb-10 tracking-tight">
						{selectedArticle.title}
					</h2>

					<div class="space-y-6 text-[15px] leading-relaxed text-zinc-400 font-medium">
						<div class="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] mb-12">
							<div class="flex items-center gap-2 mb-4 text-white">
								<Sparkles class="w-4 h-4 text-violet-400" />
								<span class="text-[11px] font-bold uppercase tracking-widest">Axon Insight</span>
							</div>
							<p class="text-zinc-200 leading-relaxed italic">
								{stripHtml(selectedArticle.insight || '')}
							</p>
						</div>

						{stripHtml(selectedArticle.content_snippet || '')}
						
						<!-- Chat Area -->
						<div bind:this={chatContainer} class="pt-20 space-y-8">
							{#each chatMessages as msg}
								<div class="flex gap-4 {msg.role === 'ai' ? 'items-start' : 'items-center justify-end'}">
									{#if msg.role === 'ai'}
										<div class="w-7 h-7 rounded bg-white flex items-center justify-center shrink-0 mt-1">
											<Zap class="w-4 h-4 text-black fill-black" />
										</div>
									{/if}
									<div class="max-w-[85%] px-5 py-3 rounded-2xl text-[14px] leading-relaxed 
										{msg.role === 'user' ? 'bg-zinc-800 text-white' : 'bg-transparent text-zinc-300'}"
									>
										{msg.content}
									</div>
								</div>
							{/each}
							{#if chatLoading}
								<div class="flex gap-4 items-center">
									<div class="w-7 h-7 rounded bg-white flex items-center justify-center shrink-0">
										<Zap class="w-4 h-4 text-black animate-pulse" />
									</div>
									<div class="flex gap-1">
										<span class="w-1 h-1 rounded-full bg-zinc-700 animate-bounce"></span>
										<span class="w-1 h-1 rounded-full bg-zinc-700 animate-bounce [animation-delay:0.2s]"></span>
										<span class="w-1 h-1 rounded-full bg-zinc-700 animate-bounce [animation-delay:0.4s]"></span>
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>

			<!-- Anchored Bottom Bar -->
			<div class="sticky bottom-0 bg-[#0a0a0a]/90 backdrop-blur-xl border-t border-white/[0.05] p-6 shadow-[0_-20px_40px_rgba(0,0,0,0.5)] z-50">
				<div class="max-w-2xl mx-auto flex flex-col gap-4">
					
					<!-- Suggested Prompts -->
					{#if chatMessages.length === 0}
						<div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
							{#each SUGGESTIONS as tip}
								<button 
									onclick={() => sendChat(tip)}
									class="whitespace-nowrap px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.06] text-[11px] font-semibold text-zinc-400 hover:bg-white/[0.06] hover:text-white transition-all transition-all"
								>
									{tip}
								</button>
							{/each}
						</div>
					{/if}

					<div class="relative group">
						<input 
							type="text" 
							bind:value={chatInput}
							onkeydown={(e) => e.key === 'Enter' && sendChat()}
							placeholder="Interrogate this signal..."
							class="w-full bg-white/[0.03] border border-white/[0.08] rounded-2xl px-6 py-4 pr-14 text-[14px] outline-none focus:border-white/20 focus:bg-white/[0.05] transition-all"
						/>
						<button 
							onclick={() => sendChat()}
							disabled={!chatInput.trim() || chatLoading}
							class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-xl bg-white text-black flex items-center justify-center hover:bg-zinc-200 disabled:opacity-20 transition-all focus:scale-95 active:scale-90"
						>
							<Send class="w-4 h-4" />
						</button>
					</div>
				</div>
			</div>

		</div>
	{/if}

</div>

<style>
	:global(body) {
		background: #0a0a0a;
		overflow-x: hidden;
	}
	.no-scrollbar::-webkit-scrollbar {
		display: none;
	}
	.no-scrollbar {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
</style>