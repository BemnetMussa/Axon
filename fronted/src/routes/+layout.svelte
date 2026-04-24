<script lang="ts">
import { onMount } from 'svelte';
import "../app.css";
import './layout.css';
import favicon from '$lib/assets/favicon.svg';

let { children } = $props();

let runtimeError = $state<string | null>(null);

onMount(() => {
	const handleError = (e: ErrorEvent) => {
		// Ignore benign browser extension errors and ResizeObserver noise
		const msg = e.message || '';
		if (
			msg.includes('ResizeObserver') ||
			msg.includes('Extension') ||
			msg.includes('chrome-extension')
		) return;
		runtimeError = 'A JavaScript error occurred. The page may not work correctly.';
	};
	const handleRejection = (e: PromiseRejectionEvent) => {
		const msg = String(e.reason?.message || e.reason || '');
		if (msg.includes('Load failed') || msg.includes('NetworkError')) {
			// Network errors are expected offline — don't surface
			return;
		}
		// Only surface truly unexpected promise rejections
		console.error('[Axon] Unhandled rejection:', e.reason);
	};
	window.addEventListener('error', handleError);
	window.addEventListener('unhandledrejection', handleRejection);
	return () => {
		window.removeEventListener('error', handleError);
		window.removeEventListener('unhandledrejection', handleRejection);
	};
});
</script>

<svelte:head><link rel="icon" href="{favicon}" /></svelte:head>

{#if runtimeError}
	<div class="fixed top-4 left-1/2 z-[9999] -translate-x-1/2 max-w-sm w-full px-4">
		<div class="flex items-start gap-3 rounded-xl border border-red-500/30 bg-[#1a0a0a] px-4 py-3 shadow-2xl">
			<span class="mt-0.5 shrink-0 text-red-400">⚠</span>
			<div class="min-w-0 flex-1">
				<p class="text-[12px] font-semibold text-red-300">{runtimeError}</p>
				<button
					onclick={() => window.location.reload()}
					class="mt-1 text-[11px] font-bold text-red-400 underline underline-offset-2 hover:text-red-300"
				>Reload page</button>
			</div>
			<button onclick={() => (runtimeError = null)} class="shrink-0 text-red-600 hover:text-red-400" aria-label="Dismiss">✕</button>
		</div>
	</div>
{/if}

{@render children()}
