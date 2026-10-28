<script lang="ts">
	import { onMount } from 'svelte';
	import { Bell, BellRing, BellOff } from 'lucide-svelte';
	import { getStatus, enable, disable, isPushSupported, sendTest, type PushStatus } from '$lib/push';

	type Props = {
		theme: 'dark' | 'light';
		/** 'sidebar' = compact desktop footer row; 'mobile' = larger overflow-sheet row. */
		variant?: 'sidebar' | 'mobile';
	};

	let { theme, variant = 'sidebar' }: Props = $props();
	let dark = $derived(theme === 'dark');

	let status = $state<PushStatus | null>(null);
	let busy = $state(false);
	let error = $state<string | null>(null);

	let supported = $derived(isPushSupported());
	let on = $derived(status?.permission === 'granted' && status?.subscribed === true);
	let blocked = $derived(status?.permission === 'denied');

	let label = $derived(
		blocked ? 'Notifications blocked' : on ? 'Notifications on' : 'Enable notifications'
	);

	onMount(async () => {
		if (!supported) return;
		try {
			status = await getStatus();
		} catch {
			/* leave null */
		}
	});

	async function toggle() {
		if (busy || blocked) {
			if (blocked) error = 'Turn notifications back on in your browser’s site settings.';
			return;
		}
		busy = true;
		error = null;
		try {
			const wasOn = on;
			status = wasOn ? await disable() : await enable();
			if (!wasOn && status.permission === 'denied') {
				error = 'Permission was denied.';
			} else if (!wasOn && status.subscribed) {
				void sendTest();
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Something went wrong.';
		} finally {
			busy = false;
		}
	}

	// Sizing/styling differs between the two placements but the logic is shared.
	let rowClass = $derived(
		variant === 'mobile'
			? `flex w-full items-center gap-3 px-3 py-3 text-left ${dark ? 'text-white/70 active:bg-white/[0.05]' : 'text-black/70 active:bg-black/[0.04]'}`
			: `flex w-full items-center gap-3 px-2 py-2 text-left transition-colors ${dark ? 'text-white/50 hover:bg-white/[0.05] hover:text-white' : 'text-black/50 hover:bg-black/[0.04] hover:text-black'}`
	);
	let iconClass = $derived(variant === 'mobile' ? 'h-[18px] w-[18px] shrink-0' : 'h-3.5 w-3.5 shrink-0');
	let textClass = $derived(variant === 'mobile' ? 'text-[14px] font-medium' : 'text-[13px] font-medium');
</script>

{#if supported}
	<button
		type="button"
		onclick={toggle}
		disabled={busy}
		class={`${rowClass} ${on ? (dark ? 'text-white' : 'text-zinc-900') : ''} disabled:opacity-60`}
		aria-pressed={on}
		title={blocked ? 'Blocked — enable in browser settings' : label}
	>
		{#if on}
			<BellRing class={iconClass} />
		{:else if blocked}
			<BellOff class={iconClass} />
		{:else}
			<Bell class={iconClass} />
		{/if}
		<span class={textClass}>{busy ? 'Working…' : label}</span>
	</button>
	{#if error}
		<p class={`px-3 pb-1 ${variant === 'mobile' ? 'text-[11px]' : 'text-[9px]'} ${dark ? 'text-white/60' : 'text-black/60'}`}>
			{error}
		</p>
	{/if}
{/if}
