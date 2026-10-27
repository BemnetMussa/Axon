<script lang="ts">
	import { onMount } from 'svelte';
	import { reveal } from '$lib/actions/reveal';
	import { ArrowRight, Zap } from 'lucide-svelte';
	import IntakeMachine from '$lib/components/hero/IntakeMachine.svelte';
	import FeatureShowcase from '$lib/components/hero/FeatureShowcase.svelte';
	import { sweepAgo, sweepIn } from '$lib/pulse';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const SITE_URL = 'https://axon-phi-ruby.vercel.app';
	const TITLE = 'AXON — Everything is scanned. Little gets through.';
	const DESC =
		'Axon sweeps AI labs, ArXiv, GitHub and Hacker News every few hours. A filter we built drops the reposts, listicles and hype. You read what is left.';

	let now = $state(Date.now());
	let clock = $state('');

	onMount(() => {
		const tick = () => {
			now = Date.now();
			clock = new Date(now).toISOString().slice(11, 19);
		};
		tick();
		const id = setInterval(tick, 1000);
		return () => clearInterval(id);
	});

	let pulse = $derived(data.pulse);
	let lastAgo = $derived(sweepAgo(pulse?.last_sweep_at, now));
	let nextIn = $derived(pulse?.next_sweep_at ? sweepIn(pulse.next_sweep_at, now) : null);
	let interval = $derived(pulse?.interval_hours ?? null);
	let sourceCount = $derived(pulse?.sources && pulse.sources > 0 ? pulse.sources : 17);

	let since = $derived(
		pulse?.running_since ? new Date(pulse.running_since).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : null
	);

	let steps = $derived([
		{
			n: '01',
			name: 'Sweep',
			body: `All ${sourceCount} sources are fetched at once${interval ? `, every ${interval} hours` : ''}: lab blogs, new ArXiv papers, GitHub repos created this month, Hacker News, Lobsters, Product Hunt and a few news desks.`,
			stat: pulse?.last_sweep_at ? `Last sweep: ${pulse.last_scanned} candidates` : 'About 150 candidates a sweep'
		},
		{
			n: '02',
			name: 'Cut',
			body: 'Junk rules run before anything else. Content farms (Medium, dev.to, LinkedIn) and fluff titles (tutorials, roadmaps, career posts, awesome lists) are dropped. A high star count does not buy an exception.',
			stat: 'Rules run first'
		},
		{
			n: '03',
			name: 'Collapse',
			body: 'When two sources carry the same story, their titles overlap. Above 60% overlap, only the higher-scored copy survives. Anything already in the feed is skipped.',
			stat: 'One story, one card'
		},
		{
			n: '04',
			name: 'Rank',
			body: 'Each candidate gets one score from traction, freshness and source trust (formula below). No source can take more than eight slots in a sweep, so one loud feed cannot drown the rest.',
			stat: 'Max 8 per source'
		},
		{
			n: '05',
			name: 'Brief',
			body: 'Survivors get their full text fetched and a brief written from it, then indexed by meaning so search finds ideas, not just keywords. The chat on each story reads that article only.',
			stat: pulse?.last_sweep_at ? `Last sweep: ${pulse.last_kept} kept` : 'Up to 100 kept a sweep'
		}
	]);

	const cut = [
		{ title: '15 prompts that will 10x your productivity', why: 'Listicle' },
		{ title: 'My roadmap to becoming an AI engineer in 2026', why: 'Career' },
		{ title: 'awesome-llm-resources', why: 'Evergreen list' },
		{ title: 'The same model launch, reposted on four sites', why: 'Duplicate ×4' },
		{ title: 'This changes everything. Here is why.', why: 'Hype' }
	];

	const kept = [
		{ src: 'ArXiv', title: 'Tool-use accuracy falls off a cliff past 40 tools', why: 'New result' },
		{ src: 'GitHub', title: 'A voice agent that answers in under a second on a laptop', why: '2.1k stars in 6 days' },
		{ src: 'Anthropic', title: 'Notes on how the new model handles long tasks', why: 'Primary source' },
		{ src: 'Hacker News', title: 'What people actually ran on the small reasoning models', why: '412 points' }
	];

	const channels = [
		{ ch: '01', name: 'Hacker News', what: 'Front page, plus Ask and Show HN threads with real discussion' },
		{ ch: '02', name: 'GitHub', what: 'Repos created this month that are already pulling stars' },
		{ ch: '03', name: 'ArXiv', what: 'New cs.AI and cs.LG papers' },
		{ ch: '04', name: 'AI labs', what: 'OpenAI, Anthropic, DeepMind, Google AI, Google Research, Hugging Face, NVIDIA, Together AI' },
		{ ch: '05', name: 'People', what: 'Simon Willison. Only voices that post often and stay fresh' },
		{ ch: '06', name: 'Launches & news', what: 'Product Hunt, Lobsters, TechCrunch, The Verge, Ars Technica' }
	];

	function scrollTo(id: string) {
		return (e: MouseEvent) => {
			e.preventDefault();
			document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
		};
	}
