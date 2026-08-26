<script lang="ts">
	import AxonNetworkBg from '$lib/components/hero/AxonNetworkbg.svelte';
	import { reveal } from '$lib/actions/reveal';
	import {
		Zap, ArrowRight, Github, Terminal, Cpu, Layers,
		Sparkles, Play, MessageSquare, Rss
	} from 'lucide-svelte';

	const SITE_URL = 'https://axon-phi-ruby.vercel.app';
	const TAGLINE = 'Catch up on AI — without drowning in it.';
	const OG_DESC =
		'The world moves fast. One place to track what matters — Healthy Signals from HN, ArXiv, GitHub, Reddit, and AI labs, in a 3-minute daily brief.';

	const sources = [
		{ name: 'Hacker News', desc: 'Front page & Show HN', icon: Terminal, style: 'sm:col-span-2 sm:row-span-2 p-8' },
		{ name: 'GitHub', desc: 'Trending repositories', icon: Github, style: 'p-6' },
		{ name: 'ArXiv', desc: 'New AI / ML papers', icon: Layers, style: 'p-6' },
		{ name: 'Reddit', desc: 'Builder communities', icon: Rss, style: 'p-6' },
		{ name: 'AI Labs', desc: 'OpenAI · Anthropic · DeepMind', icon: Cpu, style: 'p-6' }
	];

	const engineFeatures = [
		{ title: 'Noise out', desc: 'Drops fluff, listicles, and engagement bait before they hit your brief.' },
		{ title: 'Healthy Signal in', desc: 'Keeps papers, releases, tools, and debates that help you build.' },
		{ title: 'Actionable insight', desc: 'Says what changed — and what it means for what you’re shipping.' },
		{ title: 'Article-scoped chat', desc: 'Ask any signal a question, powered by LLaMA 3.3.' }
	];

	function scrollToEngine(e: MouseEvent) {
		e.preventDefault();
		document.getElementById('engine')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
	}
</script>

<svelte:head>
	<title>AXON — {TAGLINE}</title>
	<meta name="description" content="{OG_DESC} Free to try." />
	<meta property="og:type" content="website" />
	<meta property="og:site_name" content="AXON" />
	<meta property="og:title" content="AXON — {TAGLINE}" />
	<meta property="og:description" content={OG_DESC} />
	<meta property="og:url" content={SITE_URL} />
	<meta property="og:image" content="{SITE_URL}/og.png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="AXON — {TAGLINE}" />
	<meta name="twitter:description" content={OG_DESC} />
	<meta name="twitter:image" content="{SITE_URL}/og.png" />
	<link rel="canonical" href={SITE_URL} />
</svelte:head>

