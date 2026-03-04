<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { api, type Article, type Trend } from '../lib/api';
	import { 
		Zap, Search, X, SlidersHorizontal, ArrowLeft, 
		Send, MessageSquare, ExternalLink, RefreshCw,
		ChevronRight, Sparkles, Home, TrendingUp, Radio,
		AlertCircle, Command
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
	let chatContainer: HTMLElement | undefined = $state();

	// Suggested Prompts
	const SUGGESTIONS = [
		"Technical primitives?",
		"Architecture shift?",
		"Data moat?",
		"Strategic impact?",
		"Build opportunity?"
	];

	const NAVIGATION = [
		{ id: null, label: 'All Signals', icon: Home },
		{ id: 'AI', label: 'AI & Research', icon: Sparkles },
		{ id: 'Signal', label: 'Signals', icon: Radio },
		{ id: 'Momentum', label: 'Momentum', icon: TrendingUp },
		{ id: 'Concerns', label: 'Concerns', icon: AlertCircle },
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

<div class="h-screen flex relative bg-[#0b0b0b] text-[#e4e4e7] overflow-hidden selection:bg-white selection:text-black" style="font-family: 'Inter', sans-serif;">

	<!-- ══ NAVIGATION SIDEBAR (Left) ═══════════════════════════ -->
	<nav class="w-56 flex flex-col items-stretch py-8 border-r border-white/[0.04] bg-[#0b0b0b] shrink-0 z-30">
		<!-- Logo Section -->
		<div class="px-7 mb-12">
			<div class="flex items-center gap-3">
				<div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
					<Zap class="w-4.5 h-4.5 text-black fill-black" />
				</div>
				<span class="text-[14px] font-black uppercase tracking-[3px] text-white italic">Axon</span>
			</div>
		</div>

		<div class="flex flex-col gap-2 px-3">
			{#each NAVIGATION as item}
				<button 
					onclick={() => {
						activeCategory = item.id;
						activeSource = null;
						selectedArticle = null;
					}}
					class="relative flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 {activeCategory === item.id ? 'bg-white/[0.05] text-white' : 'text-zinc-500 hover:bg-white/[0.02] hover:text-zinc-300'}"
				>
					<item.icon class="w-5 h-5 shrink-0" />
					<span class="text-[11px] font-bold uppercase tracking-[2px]">{item.label}</span>
					
					{#if activeCategory === item.id}
						<div class="absolute -left-[12px] top-1/2 -translate-y-1/2 w-1 h-6 bg-white rounded-r-full"></div>
					{/if}
				</button>
			{/each}
		</div>

		<div class="mt-auto px-6">
			<button class="flex items-center gap-4 w-full px-4 py-3 rounded-xl text-zinc-700 hover:text-white hover:bg-white/[0.02] transition-all">
				<Command class="w-5 h-5 shrink-0" />
				<span class="text-[10px] font-bold uppercase tracking-widest">Feedback</span>
			</button>
		</div>
	</nav>

	<!-- ══ MAIN VIEWPORT ═══════════════════════════════════════ -->
	<div class="flex-1 relative flex overflow-hidden">
		
		<!-- ══ INTELLIGENCE FEED ══════════════════════════════════ -->
		<!-- Wrapper for centering/sliding logic -->
		<div 
			class="flex h-full transition-all duration-700 ease-[cubic-bezier(0.2,0,0,1)]
			{selectedArticle ? 'w-[700px]' : 'w-full justify-center'}"
		>
			<div 
				class="w-[700px] flex flex-col h-full relative shrink-0 {selectedArticle ? 'border-r border-white/[0.04]' : ''}"
			>
				<!-- Header -->
				<header class="flex flex-col border-b border-white/[0.04] shrink-0 bg-[#0b0b0b]/80 backdrop-blur-xl z-20 sticky top-0">
					<div class="h-20 flex items-center justify-between px-10">
						<div class="flex items-center gap-4">
							<h1 class="text-[18px] font-black tracking-[4px] uppercase italic text-white leading-none">
								{activeCategory ?? 'Frontier'}
							</h1>
							<div class="h-1 w-1 rounded-full bg-zinc-800"></div>
							<span class="text-[10px] font-bold uppercase tracking-widest text-zinc-600">
								{filtered.length} Signals
							</span>
						</div>

						<div class="relative group">
							<Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 group-focus-within:text-white transition-colors" />
							<input 
								type="text" 
								bind:value={searchQuery}
								placeholder="Interrogate feed..."
								class="bg-white/[0.03] border border-white/[0.08] rounded-2xl pl-10 pr-4 py-2 text-[12px] outline-none focus:border-white/20 focus:bg-white/[0.05] transition-all w-48 focus:w-64 placeholder-zinc-700"
							/>
						</div>
					</div>

					<!-- Source Chips -->
					<div class="h-12 flex items-center gap-3 px-10 pb-4 overflow-x-auto no-scrollbar">
						<button 
							onclick={() => activeSource = null}
							class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-all border
							{activeSource === null ? 'bg-white text-black border-white' : 'bg-transparent text-zinc-500 border-white/5 hover:border-white/20 hover:text-zinc-300'}"
						>
							Meta
						</button>
						{#each sources as source}
							<button 
								onclick={() => activeSource = source}
								class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-all border
								{activeSource === source ? 'bg-zinc-100 text-black border-zinc-100' : 'bg-transparent text-zinc-500 border-white/5 hover:border-white/20 hover:text-zinc-300'}"
							>
								{source}
							</button>
						{/each}
					</div>
				</header>

				<!-- Feed Content -->
				<main class="flex-1 overflow-y-auto no-scrollbar scroll-smooth">
					<div class="px-8 py-12 space-y-0">
						{#each filtered as article (article.id)}
							<button 
								onclick={() => openArticle(article)}
								class="group relative w-full text-left py-10 border-b border-white/[0.04] transition-all hover:bg-white/[0.015] px-4 -mx-4 rounded-xl {selectedArticle?.id === article.id ? 'bg-white/[0.03]' : ''}"
							>
								<div class="absolute left-0 top-10 bottom-10 w-[1.5px] {selectedArticle?.id === article.id ? 'opacity-100' : 'opacity-20 group-hover:opacity-100'} transition-opacity rounded-full" style="background-color: {getBrandColor(article.source)}"></div>

								<div class="flex flex-col gap-2.5">
									<h3 class="text-[17px] font-semibold text-white leading-snug group-hover:text-zinc-200 transition-colors">
										{article.title}
									</h3>
									<p class="text-[13.5px] text-zinc-500 leading-relaxed line-clamp-2 max-w-xl font-medium">
										{stripHtml(article.insight || article.content_snippet || '')}
									</p>
									<div class="flex items-center justify-between mt-1">
										<div class="flex items-center gap-3 text-[10.5px] font-bold uppercase tracking-widest text-zinc-700">
											<span style="color: {getBrandColor(article.source)}">{article.source}</span>
											<span class="text-zinc-800">·</span>
											<span>{relativeTime(article.published_date)}</span>
										</div>
									</div>
								</div>
							</button>
						{/each}
					</div>
				</main>
			</div>
		</div>

		<!-- ══ READER PANEL ═══════════════════════════════════════ -->
		{#if selectedArticle}
			<aside 
				class="flex-1 bg-[#0a0a0a] flex flex-col relative z-10 border-l border-white/5 shadow-[20px_0_60px_rgba(0,0,0,0.5)]"
				transition:fly={{ x: 100, duration: 600, opacity: 0 }}
			>
				<!-- Sticky Header -->
				<header class="h-16 border-b border-white/[0.05] flex items-center justify-between px-6 bg-[#0a0a0a]/80 backdrop-blur-md shrink-0">
					<button onclick={() => selectedArticle = null} class="flex items-center gap-2 text-zinc-500 hover:text-white transition-colors">
						<ArrowLeft class="w-4 h-4" />
						<span class="text-[11px] font-bold uppercase tracking-widest">Back to Feed</span>
					</button>

					<div class="flex items-center gap-4">
						<div class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.08] bg-white/[0.02]">
							<div class="w-1.5 h-1.5 rounded-full" style="background-color: {getBrandColor(selectedArticle.source)}"></div>
							<span class="text-[10px] font-bold uppercase tracking-wider text-zinc-400">{selectedArticle.source}</span>
						</div>
						<button onclick={() => window.open(selectedArticle?.url, '_blank')} class="w-9 h-9 flex items-center justify-center rounded-full border border-white/[0.1] hover:bg-white hover:text-black transition-all">
							<ExternalLink class="w-4 h-4" />
						</button>
					</div>
				</header>

				<!-- Scrollable Content -->
				<div class="flex-1 overflow-y-auto no-scrollbar scroll-smooth">
					<div class="max-w-2xl mx-auto px-10 py-20 pb-48">
						<div class="flex items-center gap-2 mb-6 text-[10px] font-black uppercase tracking-[2px] text-zinc-600">
							<span>{selectedArticle.category}</span>
							<span>·</span>
							<span>{new Date(selectedArticle.published_date).toLocaleDateString()}</span>
						</div>

						<h2 class="text-[32px] font-bold text-white leading-[1.1] mb-12 tracking-tight">
							{selectedArticle.title}
						</h2>

						<div class="space-y-10 text-[15.5px] leading-relaxed text-zinc-400 font-medium">
							<div class="p-8 rounded-3xl bg-white/[0.02] border border-white/[0.05] relative overflow-hidden">
								<div class="flex items-center gap-2 mb-6 text-white">
									<Sparkles class="w-4 h-4 text-violet-400" />
									<span class="text-[11px] font-bold uppercase tracking-widest">Axon Insight</span>
								</div>
								<p class="text-zinc-200 leading-relaxed italic text-[17px]">
									{stripHtml(selectedArticle.insight || '')}
								</p>
							</div>

							<div class="prose prose-invert max-w-none">
								{stripHtml(selectedArticle.content_snippet || '')}
							</div>
							
							<!-- Chat Area -->
							<div bind:this={chatContainer} class="pt-24 space-y-10 border-t border-white/[0.04]">
								{#each chatMessages as msg}
									<div class="flex gap-5 {msg.role === 'ai' ? 'items-start' : 'items-center justify-end'}">
										{#if msg.role === 'ai'}
											<div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center shrink-0 mt-1">
												<Zap class="w-4 h-4 text-black fill-black" />
											</div>
										{/if}
										<div class="max-w-[85%] px-6 py-4 rounded-3xl text-[14.5px] leading-relaxed 
											{msg.role === 'user' ? 'bg-zinc-800/80 text-white' : 'bg-transparent text-zinc-300'}"
										>
											{msg.content}
										</div>
									</div>
								{/each}
								{#if chatLoading}
									<div class="flex gap-4 items-center pl-1">
										<div class="flex gap-1.5">
											<span class="w-1.5 h-1.5 rounded-full bg-zinc-700 animate-bounce"></span>
											<span class="w-1.5 h-1.5 rounded-full bg-zinc-700 animate-bounce [animation-delay:0.2s]"></span>
											<span class="w-1.5 h-1.5 rounded-full bg-zinc-700 animate-bounce [animation-delay:0.4s]"></span>
										</div>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>

				<!-- Anchored Chat -->
				<div class="absolute bottom-0 inset-x-0 bg-[#0a0a0a]/95 backdrop-blur-2xl border-t border-white/[0.06] p-8 z-30 shadow-2xl">
					<div class="max-w-2xl mx-auto flex flex-col gap-6">
						{#if chatMessages.length === 0}
							<div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
								{#each SUGGESTIONS as tip}
									<button onclick={() => sendChat(tip)} class="whitespace-nowrap px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] text-[11px] font-bold uppercase tracking-wider text-zinc-500 hover:bg-white/[0.08] hover:text-white transition-all">
										{tip}
									</button>
								{/each}
							</div>
						{/if}

						<div class="relative group">
							<input type="text" bind:value={chatInput} onkeydown={(e) => e.key === 'Enter' && sendChat()} placeholder="Interrogate this signal..." class="w-full bg-white/[0.04] border border-white/[0.1] rounded-2xl px-6 py-4.5 pr-16 text-[15px] outline-none focus:border-white/20 focus:bg-white/[0.06] transition-all" />
							<button onclick={() => sendChat()} disabled={!chatInput.trim() || chatLoading} class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-xl bg-white text-black flex items-center justify-center hover:bg-zinc-200 disabled:opacity-20 transition-all focus:scale-95">
								<Send class="w-4.5 h-4.5" />
							</button>
						</div>
					</div>
				</div>
			</aside>
		{/if}
	</div>
</div>

<style>
	:global(body) {
		background: #0b0b0b;
		overflow: hidden;
	}
	.no-scrollbar::-webkit-scrollbar {
		display: none;
	}
	.no-scrollbar {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
</style>
