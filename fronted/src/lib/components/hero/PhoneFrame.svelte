<script lang="ts">
	import { onMount } from 'svelte';
	import type { Pulse } from '$lib/api';
	import type { PreviewMessage, PreviewScreen } from '$lib/preview-content';

	// A phone bezel around the app's own screen. The screen is a /preview frame with
	// a real 390×788 viewport, so the app's breakpoints resolve exactly as on a phone,
	// then scaled into the bezel. It is a picture of the app, so it takes no input.
	type Props = {
		screen: PreviewScreen;
		theme: 'dark' | 'light';
		title: string;
		pulse?: Pulse | null;
		class?: string;
		frame?: HTMLIFrameElement;
	};
	let { screen, theme, title, pulse = null, class: className = '', frame = $bindable() }: Props = $props();
	let dark = $derived(theme === 'dark');

	const WIDTH = 390;
	const HEIGHT = 788;
	const SCALE = 274 / WIDTH;

	// The frame picks up the saved theme like any page; later changes are posted to it.
	let src = $derived(`/preview?screen=${screen}`);
	let loaded = $state(false);

	onMount(() => {
		const onMessage = (event: MessageEvent<PreviewMessage>) => {
			if (event.origin === location.origin && event.source === frame?.contentWindow && event.data?.type === 'axon-preview:ready') loaded = true;
		};
		window.addEventListener('message', onMessage);
		return () => window.removeEventListener('message', onMessage);
	});

	$effect(() => {
		const t = theme;
		if (loaded) frame?.contentWindow?.postMessage({ type: 'axon-preview:theme', theme: t }, location.origin);
	});

	$effect(() => {
		const p = $state.snapshot(pulse);
		if (loaded) frame?.contentWindow?.postMessage({ type: 'axon-preview:pulse', pulse: p }, location.origin);
	});
</script>

<div class={`relative w-[292px] shrink-0 rounded-[46px] border border-black/15 bg-[#050505] p-[9px] shadow-[0_40px_100px_-30px_rgba(0,0,0,0.55)] dark:border-white/15 dark:shadow-[0_40px_120px_-20px_rgba(0,0,0,0.9)] ${className}`}>
	<div
		class={`relative flex h-[590px] flex-col overflow-hidden rounded-[38px] ${dark ? 'bg-[#0a0a0a] text-[#ededed]' : 'bg-[#fafafa] text-[#0a0a0a]'}`}
	>
		<div aria-hidden="true" class="relative flex h-9 shrink-0 items-center justify-between px-6 pt-1 text-[11px] font-semibold tabular-nums">
			<span>9:41</span>
			<span class="absolute left-1/2 top-2 h-[22px] w-[84px] -translate-x-1/2 rounded-full bg-black"></span>
			<span class="flex items-center gap-1">
				<span class="flex items-end gap-[2px]">
					{#each [4, 6, 8, 10] as h}<span class="w-[3px] rounded-[1px] bg-current" style={`height:${h}px`}></span>{/each}
				</span>
				<span class="ml-1 h-[10px] w-[20px] rounded-[3px] border border-current p-[1.5px]"><span class="block h-full w-3/4 rounded-[1px] bg-current"></span></span>
			</span>
		</div>

		<div class="relative min-h-0 flex-1 overflow-hidden">
			<iframe
				bind:this={frame}
				{src}
				{title}
				loading="lazy"
				tabindex="-1"
				class={`pointer-events-none absolute left-0 top-0 origin-top-left border-0 transition-opacity duration-500 ${loaded ? 'opacity-100' : 'opacity-0'}`}
				style={`width:${WIDTH}px;height:${HEIGHT}px;transform:scale(${SCALE});color-scheme:${dark ? 'dark' : 'light'}`}
			></iframe>
		</div>
	</div>
</div>
