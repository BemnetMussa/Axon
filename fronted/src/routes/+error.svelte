<script lang="ts">
	import { page } from '$app/stores';
	import { Zap, RefreshCw, Home } from 'lucide-svelte';

	async function hardRecover() {
		try {
			if ('serviceWorker' in navigator) {
				const regs = await navigator.serviceWorker.getRegistrations();
				await Promise.all(regs.map((r) => r.unregister()));
			}
			if ('caches' in window) {
				const keys = await caches.keys();
				await Promise.all(keys.map((k) => caches.delete(k)));
			}
		} catch {
			/* best-effort — still navigate */
		}
		// Bypass any leftover HTTP/SW cache of the error document.
		window.location.replace(`/app?recover=${Date.now()}`);
	}
</script>

<svelte:head>
	<title>Something went wrong — AXON</title>
</svelte:head>

<div class="flex min-h-screen flex-col items-center justify-center bg-[#0b0b0b] px-6 text-center font-sans antialiased">
	<!-- Subtle grid background -->
	<div class="pointer-events-none fixed inset-0 opacity-[0.035]"
		style="background-image: repeating-linear-gradient(0deg,#fff 0,#fff 1px,transparent 1px,transparent 44px),repeating-linear-gradient(90deg,#fff 0,#fff 1px,transparent 1px,transparent 44px);">
	</div>

	<div class="relative z-10 flex flex-col items-center">
		<!-- Logo mark -->
		<div class="mb-8 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/[0.06] ring-1 ring-white/[0.08]">
			<Zap class="h-5 w-5 text-white/60" />
		</div>

		<!-- Status code -->
		{#if $page.status !== 200}
			<p class="mb-2 text-[11px] font-bold uppercase tracking-[0.2em] text-zinc-600">
				Error {$page.status}
			</p>
		{/if}

		<h1 class="mb-3 text-2xl font-bold text-white">
			{$page.error?.message || 'Something went wrong'}
		</h1>
		<p class="mb-10 max-w-xs text-[13px] leading-relaxed text-zinc-500">
			Usually a stuck offline cache — Reload clears it. Your data is safe.
		</p>

		<div class="flex flex-wrap items-center justify-center gap-3">
			<button
				onclick={hardRecover}
				class="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-[13px] font-bold text-black transition-colors hover:bg-zinc-200"
			>
				<RefreshCw class="h-4 w-4" />
				Reload
			</button>
			<a
				href="/app"
				data-sveltekit-reload
				class="inline-flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.04] px-5 py-2.5 text-[13px] font-semibold text-zinc-300 transition-colors hover:bg-white/[0.07]"
			>
				<Home class="h-4 w-4" />
				Back to feed
			</a>
		</div>
	</div>
</div>
