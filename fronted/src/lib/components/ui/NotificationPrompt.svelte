<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { Bell, Share, X } from 'lucide-svelte';
	import { enable, getStatus, isPushConfigured, isPushSupported, needsIosInstall, sendTest } from '$lib/push';

	type Props = {
		theme: 'dark' | 'light';
		/** Held back while another overlay (onboarding) owns the screen. */
		suppressed?: boolean;
	};

	let { theme, suppressed = false }: Props = $props();
	let dark = $derived(theme === 'dark');

	const DISMISS_KEY = 'axon-notify-prompt-dismissed';
	const SNOOZE_MS = 7 * 24 * 60 * 60 * 1000;

	let mode = $state<'enable' | 'install' | 'done' | null>(null);
	let busy = $state(false);
	let error = $state<string | null>(null);

	onMount(() => {
		const dismissed = Number(localStorage.getItem(DISMISS_KEY) || 0);
		if (Date.now() - dismissed < SNOOZE_MS) return;

		const timer = setTimeout(async () => {
			if (needsIosInstall() && isPushConfigured()) {
				mode = 'install';
				return;
			}
			if (!isPushSupported()) return;
			const status = await getStatus().catch(() => null);
			if (status && status.permission !== 'denied' && !status.subscribed) mode = 'enable';
		}, 3500);
		return () => clearTimeout(timer);
	});

	function dismiss() {
		localStorage.setItem(DISMISS_KEY, String(Date.now()));
		mode = null;
	}

	async function turnOn() {
		busy = true;
		error = null;
		try {
			const status = await enable();
			if (status.subscribed) {
				void sendTest();
				mode = 'done';
				setTimeout(() => (mode = null), 3500);
			} else if (status.permission === 'denied') {
				error = 'Blocked. You can turn it on later in your browser’s site settings.';
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Something went wrong.';
		} finally {
			busy = false;
		}
	}
</script>

{#if mode && !suppressed}
	<div
		transition:fly={{ y: 16, duration: 220 }}
		role="dialog"
		aria-label="Notifications"
		class={`fixed inset-x-3 z-[45] rounded-xl border p-4 shadow-2xl bottom-[calc(4.25rem+env(safe-area-inset-bottom,0px))] lg:inset-x-auto lg:right-6 lg:bottom-6 lg:w-[340px] ${dark ? 'border-white/10 bg-[#121212] text-white' : 'border-black/10 bg-white text-zinc-900'}`}
	>
		{#if mode === 'done'}
			<div class="flex items-center gap-3">
				<Bell class="h-4 w-4 shrink-0" />
				<p class="text-[13px] font-medium">On. A test notification is on its way.</p>
			</div>
		{:else}
			<div class="flex items-start gap-3">
				<div
					class={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${dark ? 'border-white/10 bg-white/[0.04]' : 'border-black/10 bg-black/[0.03]'}`}
				>
					{#if mode === 'install'}
						<Share class="h-4 w-4" />
					{:else}
						<Bell class="h-4 w-4" />
					{/if}
				</div>
				<div class="min-w-0 flex-1">
					<p class="text-[14px] font-semibold tracking-tight">
						{mode === 'install' ? 'Add Axon to your Home Screen' : 'Get a ping when a sweep lands'}
					</p>
					<p class={`mt-1 text-[12.5px] leading-snug ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>
						{#if mode === 'install'}
							iPhone only sends notifications from installed apps. Tap <span class="font-medium">Share</span>, then
							<span class="font-medium">Add to Home Screen</span>, and open Axon from there.
						{:else}
							One notification per sweep with the top stories that made the cut. Nothing else.
						{/if}
					</p>
					{#if error}
						<p class={`mt-2 text-[12px] ${dark ? 'text-zinc-300' : 'text-zinc-700'}`}>{error}</p>
					{/if}
					<div class="mt-3 flex items-center gap-2">
						{#if mode === 'enable'}
							<button
								type="button"
								onclick={turnOn}
								disabled={busy}
								class={`rounded-md px-3 py-1.5 text-[12.5px] font-semibold transition disabled:opacity-60 ${dark ? 'bg-white text-black hover:bg-zinc-200' : 'bg-zinc-900 text-white hover:bg-zinc-700'}`}
							>
								{busy ? 'Turning on…' : 'Turn on'}
							</button>
						{/if}
						<button
							type="button"
							onclick={dismiss}
							class={`rounded-md px-3 py-1.5 text-[12.5px] font-medium transition ${dark ? 'text-zinc-400 hover:text-white' : 'text-zinc-500 hover:text-zinc-900'}`}
						>
							{mode === 'install' ? 'Got it' : 'Not now'}
						</button>
					</div>
				</div>
				<button
					type="button"
					onclick={dismiss}
					aria-label="Dismiss"
					class={`-mt-1 -mr-1 rounded p-1 ${dark ? 'text-zinc-500 hover:text-white' : 'text-zinc-400 hover:text-zinc-900'}`}
				>
					<X class="h-4 w-4" />
				</button>
			</div>
		{/if}
	</div>
{/if}

