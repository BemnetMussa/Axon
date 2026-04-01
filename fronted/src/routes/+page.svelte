<script lang="ts">
	import ShaderLines from '$lib/components/hero/ShaderLines.svelte';
	import { Zap, ArrowRight, Github, Terminal, Cpu, Layers, Globe, Code2, Sparkles, Newspaper } from 'lucide-svelte';
</script>

<svelte:head>
	<title>AXON — The Bleeding Edge, Summarized.</title>
</svelte:head>

<div class="relative min-h-screen w-full bg-white dark:bg-[#050505] text-zinc-900 dark:text-zinc-100 transition-colors duration-500 font-sans overflow-x-hidden selection:bg-black selection:text-white dark:selection:bg-white dark:selection:text-black">
	
	<!-- Ambient Background -->
	<div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
		<div class="absolute inset-0 opacity-[0.15] dark:opacity-40 mix-blend-luminosity">
			<ShaderLines />
		</div>
		<div class="absolute inset-0 bg-gradient-to-b from-transparent via-white/80 to-white dark:via-[#050505]/80 dark:to-[#050505]"></div>
	</div>

	<!-- Floating Glass Header -->
	<header class="fixed top-0 left-0 right-0 z-50 mx-auto w-full max-w-6xl px-6 py-6 sm:px-10">
		<div class="flex items-center justify-between rounded-2xl border border-zinc-200/50 dark:border-white/10 bg-white/60 dark:bg-black/40 px-5 py-3 backdrop-blur-md shadow-sm">
			<div class="flex items-center gap-2">
				<div class="flex h-8 w-8 items-center justify-center rounded bg-black dark:bg-white text-white dark:text-black shadow-lg">
					<Zap class="h-4 w-4 fill-current" />
				</div>
				<span class="text-lg font-black uppercase tracking-[0.2em] italic text-zinc-900 dark:text-white">Axon</span>
			</div>
			
			<div class="flex items-center gap-4">
				<a href="/login" class="text-sm font-medium text-zinc-600 dark:text-zinc-300 hover:text-black dark:hover:text-white transition-colors hidden sm:block">
					Sign in
				</a>
				<a href="/signup" class="group relative overflow-hidden rounded-xl bg-black dark:bg-white px-5 py-2.5 text-sm font-medium text-white dark:text-black shadow-md transition-all hover:scale-[1.02] active:scale-[0.98]">
					<span class="relative z-10 flex items-center gap-2">
						Join Network <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
					</span>
				</a>
			</div>
		</div>
	</header>

	<!-- SECTION 1: THE HOOK (Hero) -->
	<section class="relative z-10 mx-auto flex min-h-[90vh] w-full max-w-5xl flex-col items-center justify-center px-6 pt-32 text-center sm:px-10">
		<div class="mb-8 inline-flex items-center gap-2 rounded-full border border-zinc-200 dark:border-white/10 bg-white/50 dark:bg-white/5 px-4 py-1.5 text-xs font-semibold text-zinc-600 dark:text-zinc-300 shadow-sm backdrop-blur-sm">
			<span class="relative flex h-2 w-2">
				<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
				<span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
			</span>
			Live: Tracking global tech signals
		</div>

		<h1 class="max-w-4xl text-5xl font-bold tracking-tight text-zinc-900 dark:text-white sm:text-7xl">
			Stop scrolling. <br />
			<span class="text-transparent bg-clip-text bg-gradient-to-r from-zinc-400 to-zinc-600 dark:from-zinc-300 dark:to-zinc-600">Start synthesizing.</span>
		</h1>
		
		<p class="mt-8 max-w-2xl text-lg leading-relaxed text-zinc-600 dark:text-zinc-400 sm:text-xl">
			AXON is an intelligence engine for builders. We aggregate the absolute best of <span class="font-medium text-black dark:text-white">AI, code, and tech news</span>, and use Grok to distill hours of reading into a 3-minute tactical briefing.
		</p>

		<div class="mt-10 flex flex-col items-center gap-4 sm:flex-row">
			<a href="/signup" class="group relative flex h-14 items-center justify-center gap-2 overflow-hidden rounded-xl bg-black dark:bg-white px-8 text-base font-medium text-white dark:text-black shadow-[0_0_40px_-10px_rgba(0,0,0,0.3)] dark:shadow-[0_0_40px_-10px_rgba(255,255,255,0.2)] transition-all hover:scale-[1.02] active:scale-[0.98]">
				Initialize your feed
				<ArrowRight class="h-4 w-4 opacity-70 transition-transform group-hover:translate-x-1" />
			</a>
		</div>
	</section>

	<!-- SECTION 2: THE SOURCES (Where data comes from) -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-6 py-24 sm:px-10">
		<div class="text-center mb-16">
			<h2 class="text-xs font-bold uppercase tracking-[0.25em] text-zinc-500 dark:text-emerald-400/90 mb-3">Phase 1: Ingestion</h2>
			<h3 class="text-3xl font-bold text-zinc-900 dark:text-white sm:text-4xl">We tap the global firehose.</h3>
			<p class="mt-4 text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
				You don't have time to check 15 different sites every morning. AXON continuously monitors the top platforms where frontier technology is actually built and discussed.
			</p>
		</div>

		<!-- Source Badges Grid -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
			{#each [
				{ name: 'HackerNews', desc: 'Frontpage & Show HN', icon: Terminal },
				{ name: 'GitHub', desc: 'Trending Repositories', icon: Github },
				{ name: 'ArXiv', desc: 'New AI/ML Papers', icon: Layers },
				{ name: 'ProductHunt', desc: 'Top daily launches', icon: Globe },
				{ name: 'OpenAI', desc: 'Research & Releases', icon: Cpu },
				{ name: 'Nvidia', desc: 'Dev/Hardware updates', icon: Code2 },
				{ name: 'TechCrunch', desc: 'Major ecosystem shifts', icon: Newspaper },
				{ name: 'Lobsters', desc: 'Deep technical discussions', icon: Zap }
			] as source}
				<div class="flex flex-col items-center justify-center p-6 rounded-2xl border border-zinc-200 dark:border-white/5 bg-zinc-50/50 dark:bg-white/[0.02] hover:bg-zinc-100 dark:hover:bg-white/[0.05] transition-colors group cursor-default">
					<source.icon class="h-6 w-6 mb-3 text-zinc-400 dark:text-zinc-500 group-hover:text-black dark:group-hover:text-white transition-colors" />
					<span class="font-bold text-sm text-zinc-900 dark:text-white">{source.name}</span>
					<span class="text-[10px] uppercase tracking-wider text-zinc-500 mt-1 text-center">{source.desc}</span>
				</div>
			{/each}
		</div>
	</section>

	<!-- SECTION 3: THE ENGINE (How Grok processes it) -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-6 py-24 sm:px-10">
		<div class="rounded-3xl border border-zinc-200 dark:border-white/10 bg-white/50 dark:bg-[#0a0a0a]/80 backdrop-blur-xl overflow-hidden shadow-2xl">
			<div class="grid lg:grid-cols-2 items-center">
				<div class="p-10 lg:p-16">
					<h2 class="text-xs font-bold uppercase tracking-[0.25em] text-zinc-500 dark:text-blue-400/90 mb-3">Phase 2: Synthesis</h2>
					<h3 class="text-3xl font-bold text-zinc-900 dark:text-white sm:text-4xl mb-6">Grok filters the noise.</h3>
					<p class="text-zinc-600 dark:text-zinc-400 mb-6 leading-relaxed">
						99% of the internet is distraction. We pipe thousands of daily signals through a custom **Grok AI engine**. 
					</p>
					<p class="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-8">
						It detects duplicate stories, identifies true technological breakthroughs, and rewrites the core value into concise, actionable intelligence points. No fluff, no clickbait.
					</p>
					
					<ul class="space-y-4">
						{#each ['Removes duplicate coverage', 'Extracts core technical specs', 'Highlights builder-specific action items'] as feature}
							<li class="flex items-center gap-3 text-sm font-medium text-zinc-800 dark:text-zinc-200">
								<Sparkles class="h-4 w-4 text-emerald-500" /> {feature}
							</li>
						{/each}
					</ul>
				</div>
				
				<!-- Mockup of the "AI Processing" -->
				<div class="h-full bg-zinc-100 dark:bg-black/50 p-10 border-l border-zinc-200 dark:border-white/10 relative overflow-hidden">
					<div class="absolute top-0 right-0 p-4 opacity-20">
						<Cpu class="h-32 w-32 text-zinc-500" />
					</div>
					<div class="space-y-4 relative z-10 font-mono text-xs">
						<div class="p-3 rounded border border-zinc-200 dark:border-white/10 bg-white dark:bg-black text-zinc-500 line-through opacity-60">
							[Analyzing 412 HackerNews comments on new Model...]
						</div>
						<div class="p-3 rounded border border-zinc-200 dark:border-white/10 bg-white dark:bg-black text-zinc-500 line-through opacity-60">
							[Discarding generic TechCrunch opinion piece...]
						</div>
						<div class="p-4 rounded border border-emerald-500/30 bg-emerald-50/50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
							<span class="font-bold">> HIGH SIGNAL DETECTED:</span><br/>
							OpenAI releases structured outputs API. Reduces hallucination by 90% for JSON schemas. <br/>
							*Action:* Update your parsing functions.
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 4: THE DELIVERY (What the user gets) -->
	<section class="relative z-10 mx-auto w-full max-w-4xl px-6 py-24 sm:px-10 text-center">
		<h2 class="text-xs font-bold uppercase tracking-[0.25em] text-zinc-500 dark:text-cyan-400/90 mb-3">Phase 3: Delivery</h2>
		<h3 class="text-3xl font-bold text-zinc-900 dark:text-white sm:text-4xl mb-6">Your 3-minute daily advantage.</h3>
		<p class="text-zinc-600 dark:text-zinc-400 mb-12 max-w-2xl mx-auto">
			You don't get a dashboard full of links. You get a beautifully formatted, highly readable briefing waiting for you when you log in. Know exactly what happened in tech while you were sleeping.
		</p>

		<!-- Visual Mockup of the final feed -->
		<div class="rounded-2xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-[#111] p-6 text-left shadow-xl mx-auto max-w-2xl transform transition hover:-translate-y-1 hover:shadow-2xl duration-300">
			<div class="flex items-center gap-2 mb-6 border-b border-zinc-100 dark:border-white/5 pb-4">
				<Zap class="h-4 w-4 text-emerald-500" />
				<span class="font-bold text-sm text-zinc-900 dark:text-white">AXON Daily Briefing</span>
				<span class="text-xs text-zinc-400 ml-auto">Today, 8:00 AM</span>
			</div>
			
			<div class="space-y-6">
				<div>
					<h4 class="font-bold text-zinc-900 dark:text-white mb-2">1. GitHub Copilot adds o1-preview support</h4>
					<p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
						<span class="font-medium text-black dark:text-zinc-300">The shift:</span> Copilot now utilizes OpenAI's reasoning model for complex architectural refactoring. <br/>
						<span class="font-medium text-black dark:text-zinc-300">Why it matters:</span> You can now prompt for full multi-file structural changes rather than just autocomplete.
					</p>
					<div class="mt-2 flex gap-2">
						<span class="text-[10px] font-mono bg-zinc-100 dark:bg-white/10 px-2 py-1 rounded text-zinc-500">Source: GitHub Blog</span>
						<span class="text-[10px] font-mono bg-zinc-100 dark:bg-white/10 px-2 py-1 rounded text-zinc-500">Source: HackerNews (#1)</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 5: FINAL CTA -->
	<section class="relative z-10 mx-auto w-full max-w-4xl px-6 py-24 sm:px-10 text-center mb-20">
		<div class="rounded-3xl border border-zinc-200 dark:border-white/10 bg-zinc-50/50 dark:bg-white/5 p-12 backdrop-blur-sm">
			<h2 class="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white sm:text-5xl mb-6">
				Ready to plug in?
			</h2>
			<p class="text-zinc-600 dark:text-zinc-400 mb-8 max-w-lg mx-auto">
				Join thousands of elite builders who use AXON to stay ahead of the curve without sacrificing their time.
			</p>
			<a href="/signup" class="inline-flex h-14 items-center justify-center gap-2 rounded-xl bg-black dark:bg-white px-8 text-base font-medium text-white dark:text-black transition-all hover:scale-[1.02] active:scale-[0.98]">
				Create your free account
				<ArrowRight class="h-4 w-4" />
			</a>
		</div>
	</section>

</div>