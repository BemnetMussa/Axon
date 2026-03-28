<script lang="ts">
	import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { Zap } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';

	let loading = $state(false);
	let theme = $state<'dark' | 'light'>('dark');

	$effect(() => {
		if (!browser) return;
		theme = document.documentElement.classList.contains('light') ? 'light' : 'dark';
	});

	async function signInGoogle() {
		loading = true;
		try {
			const redirectTo = page.url.searchParams.get('redirectTo') || '/';
			// disableRedirect: social sign-in otherwise returns 302; @better-fetch treats non-2xx as
			// error so the client's redirect plugin never runs. 200 + JSON + manual navigation fixes Vercel.
			const { data, error } = await authClient.signIn.social({
				provider: 'google',
				callbackURL: redirectTo,
				disableRedirect: true,
			});
			if (error) {
				console.error(error);
				return;
			}
			if (data?.url && browser) {
				window.location.href = data.url;
			}
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Sign in — AXON</title>
</svelte:head>

<div
	class={`flex min-h-screen flex-col items-center justify-center px-6 transition-colors ${theme === 'dark' ? 'bg-[#0b0b0b] text-zinc-200' : 'bg-white text-zinc-900'}`}
>
	<div class="mb-10 flex items-center gap-3">
		<div class={`flex h-10 w-10 items-center justify-center rounded-lg ${theme === 'dark' ? 'bg-white' : 'bg-black'}`}>
			<Zap class={`h-5 w-5 ${theme === 'dark' ? 'fill-black text-black' : 'fill-white text-white'}`} />
		</div>
		<span class={`text-lg font-black uppercase tracking-[3px] italic ${theme === 'dark' ? 'text-white' : 'text-black'}`}>Axon</span>
	</div>

	<div
		class={`w-full max-w-sm rounded-2xl border p-8 shadow-xl ${theme === 'dark' ? 'border-white/[0.08] bg-[#111]' : 'border-zinc-200 bg-zinc-50'}`}
	>
		<h1 class={`mb-1 text-center text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-zinc-900'}`}>Welcome back</h1>
		<p class={`mb-8 text-center text-[13px] ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-500'}`}>
			Sign in with Google to open your intelligence feed.
		</p>

		<button
			type="button"
			onclick={signInGoogle}
			disabled={loading}
			class={`flex w-full items-center justify-center gap-2 rounded-xl border py-3 text-[13px] font-semibold transition-all disabled:opacity-50 ${theme === 'dark' ? 'border-white/[0.1] bg-white text-black hover:bg-zinc-200' : 'border-zinc-200 bg-white text-zinc-900 hover:bg-zinc-100'}`}
		>
			{#if loading}
				<span>Connecting…</span>
			{:else}
				<svg class="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
					<path
						fill="currentColor"
						d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
					/>
					<path
						fill="currentColor"
						d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
					/>
					<path
						fill="currentColor"
						d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
					/>
					<path
						fill="currentColor"
						d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
					/>
				</svg>
				Continue with Google
			{/if}
		</button>
	</div>

	<p class={`mt-8 text-center text-[11px] ${theme === 'dark' ? 'text-zinc-600' : 'text-zinc-400'}`}>
		By continuing you agree to Axon&apos;s use of your account for sign-in only.
	</p>
</div>
