<script lang="ts">
	import { onMount } from 'svelte';
	import type { Pulse } from '$lib/api';
	import { sweepIn, sweepAgo } from '$lib/pulse';
	import { KEY_SOURCE, type PreviewMessage } from '$lib/preview-content';
	import IntakeStage from './IntakeStage.svelte';
	import PhoneFrame from './PhoneFrame.svelte';

	type Props = { pulse: Pulse | null };
	let { pulse }: Props = $props();

	// The phone is the app's real feed screen (/preview). Each story the stage keeps
	// is sent into it; the frame reports which sources are not already on screen.
	let desktopFrame = $state<HTMLIFrameElement | undefined>();
	let mobileFrame = $state<HTMLIFrameElement | undefined>();
	let keepable = $state<string[]>(Object.keys(KEY_SOURCE));

	let scannedTotal = $derived(pulse?.scanned_total || null);
	let keptTotal = $derived(pulse?.kept_total || null);
	let keptShare = $derived(scannedTotal && keptTotal ? Math.round((keptTotal / scannedTotal) * 100) : null);
	let since = $derived(
		pulse?.running_since ? new Date(pulse.running_since).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : null
	);
	const fmt = (n: number | null | undefined) => (n == null ? '—' : n.toLocaleString('en-US'));
	let theme = $state<'dark' | 'light'>('dark');
	let lastAgo = $derived(sweepAgo(pulse?.last_sweep_at, Date.now()));
	let nextIn = $derived(pulse?.next_sweep_at ? sweepIn(pulse.next_sweep_at) : null);

	onMount(() => {
		const read = () => (theme = document.documentElement.classList.contains('light') ? 'light' : 'dark');
		read();
		const mo = new MutationObserver(read);
		mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

		const onMessage = (event: MessageEvent<PreviewMessage>) => {
			if (event.origin !== location.origin) return;
			if (event.data?.type === 'axon-preview:keepable') keepable = event.data.keys;
		};
		window.addEventListener('message', onMessage);
		return () => {
			mo.disconnect();
			window.removeEventListener('message', onMessage);
		};
	});

	function handleKeep(key: string) {
		const message: PreviewMessage = { type: 'axon-preview:keep', key };
		for (const frame of [desktopFrame, mobileFrame]) frame?.contentWindow?.postMessage(message, location.origin);
	}
</script>

<div class="[--stage-bg:#fafafa] dark:[--stage-bg:#0a0a0a]">
	<!-- Desktop: sources → core → phone, left to right -->
	<div class="hidden items-center justify-center gap-10 py-4 lg:flex xl:gap-16">
		<div class="w-full max-w-[660px] xl:max-w-[720px]">
			<p class="axon-label mb-6 text-black/40 dark:text-white/35">Input · 17 sources → Axon filter</p>
			<IntakeStage layout="wide" onKeep={handleKeep} {keepable} />
		</div>
		<div class="flex flex-col items-center">
			<p class="axon-label mb-4 text-black/40 dark:text-white/35">Output · your feed</p>
			<PhoneFrame screen="feed" {theme} title="Axon feed on a phone" {pulse} bind:frame={desktopFrame} />
		</div>
	</div>

	<!-- Phone: sources → core → phone, top to bottom -->
	<div class="flex flex-col items-center pb-6 lg:hidden">
		<p class="axon-label mb-4 self-start text-black/40 dark:text-white/35">Input · 17 sources</p>
		<div class="w-full max-w-[380px]">
			<IntakeStage layout="tall" onKeep={handleKeep} {keepable} />
		</div>
		<p class="axon-label mb-4 mt-2 text-black/40 dark:text-white/35">Output · your feed</p>
		<PhoneFrame screen="feed" {theme} title="Axon feed on a phone" {pulse} bind:frame={mobileFrame} />
	</div>

	<dl class="relative mt-10 grid grid-cols-2 border-t border-black/10 md:grid-cols-4 dark:border-white/10">
		<div class="border-b border-r border-black/10 py-5 pr-4 md:border-b-0 dark:border-white/10">
			<dt class="axon-label text-black/45 dark:text-white/40">Scanned{since ? ` since ${since}` : ''}</dt>
			<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">{fmt(scannedTotal)}</dd>
			<dd class="axon-label mt-1.5 text-black/40 dark:text-white/35">{pulse?.sweeps_24h ? `${fmt(pulse.scanned_24h)} in the last 24h` : ' '}</dd>
		</div>
		<div class="border-b border-black/10 py-5 pl-4 md:border-b-0 md:border-r md:pr-4 dark:border-white/10">
			<dt class="axon-label text-black/45 dark:text-white/40">Kept</dt>
			<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">{fmt(keptTotal)}</dd>
			<dd class="axon-label mt-1.5 text-black/40 dark:text-white/35">{keptShare !== null ? `About ${keptShare}% of what was scanned` : ' '}</dd>
		</div>
		<div class="border-r border-black/10 py-5 pr-4 md:pl-4 dark:border-white/10">
			<dt class="axon-label text-black/45 dark:text-white/40">Last sweep</dt>
			<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">
				{#if pulse?.last_sweep_at}{fmt(pulse.last_scanned)} <span class="text-black/35 dark:text-white/30">→</span> {fmt(pulse.last_kept)}{:else}—{/if}
			</dd>
			<dd class="axon-label mt-1.5 text-black/40 dark:text-white/35">{pulse?.last_sweep_at ? `In → kept · ${lastAgo}` : ' '}</dd>
		</div>
		<div class="py-5 pl-4">
			<dt class="axon-label text-black/45 dark:text-white/40">Next sweep</dt>
			<dd class="mt-2 text-2xl font-medium tracking-tight tabular-nums">{nextIn ?? '—'}</dd>
			<dd class="axon-label mt-1.5 text-black/40 dark:text-white/35">{pulse ? `Every ${pulse.interval_hours} hours` : ' '}</dd>
		</div>
	</dl>
	<p class="axon-label border-t border-black/10 pt-3 text-black/35 dark:border-white/10 dark:text-white/30">
		The animation and stories are illustrative. Every number here is live from the database.
	</p>
</div>
