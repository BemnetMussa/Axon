<script lang="ts">
	import { onMount } from 'svelte';
	import { reveal } from '$lib/actions/reveal';
	import { ArrowRight, Zap } from 'lucide-svelte';
	import SignalTrace from '$lib/components/ui/SignalTrace.svelte';
	import { sweepAgo, sweepIn, keptPercent, pulseWindow, formatCount } from '$lib/pulse';
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
	let win = $derived(pulseWindow(pulse));
	let pct = $derived(win ? keptPercent(win.scanned, win.kept) : null);
	let lastAgo = $derived(sweepAgo(pulse?.last_sweep_at, now));
	let nextIn = $derived(pulse?.next_sweep_at ? sweepIn(pulse.next_sweep_at, now) : null);
	let interval = $derived(pulse?.interval_hours ?? 4);
	let sourceCount = $derived(pulse?.sources && pulse.sources > 0 ? pulse.sources : 25);

	let inLabel = $derived(win ? `In · ${formatCount(win.scanned)} items` : 'In · everything');
	let outLabel = $derived(win ? `Out · ${formatCount(win.kept)} kept` : 'Out · what matters');

	const steps = [
		{
			n: '01',
			name: 'Sweep',
			body: `Lab blogs, ArXiv, GitHub, Hacker News, Lobsters, Product Hunt and a short list of people worth reading. All fetched at once, every few hours.`
		},
		{
			n: '02',
			name: 'Cut',
			body: 'Listicles, tutorials, career posts, roadmaps and “awesome” lists are dropped first. Popularity does not buy them back in.'
		},
		{
			n: '03',
			name: 'Collapse',
			body: 'The same launch posted on five sites becomes one story. The strongest copy stays.'
		},
		{
			n: '04',
			name: 'Rank',
			body: 'Traction measured inside its own source, how fresh it is, and how much we trust where it came from. No source gets more than eight slots.'
		},
		{
			n: '05',
			name: 'Brief',
			body: 'What survives gets a brief written from the full article, and a chat that only talks about that story.'
		}
	];

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
		{ ch: '04', name: 'AI labs', what: 'OpenAI, Anthropic, DeepMind, Google, Hugging Face, NVIDIA' },
		{ ch: '05', name: 'People', what: 'Karpathy, Simon Willison, Lilian Weng, fast.ai, BAIR' },
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
		<div class="mx-auto flex h-14 w-full max-w-6xl items-center justify-between gap-4 px-5 sm:px-8">
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
	<section class="mx-auto w-full max-w-6xl px-5 pt-28 sm:px-8 sm:pt-36">
		<p use:reveal class="axon-label mb-8 flex items-center gap-3 text-black/50 dark:text-white/45">
			<span class="h-px w-8 bg-current"></span>
			{sourceCount} sources · swept every {interval}h · one feed
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

	<!-- Instrument -->
	<section class="mx-auto w-full max-w-6xl px-5 pt-14 sm:px-8 sm:pt-20">
		<div use:reveal={{ delay: 200 }} class="axon-corners border border-black/10 dark:border-white/10">
			<div class="axon-label flex items-center justify-between border-b border-black/10 px-4 py-3 text-black/50 sm:px-5 dark:border-white/10 dark:text-white/45">
				<span>Input · {sourceCount} sources</span>
				<span class="hidden sm:inline">Axon filter</span>
				<span>Output · your feed</span>
			</div>

			<div class="px-4 pb-4 pt-8 sm:px-5 sm:pt-10 [--trace-bg:#fafafa] dark:[--trace-bg:#0a0a0a]">
				<SignalTrace class="h-36 sm:h-52" {inLabel} {outLabel} />
			</div>

			<dl class="grid grid-cols-2 border-t border-black/10 md:grid-cols-4 dark:border-white/10">
				<div class="border-b border-r border-black/10 px-4 py-5 sm:px-5 md:border-b-0 dark:border-white/10">
					<dt class="axon-label text-black/45 dark:text-white/40">Last sweep</dt>
					<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">{lastAgo}</dd>
				</div>
				<div class="border-b border-black/10 px-4 py-5 sm:px-5 md:border-b-0 md:border-r dark:border-white/10">
					<dt class="axon-label text-black/45 dark:text-white/40">Scanned{win ? ` · ${win.label}` : ''}</dt>
					<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">{win ? formatCount(win.scanned) : '—'}</dd>
				</div>
				<div class="border-r border-black/10 px-4 py-5 sm:px-5 dark:border-white/10">
					<dt class="axon-label text-black/45 dark:text-white/40">Kept</dt>
					<dd class="mt-2 flex items-baseline gap-2 text-2xl font-medium tracking-tight tabular-nums">
						{win ? formatCount(win.kept) : '—'}
						{#if pct !== null}<span class="axon-label text-black/45 dark:text-white/40">{pct}%</span>{/if}
					</dd>
				</div>
				<div class="px-4 py-5 sm:px-5">
					<dt class="axon-label text-black/45 dark:text-white/40">Next sweep</dt>
					<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">{nextIn ?? `every ${interval}h`}</dd>
				</div>
			</dl>
		</div>
	</section>

	<!-- How the filter works -->
	<section id="filter" class="mx-auto w-full max-w-6xl scroll-mt-20 px-5 pt-28 sm:px-8 sm:pt-36">
		<div use:reveal class="mb-12 grid gap-4 lg:grid-cols-[280px_1fr]">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">The filter</p>
			<h2 class="max-w-2xl text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">
				Five steps between the internet and your feed.
			</h2>
		</div>

		<ol class="grid border-t border-black/10 sm:grid-cols-2 lg:grid-cols-5 dark:border-white/10">
			{#each steps as step, i}
				<li use:reveal={{ delay: i * 60 }} class="border-b border-black/10 py-6 sm:pr-6 lg:border-b-0 lg:border-r lg:px-5 lg:py-8 lg:first:pl-0 lg:last:border-r-0 dark:border-white/10">
					<div class="flex items-baseline justify-between">
						<span class="axon-label text-black/40 dark:text-white/35">{step.n}</span>
						<span class="h-px flex-1 translate-y-[-3px] bg-black/10 mx-3 lg:hidden dark:bg-white/10"></span>
					</div>
					<h3 class="mt-4 text-xl font-semibold tracking-tight">{step.name}</h3>
					<p class="mt-3 text-[15px] leading-relaxed text-black/60 dark:text-white/55">{step.body}</p>
					<div class="mt-6 h-[3px] bg-black/10 dark:bg-white/10">
						<div class="h-full bg-black dark:bg-white" style={`width: ${[100, 58, 44, 26, 26][i]}%`}></div>
					</div>
				</li>
			{/each}
		</ol>
	</section>

	<!-- Ledger: cut vs kept -->
	<section id="ledger" class="mx-auto w-full max-w-6xl scroll-mt-20 px-5 pt-28 sm:px-8 sm:pt-36">
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
	<section class="mx-auto w-full max-w-6xl px-5 pt-28 sm:px-8 sm:pt-36">
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

	<!-- Ask -->
	<section class="mx-auto w-full max-w-6xl px-5 pt-28 sm:px-8 sm:pt-36">
		<div class="grid gap-10 lg:grid-cols-[280px_1fr]">
			<p use:reveal class="axon-label pt-2 text-black/45 dark:text-white/40">Then ask it</p>
			<div class="grid gap-10 lg:grid-cols-2 lg:items-start">
				<div use:reveal>
					<h2 class="text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">Every story you can question.</h2>
					<p class="mt-5 max-w-md text-[15px] leading-relaxed text-black/60 dark:text-white/55">
						Each kept story comes with a brief written from the full article. Ask it what changed, who it affects, or whether
						it matters for what you are building. The answers stay on that story.
					</p>
				</div>

				<article use:reveal={{ delay: 80 }} class="axon-corners border border-black/10 dark:border-white/10">
					<div class="axon-label flex items-center justify-between border-b border-black/10 px-5 py-3 text-black/45 dark:border-white/10 dark:text-white/40">
						<span>ArXiv · cs.AI</span>
						<span>Example</span>
					</div>
					<div class="px-5 py-6">
						<h3 class="text-xl font-semibold leading-snug tracking-tight">Tool-use accuracy falls off a cliff past 40 tools</h3>
						<div class="mt-6 space-y-3">
							<p class="ml-auto w-fit max-w-[85%] bg-black px-3.5 py-2.5 text-sm text-white dark:bg-white dark:text-black">
								Does this matter if my agent has 12 tools?
							</p>
							<p class="max-w-[92%] border border-black/10 px-3.5 py-2.5 text-sm leading-relaxed text-black/70 dark:border-white/10 dark:text-white/65">
								Not much yet. The drop starts past roughly 40. At 12 the paper sees near-baseline accuracy, so you get more out of
								clear tool descriptions than out of trimming the list.
							</p>
						</div>
					</div>
				</article>
			</div>
		</div>
	</section>

	<!-- CTA -->
	<section class="mx-auto w-full max-w-6xl px-5 py-28 sm:px-8 sm:py-36">
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
		<div class="mx-auto flex w-full max-w-6xl flex-col gap-6 px-5 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-8">
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
