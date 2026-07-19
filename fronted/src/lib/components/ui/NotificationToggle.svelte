<script lang="ts">
	import { onMount } from 'svelte';
	import { Bell, BellRing, BellOff } from 'lucide-svelte';
	import { getStatus, enable, disable, isPushSupported, type PushStatus } from '$lib/push';

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
			status = on ? await disable() : await enable();
			if (!on && status && status.permission === 'denied') {
				error = 'Permission was denied.';
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
			? `flex w-full items-center gap-3 rounded-xl px-3 py-3 transition-all ${dark ? 'text-zinc-400 hover:bg-white/[0.04]' : 'text-zinc-600 hover:bg-zinc-50'}`
			: `flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-zinc-600 hover:text-zinc-300' : 'text-zinc-400 hover:text-zinc-600'}`
	);
	let iconClass = $derived(variant === 'mobile' ? 'h-5 w-5 shrink-0' : 'h-4 w-4 shrink-0');
	let textClass = $derived(variant === 'mobile' ? 'text-[13px] font-semibold' : 'text-[10px] font-semibold');
</script>

{#if supported}
	<button
		type="button"
		onclick={toggle}
		disabled={busy}
		class={`${rowClass} ${on ? 'text-emerald-500 hover:text-emerald-400' : ''} disabled:opacity-60`}
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
		<p class={`px-3 pb-1 ${variant === 'mobile' ? 'text-[11px]' : 'text-[9px]'} ${dark ? 'text-amber-400/80' : 'text-amber-600'}`}>
			{error}
		</p>
	{/if}
{/if}
