<script lang="ts">
	import AxonNetworkBg from '$lib/components/hero/AxonNetworkBg.svelte';
	import { Zap, ArrowRight, Github, Terminal, Cpu, Layers, Globe, Code2, Sparkles, Newspaper, Play, Users } from 'lucide-svelte';
</script>

<svelte:head>
	<title>AXON — The Bleeding Edge, Summarized.</title>
</svelte:head>

<!-- Added 'antialiased' for crisper typography -->
<div class="relative min-h-screen w-full bg-[#FAFAFA] dark:bg-[#050505] text-zinc-900 dark:text-zinc-100 transition-colors duration-500 font-sans overflow-x-hidden selection:bg-emerald-500/30 selection:text-emerald-900 dark:selection:bg-emerald-400/30 dark:selection:text-emerald-100 antialiased">
	
	<!-- Ambient Background -->
	<div class="fixed inset-0 z-0 overflow-hidden pointer-events-none bg-[#FAFAFA] dark:bg-[#050505]">
		<!-- The new converging signal background -->
		<AxonNetworkBg />
		
		<!-- We keep this gradient so it fades gracefully as you scroll down -->
		<div class="absolute inset-0 bg-gradient-to-b from-transparent via-[#FAFAFA]/50 to-[#FAFAFA] dark:via-[#050505]/80 dark:to-[#050505] mt-[50vh]"></div>
	</div>

	<!-- Floating Glass Header -->
	<header class="fixed top-6 left-0 right-0 z-50 mx-auto w-full max-w-5xl px-6 sm:px-10">
		<div class="flex items-center justify-between rounded-full border border-zinc-200/80 dark:border-white/10 bg-white/70 dark:bg-zinc-950/60 px-6 py-3.5 backdrop-blur-xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.1)] transition-all">
			<div class="flex items-center gap-3 group cursor-pointer">
				<div class="flex h-9 w-9 items-center justify-center rounded-xl bg-zinc-900 dark:bg-white text-white dark:text-black shadow-inner transition-transform group-hover:scale-105 group-hover:rotate-3">
					<Zap class="h-4 w-4 fill-current" />
				</div>
				<span class="text-lg font-black uppercase tracking-[0.2em] text-zinc-900 dark:text-white">Axon</span>
			</div>
			
			<div class="flex items-center gap-6">
				<a href="/login" class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors hidden sm:block">
					Sign in
				</a>
				<a href="/signup" class="group relative overflow-hidden rounded-full bg-zinc-900 dark:bg-white px-6 py-2.5 text-sm font-semibold text-white dark:text-zinc-900 shadow-md transition-all hover:scale-105 active:scale-95">
					<span class="relative z-10 flex items-center gap-2">
						Join Network <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-1" />
					</span>
				</a>
			</div>
		</div>
	</header>

	<!-- SECTION 1: THE HOOK (Hero) -->
	<section class="relative z-10 mx-auto flex min-h-[100vh] w-full max-w-5xl flex-col items-center justify-center px-6 pt-20 text-center sm:px-10">
		
		<!-- Enhanced Live Badge -->
		<div class="mb-8 inline-flex items-center gap-2.5 rounded-full border border-zinc-200/80 dark:border-white/10 bg-white/80 dark:bg-white/5 px-4 py-2 text-xs font-semibold text-zinc-600 dark:text-zinc-300 shadow-sm backdrop-blur-md transition-transform hover:scale-105 cursor-default">
			<span class="relative flex h-2.5 w-2.5">
				<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
				<span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
			</span>
			<span class="tracking-wide">LIVE: Tracking global tech signals</span>
		</div>

		<!-- Tighter typography, better gradient -->
		<h1 class="max-w-4xl text-6xl font-extrabold tracking-tighter text-zinc-900 dark:text-white sm:text-8xl leading-[1.1]">
			Stop scrolling. <br />
			<span class="text-transparent bg-clip-text bg-gradient-to-r from-zinc-500 via-zinc-800 to-zinc-500 dark:from-white dark:via-zinc-400 dark:to-zinc-600">Start synthesizing.</span>
		</h1>
		
		<p class="mt-8 max-w-2xl text-lg leading-relaxed text-zinc-500 dark:text-zinc-400 sm:text-xl font-medium">
			AXON is an intelligence engine for builders. We aggregate the absolute best of <span class="text-zinc-900 dark:text-zinc-100">AI, code, and tech news</span>, using Grok to distill hours of reading into a 3-minute tactical briefing.
		</p>

		<!-- Dual CTAs for better conversion -->
		<div class="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:gap-6">
			<a href="/signup" class="group relative flex h-14 w-full sm:w-auto items-center justify-center gap-2 overflow-hidden rounded-2xl bg-zinc-900 dark:bg-white px-8 text-base font-semibold text-white dark:text-zinc-900 shadow-[0_0_40px_-10px_rgba(0,0,0,0.4)] dark:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] transition-all hover:-translate-y-1 hover:shadow-xl active:translate-y-0">
				Initialize your feed
				<ArrowRight class="h-4 w-4 opacity-70 transition-transform group-hover:translate-x-1" />
			</a>
			<button class="group flex h-14 w-full sm:w-auto items-center justify-center gap-2 rounded-2xl border border-zinc-200 dark:border-white/10 bg-white/50 dark:bg-white/5 px-8 text-base font-semibold text-zinc-900 dark:text-white backdrop-blur-sm transition-all hover:bg-zinc-50 dark:hover:bg-white/10">
				<Play class="h-4 w-4 text-zinc-500 dark:text-zinc-400 transition-transform group-hover:scale-110" />
				See how it works
			</button>
		</div>

		<!-- Social Proof -->
		<div class="mt-12 flex items-center gap-4 text-sm font-medium text-zinc-500 dark:text-zinc-400">
			<div class="flex -space-x-3">
				<!-- Replace with actual user avatars if you have them -->
				<div class="h-8 w-8 rounded-full border-2 border-white dark:border-[#050505] bg-zinc-200 dark:bg-zinc-800"></div>
				<div class="h-8 w-8 rounded-full border-2 border-white dark:border-[#050505] bg-zinc-300 dark:bg-zinc-700"></div>
				<div class="h-8 w-8 rounded-full border-2 border-white dark:border-[#050505] bg-zinc-400 dark:bg-zinc-600"></div>
				<div class="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white dark:border-[#050505] bg-zinc-100 dark:bg-zinc-900">
					<Users class="h-3 w-3 text-zinc-500" />
				</div>
			</div>
			<p>Joined by <span class="font-bold text-zinc-900 dark:text-white">2,400+</span> elite builders</p>
		</div>
	</section>

	<!-- SECTION 2: THE SOURCES (Bento Grid Style) -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-6 py-32 sm:px-10">
		<div class="text-center mb-16">
			<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-xs font-bold uppercase tracking-[0.2em] text-zinc-600 dark:text-zinc-400 mb-6">
				<span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span> Phase 1: Ingestion
			</div>
			<h2 class="text-4xl font-extrabold text-zinc-900 dark:text-white sm:text-5xl tracking-tight">Tap the global firehose.</h2>
			<p class="mt-6 text-lg text-zinc-500 dark:text-zinc-400 max-w-2xl mx-auto">
				Stop checking 15 different sites. AXON continuously monitors the raw nodes where frontier technology is built, debated, and shipped.
			</p>
		</div>

		<!-- Bento Grid -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
			{#each [
				{ name: 'HackerNews', desc: 'Frontpage & Show HN', icon: Terminal, style: 'md:col-span-2 md:row-span-2 p-8' },
				{ name: 'GitHub', desc: 'Trending Repositories', icon: Github, style: 'p-6' },
				{ name: 'ArXiv', desc: 'New AI/ML Papers', icon: Layers, style: 'p-6' },
				{ name: 'ProductHunt', desc: 'Top daily launches', icon: Globe, style: 'p-6' },
				{ name: 'OpenAI', desc: 'Research Updates', icon: Cpu, style: 'p-6' },
			] as source}
				<div class="flex flex-col justify-between rounded-3xl border border-zinc-200 dark:border-white/5 bg-white/50 dark:bg-white/[0.02] hover:bg-white dark:hover:bg-white/[0.04] transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group cursor-default backdrop-blur-sm {source.style}">
					<source.icon class="h-8 w-8 text-zinc-400 dark:text-zinc-500 group-hover:text-emerald-500 dark:group-hover:text-emerald-400 transition-colors" />
					<div class="mt-8">
						<h3 class="font-bold text-lg text-zinc-900 dark:text-white">{source.name}</h3>
						<p class="text-xs font-medium uppercase tracking-wider text-zinc-500 mt-2">{source.desc}</p>
					</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- SECTION 3: THE ENGINE -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-6 py-20 sm:px-10">
		<div class="rounded-[2.5rem] border border-zinc-200/80 dark:border-white/10 bg-white/60 dark:bg-zinc-950/80 backdrop-blur-2xl overflow-hidden shadow-2xl">
			<div class="grid lg:grid-cols-2 items-stretch">
				<div class="p-10 sm:p-16 flex flex-col justify-center">
					<div class="inline-flex items-center gap-2 px-3 py-1 w-max rounded-full bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-xs font-bold uppercase tracking-[0.2em] text-zinc-600 dark:text-zinc-400 mb-6">
						<span class="h-1.5 w-1.5 rounded-full bg-blue-500"></span> Phase 2: Synthesis
					</div>
					<h3 class="text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-white mb-6">Grok filters the noise.</h3>
					<p class="text-lg text-zinc-500 dark:text-zinc-400 mb-8 leading-relaxed">
						99% of the internet is distraction. We pipe thousands of daily signals through a custom <strong class="text-zinc-900 dark:text-zinc-200 font-bold">Grok AI engine</strong> to extract raw value.
					</p>
					
					<div class="space-y-5">
						{#each [
							{ title: 'Deduplication', desc: 'Merges 50 articles about the same launch into one core update.' },
							{ title: 'Technical Extraction', desc: 'Pulls out actual benchmark numbers, not marketing fluff.' },
							{ title: 'Actionable Insights', desc: 'Tells you exactly what you need to change in your codebase.' }
						] as feature}
							<div class="flex gap-4">
								<div class="flex-shrink-0 mt-1">
									<div class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
										<Sparkles class="h-4 w-4" />
									</div>
								</div>
								<div>
									<h4 class="font-bold text-zinc-900 dark:text-zinc-100">{feature.title}</h4>
									<p class="text-sm text-zinc-500 dark:text-zinc-400 mt-1">{feature.desc}</p>
								</div>
							</div>
						{/each}
					</div>
				</div>
				
				<!-- Polished Code/Terminal Mockup -->
				<div class="bg-zinc-900 dark:bg-[#0A0A0A] p-8 sm:p-12 relative overflow-hidden flex flex-col justify-center border-t lg:border-t-0 lg:border-l border-zinc-200 dark:border-white/5">
					<div class="absolute -top-24 -right-24 p-4 opacity-5 pointer-events-none">
						<Cpu class="h-96 w-96 text-white" />
					</div>
					
					<div class="space-y-4 relative z-10 font-mono text-sm">
						<!-- Terminal Header -->
						<div class="flex items-center gap-2 mb-6">
							<div class="h-3 w-3 rounded-full bg-red-500/80"></div>
							<div class="h-3 w-3 rounded-full bg-yellow-500/80"></div>
							<div class="h-3 w-3 rounded-full bg-green-500/80"></div>
							<span class="ml-2 text-xs text-zinc-500">axon-engine.ts</span>
						</div>

						<div class="p-4 rounded-xl bg-zinc-800/50 dark:bg-white/5 text-zinc-500 line-through opacity-70">
							[Analyzing 412 HackerNews comments...]
						</div>
						<div class="p-4 rounded-xl bg-zinc-800/50 dark:bg-white/5 text-zinc-500 line-through opacity-70">
							[Discarding generic opinion piece...]
						</div>
						
						<!-- High Signal Output -->
						<div class="p-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 shadow-[0_0_30px_rgba(16,185,129,0.15)] transform hover:scale-[1.02] transition-transform">
							<div class="flex items-center gap-2 text-emerald-400 font-bold mb-3">
								<Zap class="h-4 w-4 fill-current" /> > HIGH SIGNAL DETECTED
							</div>
							<p class="text-zinc-300 leading-relaxed mb-3">
								<span class="text-white font-semibold">OpenAI Structured Outputs</span> reduces JSON schema hallucination by 90%.
							</p>
							<div class="bg-black/40 rounded p-3 text-xs text-zinc-400 border border-white/5">
								<span class="text-purple-400">Action:</span> Update parsing logic. Replace old regex sanitizers with native strict schema validation.
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 4: THE DELIVERY -->
	<section class="relative z-10 mx-auto w-full max-w-4xl px-6 py-32 sm:px-10 text-center">
		<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-xs font-bold uppercase tracking-[0.2em] text-zinc-600 dark:text-zinc-400 mb-6">
			<span class="h-1.5 w-1.5 rounded-full bg-purple-500"></span> Phase 3: Delivery
		</div>
		<h2 class="text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-white sm:text-5xl mb-6">Your 3-minute advantage.</h2>
		<p class="text-lg text-zinc-500 dark:text-zinc-400 mb-16 max-w-2xl mx-auto">
			No endless feeds. No doomscrolling. Just a beautifully formatted, highly readable briefing waiting for you when you wake up.
		</p>

		<!-- Polished Email/App Mockup -->
		<div class="rounded-3xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-[#0A0A0A] p-8 sm:p-10 text-left shadow-2xl mx-auto max-w-2xl transform transition hover:-translate-y-2 hover:shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] dark:hover:shadow-[0_20px_60px_-15px_rgba(255,255,255,0.05)] duration-500">
			<div class="flex items-center justify-between mb-8 border-b border-zinc-100 dark:border-zinc-800 pb-6">
				<div class="flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-900 dark:bg-white text-white dark:text-black">
						<Zap class="h-5 w-5 fill-current" />
					</div>
					<div>
						<h3 class="font-bold text-zinc-900 dark:text-white">AXON Daily Briefing</h3>
						<p class="text-xs text-zinc-500">Today, 8:00 AM</p>
					</div>
				</div>
				<div class="px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold">
					3 min read
				</div>
			</div>
			
			<div class="space-y-8">
				<div>
					<h4 class="text-xl font-bold text-zinc-900 dark:text-white mb-3">1. GitHub Copilot adds o1-preview support</h4>
					<div class="space-y-3">
						<p class="text-zinc-600 dark:text-zinc-400 leading-relaxed">
							<strong class="text-zinc-900 dark:text-zinc-200">The shift:</strong> Copilot now utilizes OpenAI's reasoning model for complex architectural refactoring.
						</p>
						<p class="text-zinc-600 dark:text-zinc-400 leading-relaxed">
							<strong class="text-zinc-900 dark:text-zinc-200">Why it matters:</strong> You can now prompt for full multi-file structural changes rather than just inline autocomplete.
						</p>
					</div>
					<div class="mt-4 flex gap-2">
						<span class="inline-flex items-center gap-1 text-[11px] font-mono font-medium bg-zinc-100 dark:bg-zinc-800 px-2.5 py-1 rounded-md text-zinc-600 dark:text-zinc-400"><Github class="h-3 w-3" /> GitHub Blog</span>
						<span class="inline-flex items-center gap-1 text-[11px] font-mono font-medium bg-orange-100/50 dark:bg-orange-500/10 px-2.5 py-1 rounded-md text-orange-600 dark:text-orange-400"><Terminal class="h-3 w-3" /> HackerNews (#1)</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 5: FINAL CTA -->
	<section class="relative z-10 mx-auto w-full max-w-5xl px-6 py-24 sm:px-10 text-center mb-20">
		<div class="relative rounded-[3rem] border border-zinc-200/80 dark:border-white/10 bg-white/50 dark:bg-zinc-900/30 p-12 sm:p-20 backdrop-blur-xl overflow-hidden shadow-2xl">
			<!-- Decorative Background Glow -->
			<div class="absolute inset-0 bg-gradient-to-b from-emerald-500/5 to-transparent pointer-events-none"></div>
			
			<div class="relative z-10">
				<h2 class="text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-white sm:text-6xl mb-6">
					Ready to plug in?
				</h2>
				<p class="text-lg text-zinc-500 dark:text-zinc-400 mb-10 max-w-xl mx-auto font-medium">
					Join thousands of elite builders who use AXON to stay ahead of the curve without sacrificing their time.
				</p>
				<a href="/signup" class="inline-flex h-16 items-center justify-center gap-3 rounded-2xl bg-zinc-900 dark:bg-white px-10 text-lg font-bold text-white dark:text-zinc-900 transition-all hover:scale-105 active:scale-95 shadow-xl hover:shadow-2xl">
					Create your free account
					<ArrowRight class="h-5 w-5" />
				</a>
				<p class="mt-6 text-sm text-zinc-500">No credit card required. Unsubscribe anytime.</p>
			</div>
		</div>
	</section>

</div>