</script>

<svelte:head>
	<title>{TITLE}</title>
	<meta name="description" content={DESC} />
	<meta property="og:type" content="website" />
	<meta property="og:site_name" content="AXON" />
	<meta property="og:title" content={TITLE} />
	<meta property="og:description" content={DESC} />
	<meta property="og:url" content={SITE_URL} />
	<meta property="og:image" content="{SITE_URL}/og.png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={TITLE} />
	<meta name="twitter:description" content={DESC} />
	<meta name="twitter:image" content="{SITE_URL}/og.png" />
	<link rel="canonical" href={SITE_URL} />
</svelte:head>

<div class="landing min-h-screen w-full overflow-x-hidden bg-[#fafafa] font-sans text-[#0a0a0a] antialiased selection:bg-black selection:text-white dark:bg-[#0a0a0a] dark:text-[#ededed] dark:selection:bg-white dark:selection:text-black">
	<!-- Header -->
	<header class="fixed inset-x-0 top-0 z-50 border-b border-black/10 bg-[#fafafa]/85 backdrop-blur-md dark:border-white/10 dark:bg-[#0a0a0a]/85">
		<div class="mx-auto flex h-14 w-full max-w-7xl items-center justify-between gap-4 px-5 sm:px-8">
			<a href="/" class="flex items-center gap-2.5">
				<span class="flex h-7 w-7 items-center justify-center bg-black text-white dark:bg-white dark:text-black">
					<Zap class="h-3.5 w-3.5 fill-current" />
				</span>
				<span class="text-[13px] font-semibold uppercase tracking-[0.24em]">Axon</span>
			</a>

			<div class="axon-label hidden items-center gap-5 text-black/55 md:flex dark:text-white/50">
				<span class="flex items-center gap-2 text-black dark:text-white"><span class="axon-live"></span>Filter running</span>
				<span>Last sweep {lastAgo}</span>
				<span class="tabular-nums">{clock || '--:--:--'} UTC</span>
			</div>

			<div class="flex items-center gap-1 sm:gap-2">
				<a href="/login" class="hidden px-3 py-2 text-sm text-black/60 transition-colors hover:text-black sm:block dark:text-white/60 dark:hover:text-white">Sign in</a>
				<a href="/signup" class="group inline-flex h-9 items-center gap-2 bg-black px-4 text-sm font-medium text-white transition-colors hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/85">
					Open the feed
					<ArrowRight class="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
				</a>
			</div>
		</div>
	</header>

	<!-- Hero -->
	<section class="mx-auto w-full max-w-7xl px-5 pt-28 sm:px-8 sm:pt-36">
		<p use:reveal class="axon-label mb-8 flex items-center gap-3 text-black/50 dark:text-white/45">
			<span class="h-px w-8 bg-current"></span>
			{sourceCount} sources · {interval ? `swept every ${interval}h` : 'swept on a schedule'}{since ? ` · running since ${since}` : ''}
		</p>

		<h1 use:reveal={{ delay: 60 }} class="max-w-4xl text-[44px] font-semibold leading-[0.98] tracking-[-0.045em] sm:text-7xl lg:text-[88px]">
			Everything is scanned.<br />
			<span class="text-black/35 dark:text-white/35">Little gets through.</span>
		</h1>

		<div use:reveal={{ delay: 140 }} class="mt-8 grid gap-8 sm:mt-10 lg:grid-cols-[1fr_auto] lg:items-end">
			<p class="max-w-xl text-lg leading-relaxed text-black/65 dark:text-white/60">
				Axon reads the labs, the papers, GitHub and Hacker News around the clock. A filter we built drops the reposts,
				listicles and hype, and keeps what actually moved. You read what is left.
			</p>
			<div class="flex flex-col gap-3 sm:flex-row">
				<a href="/signup" class="group inline-flex h-12 items-center justify-center gap-2 bg-black px-6 text-sm font-medium text-white transition-colors hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/85">
					Open the feed
					<ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
				</a>
				<a href="#ledger" onclick={scrollTo('ledger')} class="inline-flex h-12 items-center justify-center border border-black/20 px-6 text-sm text-black/70 transition-colors hover:border-black hover:text-black dark:border-white/20 dark:text-white/70 dark:hover:border-white dark:hover:text-white">
					See what gets cut
				</a>
			</div>
		</div>
	</section>

	<!-- Intake: sources → Axon → feed -->
	<section class="mx-auto w-full max-w-7xl px-5 pt-14 sm:px-8 sm:pt-20">
		<div use:reveal={{ delay: 200 }}>
			<IntakeMachine {pulse} />
		</div>
	</section>

	<!-- How the filter works -->
	<section id="filter" class="mx-auto w-full max-w-7xl scroll-mt-20 px-5 pt-28 sm:px-8 sm:pt-36">
		<div use:reveal class="mb-12 grid gap-4 lg:grid-cols-[280px_1fr]">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">The filter</p>
			<h2 class="max-w-2xl text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">
				Five steps between the internet and your feed.
			</h2>
		</div>

		<ol class="grid border-t border-black/10 sm:grid-cols-2 lg:grid-cols-5 dark:border-white/10">
			{#each steps as step, i}
				<li use:reveal={{ delay: i * 60 }} class="flex flex-col border-b border-black/10 py-6 sm:pr-6 lg:border-b-0 lg:border-r lg:px-5 lg:py-8 lg:first:pl-0 lg:last:border-r-0 dark:border-white/10">
					<div class="flex items-baseline justify-between">
						<span class="axon-label text-black/40 dark:text-white/35">{step.n}</span>
						<span class="h-px flex-1 translate-y-[-3px] bg-black/10 mx-3 lg:hidden dark:bg-white/10"></span>
					</div>
					<h3 class="mt-4 text-xl font-semibold tracking-tight">{step.name}</h3>
					<p class="mt-3 flex-1 text-[15px] leading-relaxed text-black/60 dark:text-white/55">{step.body}</p>
					<p class="axon-label mt-6 border-t border-black/10 pt-3 text-black/70 dark:border-white/10 dark:text-white/65">{step.stat}</p>
				</li>
			{/each}
		</ol>

		<div use:reveal class="mt-16 grid gap-10 lg:grid-cols-[280px_1fr]">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">The score</p>
			<div>
				<p class="font-mono text-lg tracking-tight sm:text-2xl">
					score = trust <span class="text-black/35 dark:text-white/35">×</span> (0.55 <span class="text-black/35 dark:text-white/35">×</span> traction + 0.45 <span class="text-black/35 dark:text-white/35">×</span> freshness)
				</p>
				<dl class="mt-8 grid border-t border-black/10 sm:grid-cols-3 dark:border-white/10">
					<div class="border-b border-black/10 py-5 sm:border-b-0 sm:border-r sm:pr-6 dark:border-white/10">
						<dt class="text-[15px] font-semibold">Traction</dt>
						<dd class="mt-2 text-[15px] leading-relaxed text-black/60 dark:text-white/55">Points, stars or votes, compared only against the same source in the same sweep. So 300 Hacker News points and 3,000 GitHub stars can be ranked fairly.</dd>
					</div>
					<div class="border-b border-black/10 py-5 sm:border-b-0 sm:border-r sm:px-6 dark:border-white/10">
						<dt class="text-[15px] font-semibold">Freshness</dt>
						<dd class="mt-2 text-[15px] leading-relaxed text-black/60 dark:text-white/55">Decays over about three days. A story from this morning beats the same story from last week.</dd>
					</div>
					<div class="py-5 sm:pl-6">
						<dt class="text-[15px] font-semibold">Trust</dt>
						<dd class="mt-2 text-[15px] leading-relaxed text-black/60 dark:text-white/55">Primary sources (labs and papers) weigh more than aggregators, and aggregators more than news rewrites. Blogs with no vote count lean on freshness and trust.</dd>
					</div>
				</dl>
			</div>
		</div>
	</section>

	<!-- Ledger: cut vs kept -->
	<section id="ledger" class="mx-auto w-full max-w-7xl scroll-mt-20 px-5 pt-28 sm:px-8 sm:pt-36">
		<div use:reveal class="mb-12 grid gap-4 lg:grid-cols-[280px_1fr]">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">One sweep, in short</p>
			<div>
				<h2 class="max-w-2xl text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">Most of it never reaches you.</h2>
				<p class="mt-4 text-sm text-black/45 dark:text-white/40">Illustrative examples of what the filter does. The live feed is inside.</p>
			</div>
		</div>

		<div class="grid border border-black/10 lg:grid-cols-2 dark:border-white/10">
			<div use:reveal class="border-b border-black/10 lg:border-b-0 lg:border-r dark:border-white/10">
				<div class="axon-label flex items-center justify-between border-b border-black/10 px-5 py-3 text-black/45 dark:border-white/10 dark:text-white/40">
					<span>Cut</span>
					<span>Reason</span>
				</div>
				<ul>
					{#each cut as row}
						<li class="flex items-baseline justify-between gap-6 border-b border-black/5 px-5 py-4 last:border-b-0 dark:border-white/5">
							<span class="text-[15px] text-black/35 line-through decoration-black/30 dark:text-white/30 dark:decoration-white/25">{row.title}</span>
							<span class="axon-label shrink-0 text-black/40 dark:text-white/35">{row.why}</span>
						</li>
					{/each}
				</ul>
			</div>
			<div use:reveal={{ delay: 80 }}>
				<div class="axon-label flex items-center justify-between border-b border-black/10 px-5 py-3 text-black/45 dark:border-white/10 dark:text-white/40">
					<span class="flex items-center gap-2 text-black dark:text-white"><span class="h-1.5 w-1.5 bg-current"></span>Kept</span>
					<span>Why</span>
				</div>
				<ul>
					{#each kept as row}
						<li class="flex items-baseline justify-between gap-6 border-b border-black/5 px-5 py-4 last:border-b-0 dark:border-white/5">
							<span class="min-w-0">
								<span class="axon-label mr-2 text-black/45 dark:text-white/40">{row.src}</span>
								<span class="text-[15px] font-medium">{row.title}</span>
							</span>
							<span class="axon-label shrink-0 text-black/60 dark:text-white/55">{row.why}</span>
						</li>
					{/each}
				</ul>
			</div>
		</div>
	</section>

	<!-- Channels -->
	<section class="mx-auto w-full max-w-7xl px-5 pt-28 sm:px-8 sm:pt-36">
		<div use:reveal class="mb-12 grid gap-4 lg:grid-cols-[280px_1fr]">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">Channels</p>
			<h2 class="max-w-2xl text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">Where we listen.</h2>
		</div>

		<ul class="border-t border-black/10 dark:border-white/10">
			{#each channels as c, i}
				<li use:reveal={{ delay: i * 40 }} class="grid grid-cols-[48px_1fr] items-baseline gap-x-4 gap-y-1 border-b border-black/10 py-5 sm:grid-cols-[80px_240px_1fr] dark:border-white/10">
					<span class="axon-label text-black/40 dark:text-white/35">CH {c.ch}</span>
					<span class="text-lg font-medium tracking-tight">{c.name}</span>
					<span class="col-start-2 text-[15px] text-black/55 sm:col-start-auto dark:text-white/50">{c.what}</span>
				</li>
			{/each}
		</ul>
	</section>

	<!-- What you get -->
	<section id="features" class="mx-auto w-full max-w-7xl scroll-mt-20 px-5 pt-28 sm:px-8 sm:pt-36">
		<div use:reveal class="mb-16 grid gap-4 lg:grid-cols-[280px_1fr] sm:mb-24">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">What you get</p>
			<div>
				<h2 class="max-w-2xl text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">What reaches you, and what you can do with it.</h2>
				<p class="mt-4 text-sm text-black/45 dark:text-white/40">These are the app's own screens. The story and its brief are real, from the feed on Oct 6; the chat answer and digest summary are examples.</p>
			</div>
		</div>
		<FeatureShowcase />
	</section>

	<!-- CTA -->
	<section class="mx-auto w-full max-w-7xl px-5 py-28 sm:px-8 sm:py-36">
		<div use:reveal class="axon-corners border border-black/10 px-6 py-14 text-center sm:py-20 dark:border-white/10">
			<p class="axon-label flex items-center justify-center gap-2 text-black/50 dark:text-white/45">
				<span class="axon-live text-black dark:text-white"></span>
				Last sweep {lastAgo}{nextIn ? ` · next ${nextIn}` : ''}
			</p>
			<h2 class="mx-auto mt-6 max-w-2xl text-4xl font-semibold leading-tight tracking-[-0.04em] sm:text-6xl">The filter is already running.</h2>
			<a href="/signup" class="group mt-10 inline-flex h-12 items-center justify-center gap-2 bg-black px-7 text-sm font-medium text-white transition-colors hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/85">
				Open the feed
				<ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
			</a>
			<p class="mt-4 text-sm text-black/45 dark:text-white/40">Free. No credit card.</p>
		</div>
	</section>

	<footer class="border-t border-black/10 dark:border-white/10">
		<div class="mx-auto flex w-full max-w-7xl flex-col gap-6 px-5 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-8">
			<div class="flex items-center gap-2.5">
				<span class="flex h-6 w-6 items-center justify-center bg-black text-white dark:bg-white dark:text-black">
					<Zap class="h-3 w-3 fill-current" />
				</span>
				<span class="axon-label text-black/50 dark:text-white/45">Axon · © 2026 Bemnet Mussa</span>
			</div>
			<nav class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-black/50 dark:text-white/45">
				<a href="/privacy" class="hover:text-black dark:hover:text-white">Privacy</a>
				<a href="/terms" class="hover:text-black dark:hover:text-white">Terms</a>
				<a href="/login" class="hover:text-black dark:hover:text-white">Sign in</a>
				<a href="/signup" class="hover:text-black dark:hover:text-white">Open the feed</a>
			</nav>
		</div>
	</footer>
</div>