<div class="relative min-h-screen w-full overflow-x-hidden bg-white dark:bg-[#0B0F17] font-sans text-zinc-900 dark:text-[#E8ECF4] antialiased selection:bg-zinc-900 selection:text-white dark:selection:bg-[#5B8CFF]/40 dark:selection:text-white">

	<!-- Ambient background -->
	<div class="pointer-events-none fixed inset-0 z-0 overflow-hidden bg-white dark:bg-[#0B0F17]">
		<AxonNetworkBg />
		<div class="absolute inset-0 bg-gradient-to-b from-white/10 via-white/60 to-white dark:from-[#0B0F17]/20 dark:via-[#0B0F17]/75 dark:to-[#0B0F17]"></div>
	</div>

	<!-- Floating glass header -->
	<header class="fixed left-0 right-0 top-5 z-50 mx-auto w-full max-w-6xl px-4 sm:px-8">
		<div class="flex items-center justify-between rounded-2xl border border-zinc-200 dark:border-[#242E43] bg-white/80 dark:bg-[#121826]/80 px-4 py-3 backdrop-blur-xl sm:px-5">
			<a href="/" class="group flex items-center gap-3">
				<div class="flex h-8 w-8 items-center justify-center rounded-md bg-black text-white transition-transform group-hover:scale-105 dark:bg-white/10 dark:ring-1 dark:ring-white/10">
					<Zap class="h-4 w-4 fill-current" />
				</div>
				<span class="text-sm font-semibold uppercase tracking-[0.2em]">Axon</span>
			</a>

			<div class="flex items-center gap-2 sm:gap-4">
				<a href="/login" class="hidden text-sm font-medium text-zinc-600 transition-colors hover:text-zinc-900 dark:text-[#A3ADBF] dark:hover:text-[#E8ECF4] sm:block">
					Sign in
				</a>
				<a href="/signup" class="group inline-flex items-center gap-2 rounded-md bg-black dark:bg-white text-white dark:text-black px-4 py-2 text-sm font-semibold transition-colors hover:bg-zinc-800 dark:hover:bg-zinc-200">
					Get the brief
					<ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
				</a>
			</div>
		</div>
	</header>

	<!-- SECTION 1: HERO -->
	<section class="relative z-10 mx-auto flex min-h-screen w-full max-w-5xl flex-col items-center justify-center px-5 pt-20 text-center sm:px-8">

		<div use:reveal={{ delay: 0 }} class="mb-8 inline-flex cursor-default items-center gap-2 rounded-full border border-zinc-300 dark:border-[#33415C] bg-white/80 dark:bg-[#121826]/80 px-3 py-1.5 text-xs font-medium text-zinc-600 dark:text-[#A3ADBF]">
			<span class="relative flex h-2.5 w-2.5">
				<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#22C3A6] opacity-70"></span>
				<span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#22C3A6]"></span>
			</span>
			<span class="tracking-wide">LIVE · HN · ArXiv · GitHub · Reddit · AI labs</span>
		</div>

		<h1 use:reveal={{ delay: 80 }} class="max-w-4xl text-4xl font-bold leading-[1.1] tracking-tight sm:text-6xl">
			Catch up on AI — without drowning in it.
		</h1>

		<p use:reveal={{ delay: 160 }} class="mt-6 max-w-2xl text-base font-normal leading-7 text-zinc-600 dark:text-[#A3ADBF] sm:text-lg">
			The world moves fast. AXON is <span class="text-zinc-900 dark:text-[#E8ECF4]">one place to track what matters</span> —
			<span class="text-zinc-900 dark:text-[#E8ECF4]">Healthy Signals only</span> from Hacker News, ArXiv, GitHub, Reddit, and the labs.
			Skim it in three minutes.
		</p>

		<div use:reveal={{ delay: 240 }} class="mt-8 flex w-full max-w-sm flex-col items-center gap-3">
			<a href="/signup" class="group inline-flex h-12 w-full items-center justify-center gap-2 rounded-md bg-black dark:bg-white text-white dark:text-black px-6 text-sm font-semibold transition-colors hover:bg-zinc-800 dark:hover:bg-zinc-200">
				Get today’s brief — free
				<ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
			</a>
			<a href="#engine" onclick={scrollToEngine} class="group inline-flex items-center gap-2 text-sm font-medium text-zinc-500 dark:text-[#7B8497] transition-colors hover:text-zinc-700 dark:hover:text-[#A3ADBF]">
				<Play class="h-4 w-4 transition-transform group-hover:scale-110" />
				See how it works
			</a>
		</div>

		<div use:reveal={{ delay: 320 }} class="mt-10">
			<p class="text-sm font-medium text-zinc-500 dark:text-[#7B8497]">
				Free to try · One brief · No credit card
			</p>
		</div>
	</section>

	<!-- SECTION 2: SOURCES -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-5 py-24 sm:px-8">
		<div use:reveal class="mb-12 text-center">
			<div class="mb-5 inline-flex items-center gap-2 rounded-full border border-zinc-300 dark:border-[#33415C] bg-white dark:bg-[#121826] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-zinc-500 dark:text-[#7B8497]">
				<span class="h-1.5 w-1.5 rounded-full bg-[#22C3A6]"></span> Phase 1 · Ingestion
			</div>
			<h2 class="text-3xl font-semibold tracking-tight sm:text-4xl">One place to track what matters.</h2>
			<p class="mx-auto mt-4 max-w-2xl text-base leading-7 text-zinc-600 dark:text-[#A3ADBF] sm:text-lg">
				Stop juggling 15 tabs. AXON watches where AI and tech are built, debated, and shipped — then keeps only Healthy Signals.
			</p>
		</div>

		<div class="mx-auto grid max-w-5xl grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
			{#each sources as source, i}
				<div
					use:reveal={{ delay: i * 70 }}
					class="group flex cursor-default flex-col justify-between rounded-2xl border border-zinc-200 dark:border-[#242E43] bg-white/90 dark:bg-[#121826]/90 transition-colors duration-200 hover:border-zinc-300 dark:hover:border-[#33415C] hover:bg-zinc-50 dark:hover:bg-[#1A2233] {source.style}"
				>
					<source.icon class="h-8 w-8 text-zinc-500 dark:text-[#7B8497] transition-colors group-hover:text-[#5B8CFF]" />
					<div class="mt-8">
						<h3 class="text-lg font-semibold">{source.name}</h3>
						<p class="mt-2 text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-[#7B8497]">{source.desc}</p>
					</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- SECTION 3: ENGINE -->
	<section id="engine" class="relative z-10 mx-auto w-full max-w-6xl scroll-mt-28 px-5 py-20 sm:px-8">
		<div use:reveal class="overflow-hidden rounded-[1.75rem] border border-zinc-200 dark:border-[#242E43] bg-white/90 dark:bg-[#121826]/90 backdrop-blur-xl">
			<div class="grid items-stretch lg:grid-cols-2">
				<div class="flex flex-col justify-center p-10 sm:p-16">
					<div class="mb-6 inline-flex w-max items-center gap-2 rounded-full border border-zinc-300 dark:border-[#33415C] bg-zinc-100 dark:bg-[#0F1522] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-zinc-500 dark:text-[#7B8497]">
						<span class="h-1.5 w-1.5 rounded-full bg-[#5B8CFF]"></span> Phase 2 · Synthesis
					</div>
					<h3 class="mb-6 text-3xl font-semibold tracking-tight sm:text-4xl">Catch up — without drowning.</h3>
					<p class="mb-8 text-base leading-7 text-zinc-600 dark:text-[#A3ADBF] sm:text-lg">
						Most feeds amplify whatever gets attention. AXON’s <strong class="font-semibold text-zinc-900 dark:text-[#E8ECF4]">healthy algorithm</strong> keeps
						<strong class="font-semibold text-zinc-900 dark:text-[#E8ECF4]">Healthy Signals</strong> — informative AI and tech worth your time — and drops the fluff. Powered by Groq and LLaMA 3.3.
					</p>

					<div class="space-y-5">
						{#each engineFeatures as feature, i}
							<div use:reveal={{ delay: i * 90 }} class="flex gap-4">
								<div class="mt-1 flex-shrink-0">
									<div class="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-100 dark:bg-[#0F1522] text-[#22C3A6]">
										<Sparkles class="h-4 w-4" />
									</div>
								</div>
								<div>
									<h4 class="font-semibold">{feature.title}</h4>
									<p class="mt-1 text-sm text-zinc-600 dark:text-[#A3ADBF]">{feature.desc}</p>
								</div>
							</div>
						{/each}
					</div>
				</div>

				<!-- Terminal mockup -->
				<div class="relative flex flex-col justify-center overflow-hidden border-t border-zinc-200 dark:border-[#242E43] bg-zinc-100 dark:bg-[#0F1522] p-8 sm:p-12 lg:border-l lg:border-t-0">
					<div class="pointer-events-none absolute -top-24 -right-24 p-4 opacity-[0.04] dark:opacity-5">
						<Cpu class="h-96 w-96 text-zinc-900 dark:text-white" />
					</div>

					<div class="relative z-10 space-y-4 font-mono text-sm">
						<div class="mb-6 flex items-center gap-2">
							<div class="h-3 w-3 rounded-full bg-red-500/80"></div>
							<div class="h-3 w-3 rounded-full bg-yellow-500/80"></div>
							<div class="h-3 w-3 rounded-full bg-green-500/80"></div>
							<span class="ml-2 text-xs text-zinc-500 dark:text-[#7B8497]">axon-engine.ts</span>
						</div>

						<div class="rounded-xl bg-white dark:bg-[#121826] p-4 text-zinc-400 dark:text-[#7B8497] line-through opacity-75">
							[Analyzing 412 Hacker News comments…]
						</div>
						<div class="rounded-xl bg-white dark:bg-[#121826] p-4 text-zinc-400 dark:text-[#7B8497] line-through opacity-75">
							[Discarding generic opinion piece…]
						</div>

						<div use:reveal={{ delay: 120 }} class="rounded-xl border border-zinc-300 dark:border-[#33415C] bg-white dark:bg-[#121826] p-5">
							<div class="mb-3 flex items-center gap-2 font-bold text-[#22C3A6]">
								<Zap class="h-4 w-4 fill-current" /> &gt; HEALTHY SIGNAL
							</div>
							<p class="mb-3 leading-relaxed text-zinc-600 dark:text-[#A3ADBF]">
								<span class="font-semibold text-zinc-900 dark:text-[#E8ECF4]">OpenAI Structured Outputs</span> cuts JSON schema hallucination by 90%.
							</p>
							<div class="rounded border border-zinc-200 dark:border-[#242E43] bg-zinc-50 dark:bg-[#0B0F17] p-3 text-xs text-zinc-600 dark:text-[#A3ADBF]">
								<span class="text-[#5B8CFF]">Action:</span> Replace old regex sanitizers with native strict schema validation.
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 4: DELIVERY -->
	<section class="relative z-10 mx-auto w-full max-w-4xl px-5 py-24 text-center sm:px-8">
		<div use:reveal>
			<div class="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-300 dark:border-[#33415C] bg-white dark:bg-[#121826] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-zinc-500 dark:text-[#7B8497]">
				<span class="h-1.5 w-1.5 rounded-full bg-[#22C3A6]"></span> Phase 3 · Delivery
			</div>
			<h2 class="mb-6 text-3xl font-semibold tracking-tight sm:text-4xl">Your 3-minute brief.</h2>
			<p class="mx-auto mb-14 max-w-2xl text-base leading-7 text-zinc-600 dark:text-[#A3ADBF] sm:text-lg">
				No endless feeds. No doomscrolling. Just Healthy Signals — waiting when you wake up.
			</p>
		</div>

		<div use:reveal={{ delay: 80 }} class="mx-auto max-w-2xl rounded-2xl border border-zinc-200 dark:border-[#242E43] bg-white dark:bg-[#121826] p-7 text-left sm:p-9">
			<div class="mb-8 flex items-center justify-between border-b border-zinc-200 dark:border-[#242E43] pb-6">
				<div class="flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-md bg-black dark:bg-white text-white dark:text-black">
						<Zap class="h-5 w-5 fill-current" />
					</div>
					<div>
						<h3 class="font-semibold">AXON Daily Briefing</h3>
						<p class="text-xs text-zinc-500 dark:text-[#7B8497]">Today, 8:00 AM</p>
					</div>
				</div>
				<div class="rounded-full bg-zinc-100 dark:bg-[#0F1522] px-3 py-1 text-xs font-semibold text-[#22C3A6]">
					3 min read
				</div>
			</div>

			<div>
				<h4 class="mb-3 text-xl font-semibold">1. GitHub Copilot adds o1-preview support</h4>
				<div class="space-y-3">
					<p class="leading-relaxed text-zinc-600 dark:text-[#A3ADBF]">
						<strong class="text-zinc-900 dark:text-[#E8ECF4]">The shift:</strong> Copilot now uses OpenAI’s reasoning model for complex architectural refactoring.
					</p>
					<p class="leading-relaxed text-zinc-600 dark:text-[#A3ADBF]">
						<strong class="text-zinc-900 dark:text-[#E8ECF4]">Why it matters:</strong> You can prompt for full multi-file structural changes, not just inline autocomplete.
					</p>
				</div>
				<div class="mt-4 flex flex-wrap gap-2">
					<span class="inline-flex items-center gap-1 rounded-md bg-zinc-100 dark:bg-[#0F1522] px-2.5 py-1 text-[11px] font-mono font-medium text-zinc-600 dark:text-[#A3ADBF]"><Github class="h-3 w-3" /> GitHub Blog</span>
					<span class="inline-flex items-center gap-1 rounded-md bg-amber-100 dark:bg-[#3D3112] px-2.5 py-1 text-[11px] font-mono font-medium text-amber-700 dark:text-[#F59E0B]"><Terminal class="h-3 w-3" /> Hacker News #1</span>
					<span class="inline-flex items-center gap-1 rounded-md bg-zinc-100 dark:bg-[#0F1522] px-2.5 py-1 text-[11px] font-mono font-medium text-zinc-600 dark:text-[#A3ADBF]"><MessageSquare class="h-3 w-3" /> Ask Axon</span>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 5: FINAL CTA -->
	<section class="relative z-10 mx-auto mb-20 w-full max-w-5xl px-5 py-20 text-center sm:px-8">
		<div use:reveal class="relative overflow-hidden rounded-[2rem] border border-zinc-200 dark:border-[#242E43] bg-white/90 dark:bg-[#121826]/90 p-10 backdrop-blur-xl sm:p-16">
			<div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#5B8CFF]/10 to-transparent"></div>

			<div class="relative z-10">
				<h2 class="mb-6 text-3xl font-semibold tracking-tight sm:text-5xl">Ready to catch up?</h2>
				<p class="mx-auto mb-10 max-w-xl text-base leading-7 text-zinc-600 dark:text-[#A3ADBF] sm:text-lg">
					One place to track what matters. Healthy Signals only — free to try.
				</p>
				<div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
					<a href="/signup" class="group inline-flex h-12 items-center justify-center gap-2 rounded-md bg-black dark:bg-white text-white dark:text-black px-8 text-base font-semibold transition-colors hover:bg-zinc-800 dark:hover:bg-zinc-200">
						Get today’s brief
						<ArrowRight class="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
					</a>
					<a href="#engine" onclick={scrollToEngine} class="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-zinc-300 dark:border-[#33415C] px-8 text-base font-semibold text-zinc-700 dark:text-[#A3ADBF] transition-colors hover:border-zinc-400 hover:text-zinc-900 dark:hover:border-[#5B8CFF]/50 dark:hover:text-[#E8ECF4]">
						How it works
					</a>
				</div>
				<p class="mt-6 text-sm text-zinc-500 dark:text-[#7B8497]">Free to try · Healthy Signals · No credit card required</p>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="relative z-10 border-t border-zinc-200 dark:border-[#242E43]">
		<div class="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-6 px-5 py-10 sm:flex-row sm:px-8">
			<div class="flex items-center gap-3">
				<div class="flex h-7 w-7 items-center justify-center rounded-md bg-black dark:bg-white text-white dark:text-black">
					<Zap class="h-3.5 w-3.5 fill-current" />
				</div>
				<span class="text-sm text-zinc-500 dark:text-[#7B8497]">Catch up on AI — without drowning in it.</span>
			</div>
			<div class="flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm font-medium text-zinc-500 dark:text-[#7B8497]">
				<a href="/privacy" class="transition-colors hover:text-zinc-900 dark:hover:text-[#E8ECF4]">Privacy</a>
				<a href="/terms" class="transition-colors hover:text-zinc-900 dark:hover:text-[#E8ECF4]">Terms</a>
				<a href="/login" class="transition-colors hover:text-zinc-900 dark:hover:text-[#E8ECF4]">Sign in</a>
				<a href="/signup" class="transition-colors hover:text-zinc-900 dark:hover:text-[#E8ECF4]">Get started</a>
			</div>
		</div>
		<div class="mx-auto w-full max-w-6xl px-5 pb-10 text-center text-xs text-zinc-400 dark:text-[#525C6E] sm:px-8 sm:text-left">
			© 2026 Bemnet Mussa · Healthy Signals only · Built with SvelteKit, FastAPI &amp; Groq.
		</div>
	</footer>

</div>
