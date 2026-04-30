<script lang="ts">
import AxonNetworkBg from '$lib/components/hero/AxonNetworkbg.svelte';
	import { Zap, ArrowRight, Github, Terminal, Cpu, Layers, Globe, Code2, Sparkles, Newspaper, Play, Users } from 'lucide-svelte';
</script>

<svelte:head>
	<title>AXON — The Bleeding Edge, Summarized.</title>
</svelte:head>

<div class="relative min-h-screen w-full overflow-x-hidden bg-[#0B0F17] font-sans text-[#E8ECF4] antialiased selection:bg-[#5B8CFF]/40 selection:text-white">
	
	<!-- Ambient Background -->
	<div class="pointer-events-none fixed inset-0 z-0 overflow-hidden bg-[#0B0F17]">
		<AxonNetworkBg />
		
		<div class="absolute inset-0 bg-gradient-to-b from-[#0B0F17]/20 via-[#0B0F17]/75 to-[#0B0F17]"></div>
	</div>

	<!-- Floating Glass Header -->
	<header class="fixed left-0 right-0 top-5 z-50 mx-auto w-full max-w-6xl px-4 sm:px-8">
		<div class="flex items-center justify-between rounded-2xl border border-[#242E43] bg-[#121826]/80 px-4 py-3 backdrop-blur-xl sm:px-5">
			<div class="flex items-center gap-3 group cursor-pointer">
				<div class="flex h-8 w-8 items-center justify-center rounded-md bg-white text-black transition-transform group-hover:scale-105">
					<Zap class="h-4 w-4 fill-current " />
				</div>
				<span class="text-sm font-semibold uppercase tracking-[0.2em] text-[#E8ECF4]">Axon</span>
			</div>
			
			<div class="flex items-center gap-4">
				<a href="/login" class="hidden text-sm font-medium text-[#A3ADBF] transition-colors hover:text-[#E8ECF4] sm:block">
					Sign in
				</a>
				<a href="/signup" class="group inline-flex items-center gap-2 rounded-md bg-white text-black px-4 py-2 text-sm font-semibold  transition-colors hover:bg-gray-200">
					<span class="relative z-10 flex items-center gap-2">
						Get today's brief <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
					</span>
				</a>
			</div>
		</div>
	</header>

	<!-- SECTION 1: THE HOOK (Hero) -->
	<section class="relative z-10 mx-auto flex min-h-[100vh] w-full max-w-5xl flex-col items-center justify-center px-5 pt-20 text-center sm:px-8">
		
		<div class="mb-8 inline-flex cursor-default items-center gap-2 rounded-full border border-[#33415C] bg-[#121826]/80 px-3 py-1.5 text-xs font-medium text-[#A3ADBF]">
			<span class="relative flex h-2.5 w-2.5">
				<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#22C3A6] opacity-70"></span>
				<span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#22C3A6]"></span>
			</span>
			<span class="tracking-wide">LIVE: Tracking global tech signals</span>
		</div>

		<h1 class="max-w-4xl text-4xl font-bold leading-tight tracking-tight text-[#E8ECF4] sm:text-6xl">
			Track where the world is moving. <br />
			<span class="bg-gradient-to-r from-[#5B8CFF] via-[#A3ADBF] to-[#22C3A6] bg-clip-text text-transparent">Stay on the leading edge.</span>
		</h1>
		
		<p class="mt-6 max-w-2xl text-base font-normal leading-7 text-[#A3ADBF] sm:text-lg">
			Built for founders and anyone who wants to stay ahead, AXON turns <span class="text-[#E8ECF4]">AI, tech, research, and GitHub signals</span> into a 3-minute daily brief so you don't need to juggle 50 sites.
		</p>

		<div class="mt-8 flex w-full max-w-sm flex-col items-center gap-3">
			<a href="/signup" class="group inline-flex h-12 w-full items-center justify-center gap-2 rounded-md bg-white text-black px-6 text-sm font-semibold  transition-colors hover:bg-gray-200">
				Start for free
				<ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
			</a>
			<button class="group inline-flex items-center gap-2 text-sm font-medium text-[#7B8497] transition-colors hover:text-[#A3ADBF]">
				<Play class="h-4 w-4 transition-transform group-hover:scale-110" />
				See how it works
			</button>
		</div>

		<!-- Social Proof -->
		<div class="mt-10 flex items-center gap-4 text-sm font-medium text-[#7B8497]">
			<div class="flex -space-x-3">
				<div class="h-8 w-8 rounded-full border-2 border-[#0B0F17] bg-[#242E43]"></div>
				<div class="h-8 w-8 rounded-full border-2 border-[#0B0F17] bg-[#33415C]"></div>
				<div class="h-8 w-8 rounded-full border-2 border-[#0B0F17] bg-[#7C8598]"></div>
				<div class="flex h-8 w-8 items-center justify-center rounded-full border-2 border-[#0B0F17] bg-[#121826]">
					<Users class="h-3 w-3 text-[#A3ADBF]" />
				</div>
			</div>
			<p>Joined by <span class="font-semibold text-[#E8ECF4]">2,400+</span> elite builders</p>
		</div>
	</section>

	<!-- SECTION 2: THE SOURCES (Bento Grid Style) -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-5 py-24 sm:px-8">
		<div class="mb-12 text-center">
			<div class="mb-5 inline-flex items-center gap-2 rounded-full border border-[#33415C] bg-[#121826] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#7B8497]">
				<span class="h-1.5 w-1.5 rounded-full bg-[#22C3A6]"></span> Phase 1: Ingestion
			</div>
			<h2 class="text-3xl font-semibold tracking-tight text-[#E8ECF4] sm:text-4xl">Tap the global firehose.</h2>
			<p class="mx-auto mt-4 max-w-2xl text-base leading-7 text-[#A3ADBF] sm:text-lg">
				Stop checking 15 different sites. AXON continuously monitors the raw nodes where frontier technology is built, debated, and shipped.
			</p>
		</div>

		<div class="mx-auto grid max-w-5xl grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
			{#each [
				{ name: 'HackerNews', desc: 'Frontpage & Show HN', icon: Terminal, style: 'md:col-span-2 md:row-span-2 p-8' },
				{ name: 'GitHub', desc: 'Trending Repositories', icon: Github, style: 'p-6' },
				{ name: 'ArXiv', desc: 'New AI/ML Papers', icon: Layers, style: 'p-6' },
				{ name: 'ProductHunt', desc: 'Top daily launches', icon: Globe, style: 'p-6' },
				{ name: 'OpenAI', desc: 'Research Updates', icon: Cpu, style: 'p-6' },
			] as source}
				<div class="group flex cursor-default flex-col justify-between rounded-2xl border border-[#242E43] bg-[#121826]/90 transition-colors duration-200 hover:border-[#33415C] hover:bg-[#1A2233] {source.style}">
					<source.icon class="h-8 w-8 text-[#7B8497] transition-colors group-hover:text-[#5B8CFF]" />
					<div class="mt-8">
						<h3 class="text-lg font-semibold text-[#E8ECF4]">{source.name}</h3>
						<p class="mt-2 text-xs font-medium uppercase tracking-wider text-[#7B8497]">{source.desc}</p>
					</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- SECTION 3: THE ENGINE -->
	<section class="relative z-10 mx-auto w-full max-w-6xl px-5 py-20 sm:px-8">
		<div class="overflow-hidden rounded-[1.75rem] border border-[#242E43] bg-[#121826]/90 backdrop-blur-xl">
			<div class="grid lg:grid-cols-2 items-stretch">
				<div class="p-10 sm:p-16 flex flex-col justify-center">
					<div class="mb-6 inline-flex w-max items-center gap-2 rounded-full border border-[#33415C] bg-[#0F1522] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#7B8497]">
						<span class="h-1.5 w-1.5 rounded-full bg-[#5B8CFF]"></span> Phase 2: Synthesis
					</div>
					<h3 class="mb-6 text-3xl font-semibold tracking-tight text-[#E8ECF4] sm:text-4xl">Grok filters the noise.</h3>
					<p class="mb-8 text-base leading-7 text-[#A3ADBF] sm:text-lg">
						99% of the internet is distraction. We pipe thousands of daily signals through a custom <strong class="font-semibold text-[#E8ECF4]">Grok AI engine</strong> to extract raw value.
					</p>
					
					<div class="space-y-5">
						{#each [
							{ title: 'Deduplication', desc: 'Merges 50 articles about the same launch into one core update.' },
							{ title: 'Technical Extraction', desc: 'Pulls out actual benchmark numbers, not marketing fluff.' },
							{ title: 'Actionable Insights', desc: 'Tells you exactly what you need to change in your codebase.' }
						] as feature}
							<div class="flex gap-4">
								<div class="mt-1 flex-shrink-0">
									<div class="flex h-8 w-8 items-center justify-center rounded-full bg-[#0F1522] text-[#22C3A6]">
										<Sparkles class="h-4 w-4" />
									</div>
								</div>
								<div>
									<h4 class="font-semibold text-[#E8ECF4]">{feature.title}</h4>
									<p class="mt-1 text-sm text-[#A3ADBF]">{feature.desc}</p>
								</div>
							</div>
						{/each}
					</div>
				</div>
				
				<!-- Polished Code/Terminal Mockup -->
				<div class="relative flex flex-col justify-center overflow-hidden border-t border-[#242E43] bg-[#0F1522] p-8 sm:p-12 lg:border-l lg:border-t-0">
					<div class="absolute -top-24 -right-24 p-4 opacity-5 pointer-events-none">
						<Cpu class="h-96 w-96 text-white" />
					</div>
					
					<div class="relative z-10 space-y-4 font-mono text-sm">
						<div class="flex items-center gap-2 mb-6">
							<div class="h-3 w-3 rounded-full bg-red-500/80"></div>
							<div class="h-3 w-3 rounded-full bg-yellow-500/80"></div>
							<div class="h-3 w-3 rounded-full bg-green-500/80"></div>
							<span class="ml-2 text-xs text-[#7B8497]">axon-engine.ts</span>
						</div>

						<div class="rounded-xl bg-[#121826] p-4 text-[#7B8497] line-through opacity-75">
							[Analyzing 412 HackerNews comments...]
						</div>
						<div class="rounded-xl bg-[#121826] p-4 text-[#7B8497] line-through opacity-75">
							[Discarding generic opinion piece...]
						</div>
						
						<div class="rounded-xl border border-[#33415C] bg-[#121826] p-5">
							<div class="mb-3 flex items-center gap-2 font-bold text-[#22C3A6]">
								<Zap class="h-4 w-4 fill-current" /> > HIGH SIGNAL DETECTED
							</div>
							<p class="mb-3 leading-relaxed text-[#A3ADBF]">
								<span class="font-semibold text-[#E8ECF4]">OpenAI Structured Outputs</span> reduces JSON schema hallucination by 90%.
							</p>
							<div class="rounded border border-[#242E43] bg-[#0B0F17] p-3 text-xs text-[#A3ADBF]">
								<span class="text-[#5B8CFF]">Action:</span> Update parsing logic. Replace old regex sanitizers with native strict schema validation.
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 4: THE DELIVERY -->
	<section class="relative z-10 mx-auto w-full max-w-4xl px-5 py-24 text-center sm:px-8">
		<div class="mb-6 inline-flex items-center gap-2 rounded-full border border-[#33415C] bg-[#121826] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#7B8497]">
			<span class="h-1.5 w-1.5 rounded-full bg-[#22C3A6]"></span> Phase 3: Delivery
		</div>
		<h2 class="mb-6 text-3xl font-semibold tracking-tight text-[#E8ECF4] sm:text-4xl">Your 3-minute advantage.</h2>
		<p class="mx-auto mb-14 max-w-2xl text-base leading-7 text-[#A3ADBF] sm:text-lg">
			No endless feeds. No doomscrolling. Just a beautifully formatted, highly readable briefing waiting for you when you wake up.
		</p>

		<div class="mx-auto max-w-2xl rounded-2xl border border-[#242E43] bg-[#121826] p-7 text-left sm:p-9">
			<div class="mb-8 flex items-center justify-between border-b border-[#242E43] pb-6">
				<div class="flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-md bg-white text-black">
						<Zap class="h-5 w-5 fill-current" />
					</div>
					<div>
						<h3 class="font-semibold text-[#E8ECF4]">AXON Daily Briefing</h3>
						<p class="text-xs text-[#7B8497]">Today, 8:00 AM</p>
					</div>
				</div>
				<div class="rounded-full bg-[#0F1522] px-3 py-1 text-xs font-semibold text-[#22C3A6]">
					3 min read
				</div>
			</div>
			
			<div class="space-y-8">
				<div>
					<h4 class="mb-3 text-xl font-semibold text-[#E8ECF4]">1. GitHub Copilot adds o1-preview support</h4>
					<div class="space-y-3">
						<p class="leading-relaxed text-[#A3ADBF]">
							<strong class="text-[#E8ECF4]">The shift:</strong> Copilot now utilizes OpenAI's reasoning model for complex architectural refactoring.
						</p>
						<p class="leading-relaxed text-[#A3ADBF]">
							<strong class="text-[#E8ECF4]">Why it matters:</strong> You can now prompt for full multi-file structural changes rather than just inline autocomplete.
						</p>
					</div>
					<div class="mt-4 flex gap-2">
						<span class="inline-flex items-center gap-1 rounded-md bg-[#0F1522] px-2.5 py-1 text-[11px] font-mono font-medium text-[#A3ADBF]"><Github class="h-3 w-3" /> GitHub Blog</span>
						<span class="inline-flex items-center gap-1 rounded-md bg-[#3D3112] px-2.5 py-1 text-[11px] font-mono font-medium text-[#F59E0B]"><Terminal class="h-3 w-3" /> HackerNews (#1)</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- SECTION 5: FINAL CTA -->
	<section class="relative z-10 mx-auto mb-20 w-full max-w-5xl px-5 py-20 text-center sm:px-8">
		<div class="relative overflow-hidden rounded-[2rem] border border-[#242E43] bg-[#121826]/90 p-10 backdrop-blur-xl sm:p-16">
			<div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#5B8CFF]/10 to-transparent"></div>
			
			<div class="relative z-10">
				<h2 class="mb-6 text-3xl font-semibold tracking-tight text-[#E8ECF4] sm:text-5xl">
					Ready to plug in?
				</h2>
				<p class="mx-auto mb-10 max-w-xl text-base leading-7 text-[#A3ADBF] sm:text-lg">
					Join thousands of elite builders who use AXON to stay ahead of the curve without sacrificing their time.
				</p>
				<a href="/signup" class="inline-flex h-12 items-center justify-center gap-3 rounded-md bg-white text-black px-8 text-base font-semibold  transition-colors hover:bg-gray-200">
					Join for free
					<ArrowRight class="h-5 w-5" />
				</a>
				<p class="mt-6 text-sm text-[#7B8497]">100% Free. No credit card required. Unsubscribe anytime.</p>
			</div>
		</div>
	</section>

</div>