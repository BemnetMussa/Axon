<script lang="ts">
	import { Home, Layers, Bookmark, ArrowRight, X } from 'lucide-svelte';
	import { analytics } from '$lib/analytics';

	type Props = {
		theme: 'dark' | 'light';
		onDone: () => void;
	};

	let { theme, onDone }: Props = $props();
	let dark = $derived(theme === 'dark');
	let step = $state(0);

	const steps = [
		{
			icon: Home,
			color: 'text-current',
			darkBg: 'bg-white/[0.06]',
			lightBg: 'bg-black/[0.04]',
			title: 'The feed',
			body: 'Every few hours Axon sweeps the labs, papers, GitHub and Hacker News, and keeps only what matters. Newest day first, best story first.',
		},
		{
			icon: Layers,
			color: 'text-current',
			darkBg: 'bg-white/[0.06]',
			lightBg: 'bg-black/[0.04]',
			title: 'Narrow it down',
			body: 'Frontier is what just landed. Trending is the strongest of the week. Research is the papers. Search is the icon beside them.',
		},
		{
			icon: Bookmark,
			color: 'text-current',
			darkBg: 'bg-white/[0.06]',
			lightBg: 'bg-black/[0.04]',
			title: 'Read, ask, keep',
			body: 'Open a story to read the short note and ask questions about it. The bookmark keeps it in Saved.',
		},
	];

	function next() {
		if (step < steps.length - 1) {
			step++;
		} else {
			analytics.onboardingCompleted();
			onDone();
		}
	}

	function skip() {
		analytics.onboardingCompleted();
		onDone();
	}
</script>

<!-- Backdrop -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="fixed inset-0 z-[200] flex items-center justify-center p-5" onclick={(e) => { if (e.target === e.currentTarget) skip(); }}>
	<div class={`pointer-events-none absolute inset-0 ${dark ? 'bg-black/75' : 'bg-white/70'} backdrop-blur-sm`}></div>

	<div class={`relative w-full max-w-sm border ${dark ? 'border-white/10 bg-[#0a0a0a]' : 'border-black/10 bg-[#fafafa]'}`}>
		<!-- Skip -->
		<button
			onclick={skip}
			class={`absolute right-4 top-4 flex h-7 w-7 items-center justify-center transition-colors ${dark ? 'text-zinc-600 hover:bg-white/[0.06] hover:text-zinc-300' : 'text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700'}`}
			aria-label="Skip onboarding"
		>
			<X class="h-3.5 w-3.5" />
		</button>

		<div class="px-7 pb-7 pt-8">
			<!-- Step counter dots -->
			<div class="mb-5 flex items-center gap-1.5">
				{#each steps as _, i}
					<div class={`h-[3px] transition-all ${i === step
						? (dark ? 'w-5 bg-white' : 'w-5 bg-zinc-900')
						: (dark ? 'w-1.5 bg-white/20' : 'w-1.5 bg-zinc-200')
					}`}></div>
				{/each}
			</div>

			{#each steps as s, i}
				{#if i === step}
					<!-- Step icon -->
					<div class={`mb-5 flex h-12 w-12 items-center justify-center ${dark ? s.darkBg : s.lightBg}`}>
						<s.icon class={`h-6 w-6 ${s.color}`} />
					</div>

					<h2 class={`mb-2 text-[17px] font-bold leading-snug tracking-tight ${dark ? 'text-white' : 'text-zinc-900'}`}>
						{s.title}
					</h2>
					<p class={`text-[13px] leading-relaxed ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>
						{s.body}
					</p>
				{/if}
			{/each}

			<button
				onclick={next}
				class={`axon-label mt-7 inline-flex h-11 w-full items-center justify-center gap-2 transition-opacity hover:opacity-90 ${
					dark ? 'bg-white text-black' : 'bg-black text-white'
				}`}
			>
				{step < steps.length - 1 ? 'Next' : 'Get started'}
				<ArrowRight class="h-4 w-4" />
			</button>
		</div>
	</div>
</div>
