<script lang="ts">
	import ShaderLines from '$lib/components/hero/ShaderLines.svelte';
</script>

<svelte:head>
	<title>AXON — Intelligence for Builders</title>
</svelte:head>

<div class="relative min-h-screen overflow-hidden bg-[#070b14] text-zinc-100">
	<div class="absolute inset-0 opacity-70">
		<ShaderLines />
	</div>
	<div class="absolute inset-0 bg-gradient-to-b from-black/45 via-black/60 to-[#070b14]"></div>

	<header class="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 sm:px-10">
		<div class="text-xl font-black uppercase tracking-[0.18em] italic">Axon</div>
		<a
			href="/login"
			class="rounded-full border border-white/20 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-zinc-100 transition hover:bg-white/10"
		>
			Sign in
		</a>
	</header>

	<section class="relative z-10 mx-auto flex min-h-[72vh] w-full max-w-7xl items-center px-6 pb-20 pt-10 sm:px-10">
		<div class="max-w-3xl">
			<p class="mb-4 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-300/90">Signal -> Insight -> Action</p>
			<h1 class="text-4xl font-black leading-tight tracking-tight text-white sm:text-6xl">
				Make sense of the week in AI and tech before everyone else.
			</h1>
			<p class="mt-6 max-w-2xl text-base leading-relaxed text-zinc-300 sm:text-lg">
				Axon tracks frontier signals, distills what matters, and gives builders a tactical weekly synthesis.
				From fast-moving model releases to ecosystem shifts, you get a clear picture and what to do next.
			</p>

			<div class="mt-10 flex flex-col gap-3 sm:flex-row">
				<a
					href="/login"
					class="inline-flex items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-bold text-black transition hover:bg-zinc-200"
				>
					Get Started
				</a>
				<a
					href="#learn-more"
					class="inline-flex items-center justify-center rounded-xl border border-white/25 px-6 py-3 text-sm font-semibold text-zinc-100 transition hover:bg-white/10"
				>
					Learn More
				</a>
			</div>
		</div>
	</section>

	<section id="learn-more" class="relative z-10 mx-auto grid w-full max-w-7xl gap-4 px-6 pb-16 sm:grid-cols-3 sm:px-10">
		<div class="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
			<h3 class="text-sm font-bold text-white">Curated Signals</h3>
			<p class="mt-2 text-sm text-zinc-300">Monitor high-signal articles from trusted technical sources.</p>
		</div>
		<div class="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
			<h3 class="text-sm font-bold text-white">Weekly Synthesis</h3>
			<p class="mt-2 text-sm text-zinc-300">Get a clear summary of what changed and why it matters now.</p>
		</div>
		<div class="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
			<h3 class="text-sm font-bold text-white">Builder-Focused</h3>
			<p class="mt-2 text-sm text-zinc-300">Actionable intelligence for founders, engineers, and product teams.</p>
		</div>
	</section>
</div>
