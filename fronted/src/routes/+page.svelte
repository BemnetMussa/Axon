<script lang="ts">
	import { onMount } from 'svelte';
	import { reveal } from '$lib/actions/reveal';
	import { ArrowRight } from 'lucide-svelte';
	import AxonMark from '$lib/components/ui/AxonMark.svelte';
	import IntakeMachine from '$lib/components/hero/IntakeMachine.svelte';
	import FeatureShowcase from '$lib/components/hero/FeatureShowcase.svelte';
	import { sweepAgo, sweepIn } from '$lib/pulse';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const SITE_URL = 'https://axon-phi-ruby.vercel.app';
	const TITLE = 'AXON — You can’t keep up with everything. You don’t have to.';
	const DESC =
		'Axon reads the labs, the papers, GitHub and Hacker News every few hours, drops the reposts, listicles and hype, and keeps what actually moved: the breakthroughs, launches and repos worth your time.';

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

	let keptTotal = $derived(pulse?.kept_total ?? null);
	const fmt = (n: number) => n.toLocaleString('en-US');

	const checks = [
		{ n: '01', name: 'New', rule: 'The link is not already in the feed.' },
		{ n: '02', name: 'Recent', rule: 'Published in the last 30 days.' },
		{
			n: '03',
			name: 'Not junk',
			rule: 'Not from a content farm (Medium, dev.to, LinkedIn) and no fluff in the title: tutorials, roadmaps, career posts, awesome-lists. A high star count does not buy an exception.'
		},
		{
			n: '04',
			name: 'Not a repeat',
			rule: 'Two titles from different sources that share 60% or more of their key words are one story. The list is sorted, so the higher-scored copy is already in.'
		},
		{ n: '05', name: 'Under quota', rule: 'At most 5 stories per source and 20 per sweep. The 20 go to the highest scores, so weaker sources drop out first.' }
	];

	const terms = [
		{
			sym: 'e',
			name: 'Traction',
			body: 'Where the story ranks by points, stars or votes within its own source that sweep: 1 for the top, 0 for the bottom. That puts 300 Hacker News points and 3,000 GitHub stars on one scale. Sources without votes sit at 0.5.'
		},
		{
			sym: 'r',
			name: 'Freshness',
			body: 'Decays exponentially with age on a 72-hour scale. A story one day old scores 0.72, three days 0.37, a week 0.10.'
		},
		{
			sym: 'w',
			name: 'Trust',
			body: 'A fixed weight per source, from 0.9 for news rewrites to 1.6 for OpenAI and Anthropic. A fresh lab post lands just below the top Hacker News story of the sweep.'
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
		{ ch: '01', name: 'Hacker News', what: 'Front page, Ask and Show HN' },
		{ ch: '02', name: 'GitHub', what: 'New repos gaining stars' },
		{ ch: '03', name: 'ArXiv', what: 'cs.AI and cs.LG papers' },
		{ ch: '04', name: 'AI labs', what: 'OpenAI, Anthropic, DeepMind, Google, Hugging Face, NVIDIA, Together' },
		{ ch: '05', name: 'People', what: 'Simon Willison' },
		{ ch: '06', name: 'Launches & news', what: 'Product Hunt, Lobsters, TechCrunch, The Verge, Ars Technica' }
	];

	const footerNav = [
		{
			title: 'Product',
			links: [
				{ label: 'Open the feed', href: '/signup' },
				{ label: 'Sign in', href: '/login' },
				{ label: 'What you get', href: '#features' }
			]
		},
		{
			title: 'How it works',
			links: [
				{ label: 'The filter', href: '#filter' },
				{ label: 'What gets cut', href: '#ledger' },
				{ label: 'Where we listen', href: '#channels' }
			]
		},
		{
			title: 'Project',
			links: [
				{ label: 'Source on GitHub', href: 'https://github.com/BemnetMussa/Axon', external: true },
				{ label: 'Privacy', href: '/privacy' },
				{ label: 'Terms', href: '/terms' }
			]
		}
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
	<meta property="og:image" content="{SITE_URL}/og.png?v=2" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={TITLE} />
	<meta name="twitter:description" content={DESC} />
	<meta name="twitter:image" content="{SITE_URL}/og.png?v=2" />
	<link rel="canonical" href={SITE_URL} />
</svelte:head>

<div class="landing min-h-screen w-full overflow-x-hidden bg-[#fafafa] font-sans text-[#0a0a0a] antialiased selection:bg-black selection:text-white dark:bg-[#0a0a0a] dark:text-[#ededed] dark:selection:bg-white dark:selection:text-black">
	<!-- Header -->
	<header class="fixed inset-x-0 top-0 z-50 border-b border-black/10 bg-[#fafafa]/85 backdrop-blur-md dark:border-white/10 dark:bg-[#0a0a0a]/85">
		<div class="mx-auto flex h-14 w-full max-w-7xl items-center justify-between gap-4 px-5 sm:px-8">
			<a href="/" class="flex items-center gap-2.5">
				<span class="flex h-7 w-7 items-center justify-center bg-black text-white dark:bg-white dark:text-black">
					<AxonMark class="h-4 w-4" />
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

		<h1 use:reveal={{ delay: 60 }} class="max-w-5xl text-[40px] font-semibold leading-[1] tracking-[-0.045em] sm:text-6xl lg:text-[76px]">
			You can’t keep up<br class="hidden sm:block" /> with everything.<br />
			<span class="text-black/35 dark:text-white/35">You don’t have to.</span>
		</h1>

		<div use:reveal={{ delay: 140 }} class="mt-8 grid gap-8 sm:mt-10 lg:grid-cols-[1fr_auto] lg:items-end">
			<p class="max-w-xl text-lg leading-relaxed text-black/65 dark:text-white/60">
				Noise is the reposts, listicles and hype. Signal is what actually moved: a breakthrough, a launch, a repo people suddenly use.
				Axon reads the labs, the papers, GitHub and Hacker News {interval ? `every ${interval} hours` : 'on a schedule'} and keeps only the signal.
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
		<div use:reveal class="grid gap-4 lg:grid-cols-[280px_1fr]">
			<p class="axon-label pt-2 text-black/45 dark:text-white/40">The filter</p>
			<div>
				<h2 class="max-w-2xl text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-5xl">One score, then five checks.</h2>
				<p class="mt-6 max-w-2xl text-lg leading-relaxed text-black/65 dark:text-white/60">
					{interval ? `Every ${interval} hours` : 'On each sweep'}, Axon fetches all {sourceCount} sources at once and scores every candidate.
					It sorts the list, then walks down it and admits a story only if it passes all five checks. It stops at 20, so a sweep is something you can actually read. The same score orders the feed: newest day first, best story first within each day.
				</p>
				{#if pulse?.last_sweep_at}
					<p class="axon-label mt-6 flex items-center gap-2 text-black/60 dark:text-white/55">
						<span class="axon-live text-black dark:text-white"></span>
						Last sweep: {fmt(pulse.last_scanned)} scored, {fmt(pulse.last_kept)} admitted
					</p>
				{/if}
			</div>
		</div>

		<!-- 1 · Score -->
		<div use:reveal class="mt-16 grid gap-6 border-t border-black/10 pt-10 lg:grid-cols-[280px_1fr] dark:border-white/10">
			<p class="axon-label text-black/45 dark:text-white/40"><span class="text-black dark:text-white">1</span> · Score</p>
			<div>
				<p class="font-mono text-xl tracking-tight sm:text-3xl">
					score = <i class="font-serif text-[1.1em]">w</i><span class="text-black/35 dark:text-white/35">·</span>(0.55<span class="text-black/35 dark:text-white/35">·</span><i class="font-serif text-[1.1em]">e</i> + 0.45<span class="text-black/35 dark:text-white/35">·</span><i class="font-serif text-[1.1em]">r</i>)
				</p>
				<dl class="mt-8 grid gap-px overflow-hidden border border-black/10 bg-black/10 sm:grid-cols-3 dark:border-white/10 dark:bg-white/10">
					{#each terms as t}
						<div class="bg-[#fafafa] p-5 dark:bg-[#0a0a0a]">
							<dt class="flex items-baseline gap-3">
								<i class="font-serif text-xl">{t.sym}</i>
								<span class="text-[15px] font-semibold">{t.name}</span>
							</dt>
							<dd class="mt-2 text-[15px] leading-relaxed text-black/60 dark:text-white/55">{t.body}</dd>
						</div>
					{/each}
				</dl>
			</div>
		</div>

		<!-- 2 · Admit -->
		<div use:reveal class="mt-14 grid gap-6 border-t border-black/10 pt-10 lg:grid-cols-[280px_1fr] dark:border-white/10">
			<p class="axon-label text-black/45 dark:text-white/40"><span class="text-black dark:text-white">2</span> · Admit, in order</p>
			<ol class="border-t border-black/10 dark:border-white/10">
				{#each checks as c, i}
					<li use:reveal={{ delay: i * 40 }} class="grid grid-cols-[40px_1fr] gap-x-4 gap-y-1 border-b border-black/10 py-4 sm:grid-cols-[48px_180px_1fr] dark:border-white/10">
						<span class="axon-label pt-1 text-black/40 dark:text-white/35">{c.n}</span>
						<span class="text-[15px] font-semibold">{c.name}</span>
						<span class="col-start-2 text-[15px] leading-relaxed text-black/60 sm:col-start-auto dark:text-white/55">{c.rule}</span>
					</li>
				{/each}
			</ol>
		</div>

		<!-- 3 · Brief -->
		<div use:reveal class="mt-14 grid gap-6 border-t border-black/10 pt-10 lg:grid-cols-[280px_1fr] dark:border-white/10">
			<p class="axon-label text-black/45 dark:text-white/40"><span class="text-black dark:text-white">3</span> · Brief</p>
			<p class="max-w-2xl text-[15px] leading-relaxed text-black/60 dark:text-white/55">
				Each admitted story has its full text fetched and a brief written from it. The chat on a story answers from that article only.
			</p>
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
	<section id="channels" class="mx-auto w-full max-w-7xl scroll-mt-20 px-5 pt-24 sm:px-8 sm:pt-28">
		<div use:reveal class="mb-8 flex items-baseline justify-between gap-6 border-b border-black/10 pb-4 dark:border-white/10">
			<h2 class="text-xl font-semibold tracking-tight sm:text-2xl">Where we listen</h2>
			<p class="axon-label text-black/45 dark:text-white/40">{sourceCount} sources · 6 channels</p>
		</div>
		<ul use:reveal class="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 lg:grid-cols-6 lg:gap-x-0">
			{#each channels as c}
				<li class="min-w-0 lg:border-l lg:border-black/10 lg:px-5 lg:first:border-l-0 lg:first:pl-0 dark:lg:border-white/10">
					<p class="axon-label text-black/40 dark:text-white/35">CH {c.ch}</p>
					<p class="mt-2 text-[15px] font-medium tracking-tight">{c.name}</p>
					<p class="mt-1 text-[13px] leading-snug text-black/50 dark:text-white/45">{c.what}</p>
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
	<section class="mx-auto w-full max-w-7xl px-5 pb-28 pt-28 sm:px-8 sm:pb-36 sm:pt-36">
		<div use:reveal class="axon-corners grid border border-black/10 lg:grid-cols-[1.25fr_1fr] dark:border-white/10">
			<div class="flex flex-col justify-between gap-12 px-6 py-12 sm:px-12 sm:py-16">
				<div>
					<p class="axon-label flex items-center gap-2 text-black dark:text-white">
						<span class="axon-live"></span>Filter running
					</p>
					<h2 class="mt-6 max-w-lg text-4xl font-semibold leading-[1.02] tracking-[-0.04em] sm:text-6xl">
						Read what made it through.
					</h2>
					<p class="mt-5 max-w-md text-[15px] leading-relaxed text-black/60 dark:text-white/55">
						The next sweep is already on the clock. Sign up and the feed is there, already sorted.
					</p>
				</div>
				<div class="flex flex-col gap-3 sm:flex-row sm:items-center">
					<a href="/signup" class="group inline-flex h-12 items-center justify-center gap-2 bg-black px-7 text-sm font-medium text-white transition-colors hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/85">
						Open the feed
						<ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
					</a>
					<a href="/login" class="inline-flex h-12 items-center justify-center border border-black/20 px-6 text-sm text-black/70 transition-colors hover:border-black hover:text-black dark:border-white/20 dark:text-white/70 dark:hover:border-white dark:hover:text-white">
						Sign in
					</a>
					<span class="axon-label text-black/45 sm:ml-3 dark:text-white/40">Free · No card</span>
				</div>
			</div>

			<dl class="grid grid-cols-2 border-t border-black/10 lg:border-l lg:border-t-0 dark:border-white/10">
				<div class="border-b border-r border-black/10 p-6 sm:p-8 dark:border-white/10">
					<dt class="axon-label text-black/45 dark:text-white/40">Last sweep</dt>
					<dd class="mt-3 text-2xl font-medium tracking-tight tabular-nums sm:text-3xl">
						{#if pulse?.last_sweep_at}{fmt(pulse.last_scanned)}<span class="mx-2 text-black/30 dark:text-white/30">→</span>{fmt(pulse.last_kept)}{:else}—{/if}
					</dd>
					<dd class="axon-label mt-2 text-black/40 dark:text-white/35">{pulse?.last_sweep_at ? `In → kept · ${lastAgo}` : ' '}</dd>
				</div>
				<div class="border-b border-black/10 p-6 sm:p-8 dark:border-white/10">
					<dt class="axon-label text-black/45 dark:text-white/40">Next sweep</dt>
					<dd class="mt-3 text-2xl font-medium tracking-tight tabular-nums sm:text-3xl">{nextIn ?? '—'}</dd>
					<dd class="axon-label mt-2 text-black/40 dark:text-white/35">{interval ? `Every ${interval} hours` : ' '}</dd>
				</div>
				<div class="border-r border-black/10 p-6 sm:p-8 dark:border-white/10">
					<dt class="axon-label text-black/45 dark:text-white/40">Kept so far</dt>
					<dd class="mt-3 text-2xl font-medium tracking-tight tabular-nums sm:text-3xl">{keptTotal ? fmt(keptTotal) : '—'}</dd>
					<dd class="axon-label mt-2 text-black/40 dark:text-white/35">{since ? `Since ${since}` : ' '}</dd>
				</div>
				<div class="p-6 sm:p-8">
					<dt class="axon-label text-black/45 dark:text-white/40">Sources</dt>
					<dd class="mt-3 text-2xl font-medium tracking-tight tabular-nums sm:text-3xl">{sourceCount}</dd>
					<dd class="axon-label mt-2 text-black/40 dark:text-white/35">Labs · papers · code · forums</dd>
				</div>
			</dl>
		</div>
	</section>

	<footer class="border-t border-black/10 dark:border-white/10">
		<div class="mx-auto grid w-full max-w-7xl gap-12 px-5 py-14 sm:grid-cols-2 sm:px-8 lg:grid-cols-[1.6fr_1fr_1fr_1fr]">
			<div class="sm:col-span-2 lg:col-span-1">
				<a href="/" class="flex items-center gap-2.5">
					<span class="flex h-7 w-7 items-center justify-center bg-black text-white dark:bg-white dark:text-black">
						<AxonMark class="h-4 w-4" />
					</span>
					<span class="text-[13px] font-semibold uppercase tracking-[0.24em]">Axon</span>
				</a>
				<p class="mt-5 max-w-xs text-[15px] leading-relaxed text-black/55 dark:text-white/50">
					The signal from the frontier of technology, without the noise. Swept every few hours.
				</p>
				<p class="axon-label mt-6 flex items-center gap-2 text-black/60 dark:text-white/55">
					<span class="axon-live text-black dark:text-white"></span>
					Last sweep {lastAgo}{nextIn ? ` · next ${nextIn}` : ''}
				</p>
			</div>

			{#each footerNav as group}
				<nav aria-label={group.title}>
					<p class="axon-label text-black/40 dark:text-white/35">{group.title}</p>
					<ul class="mt-5 space-y-3 text-[15px]">
						{#each group.links as link}
							<li>
								<a
									href={link.href}
									target={link.external ? '_blank' : undefined}
									rel={link.external ? 'noopener noreferrer' : undefined}
									onclick={link.href.startsWith('#') ? scrollTo(link.href.slice(1)) : undefined}
									class="text-black/60 transition-colors hover:text-black dark:text-white/55 dark:hover:text-white"
								>{link.label}{link.external ? ' ↗' : ''}</a>
							</li>
						{/each}
					</ul>
				</nav>
			{/each}
		</div>

		<div class="border-t border-black/10 dark:border-white/10">
			<div class="axon-label mx-auto flex w-full max-w-7xl flex-col gap-2 px-5 py-5 text-black/40 sm:flex-row sm:items-center sm:justify-between sm:px-8 dark:text-white/35">
				<span>© 2026 Bemnet Mussa</span>
				<span class="tabular-nums">{sourceCount} sources{interval ? ` · every ${interval}h` : ''} · {clock || '--:--:--'} UTC</span>
			</div>
		</div>
	</footer>
</div>
