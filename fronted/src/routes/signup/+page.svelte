<script lang="ts">
	import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Zap } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';

	let googleLoading = $state(false);
	let formLoading = $state(false);
	let errorMessage = $state('');
	let name = $state('');
	let email = $state('');
	let password = $state('');
	let theme = $state<'dark' | 'light'>('dark');

	$effect(() => {
		if (!browser) return;
		theme = document.documentElement.classList.contains('light') ? 'light' : 'dark';
	});

	async function signUpEmail() {
		errorMessage = '';
		if (!name.trim() || !email.trim() || !password) {
			errorMessage = 'Name, email, and password are required.';
			return;
		}
		formLoading = true;
		try {
			const redirectTo = page.url.searchParams.get('redirectTo') || '/app';
			const { error } = await authClient.signUp.email({
				name: name.trim(),
				email: email.trim(),
				password,
				callbackURL: redirectTo,
			});
			if (error) {
				errorMessage = error.message || 'Unable to create account.';
				return;
			}
			await goto(redirectTo);
		} catch {
			errorMessage = 'Unable to create account right now. Please try again.';
		} finally {
			formLoading = false;
		}
	}

	async function signInGoogle() {
		errorMessage = '';
		googleLoading = true;
		try {
			const redirectTo = page.url.searchParams.get('redirectTo') || '/app';
			const { data, error } = await authClient.signIn.social({
				provider: 'google',
				callbackURL: redirectTo,
				disableRedirect: true,
			});
			if (error) {
				errorMessage = error.message || 'Google sign-in failed.';
				return;
			}
			if (data?.url && browser) {
				window.location.href = data.url;
			}
		} catch {
			errorMessage = 'Google sign-in failed. Please try again.';
		} finally {
			googleLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Sign up — AXON</title>
</svelte:head>

<div class={`min-h-screen transition-colors ${theme === 'dark' ? 'bg-[#0b0b0b] text-zinc-200' : 'bg-white text-zinc-900'}`}>
	<div class="mx-auto grid min-h-screen max-w-7xl lg:grid-cols-2">
		<aside class="relative hidden overflow-hidden rounded-r-3xl lg:block">
			<img src="/images/auth-signup-hero.svg" alt="Axon growth and intelligence mission visualization" class="h-full w-full object-cover" />
			<div class="absolute inset-0 bg-black/35"></div>
			<div class="absolute bottom-10 left-10 right-10">
				<p class="text-sm uppercase tracking-[0.2em] text-emerald-200/90">Join Axon</p>
				<h2 class="mt-3 text-3xl font-bold text-white">Build your intelligence edge from day one.</h2>
				<p class="mt-3 max-w-md text-sm text-zinc-200">Track frontier shifts, extract insights, and make faster strategic decisions.</p>
			</div>
		</aside>

		<section class="flex items-center justify-center px-6 py-10 sm:px-10">
			<div class="w-full max-w-sm">
				<div class="mb-8 flex items-center gap-3">
					<div class={`flex h-10 w-10 items-center justify-center rounded-lg ${theme === 'dark' ? 'bg-white' : 'bg-black'}`}>
						<Zap class={`h-5 w-5 ${theme === 'dark' ? 'fill-black text-black' : 'fill-white text-white'}`} />
					</div>
					<span class={`text-lg font-black uppercase tracking-[3px] italic ${theme === 'dark' ? 'text-white' : 'text-black'}`}>Axon</span>
				</div>

				<div class={`w-full rounded-2xl border p-8 shadow-xl ${theme === 'dark' ? 'border-white/[0.08] bg-[#111]' : 'border-zinc-200 bg-zinc-50'}`}>
		<h1 class={`mb-1 text-center text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-zinc-900'}`}>Create account</h1>
		<p class={`mb-8 text-center text-[13px] ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-500'}`}>
			Start your personalized intelligence feed.
		</p>

		<form class="space-y-3" onsubmit={(e) => { e.preventDefault(); signUpEmail(); }}>
			<input
				type="text"
				bind:value={name}
				placeholder="Full name"
				autocomplete="name"
				class={`w-full rounded-xl border px-3 py-2.5 text-sm outline-none transition ${theme === 'dark' ? 'border-white/[0.12] bg-black/30 text-zinc-100 placeholder:text-zinc-500 focus:border-white/40' : 'border-zinc-300 bg-white text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-500'}`}
			/>
			<input
				type="email"
				bind:value={email}
				placeholder="Email"
				autocomplete="email"
				class={`w-full rounded-xl border px-3 py-2.5 text-sm outline-none transition ${theme === 'dark' ? 'border-white/[0.12] bg-black/30 text-zinc-100 placeholder:text-zinc-500 focus:border-white/40' : 'border-zinc-300 bg-white text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-500'}`}
			/>
			<input
				type="password"
				bind:value={password}
				placeholder="Password"
				autocomplete="new-password"
				class={`w-full rounded-xl border px-3 py-2.5 text-sm outline-none transition ${theme === 'dark' ? 'border-white/[0.12] bg-black/30 text-zinc-100 placeholder:text-zinc-500 focus:border-white/40' : 'border-zinc-300 bg-white text-zinc-900 placeholder:text-zinc-400 focus:border-zinc-500'}`}
			/>
			<button
				type="submit"
				disabled={formLoading || googleLoading}
				class={`w-full rounded-xl py-3 text-[13px] font-semibold transition disabled:opacity-50 ${theme === 'dark' ? 'bg-white text-black hover:bg-zinc-200' : 'bg-black text-white hover:bg-zinc-800'}`}
			>
				{formLoading ? 'Creating account…' : 'Create account'}
			</button>
		</form>

		<div class="my-5 flex items-center gap-3">
			<div class={`h-px flex-1 ${theme === 'dark' ? 'bg-white/[0.08]' : 'bg-zinc-200'}`}></div>
			<span class={`text-[11px] uppercase tracking-wider ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>or</span>
			<div class={`h-px flex-1 ${theme === 'dark' ? 'bg-white/[0.08]' : 'bg-zinc-200'}`}></div>
		</div>

		<button
			type="button"
			onclick={signInGoogle}
			disabled={googleLoading || formLoading}
			class={`flex w-full items-center justify-center gap-2 rounded-xl border py-3 text-[13px] font-semibold transition-all disabled:opacity-50 ${theme === 'dark' ? 'border-white/[0.1] bg-transparent text-zinc-100 hover:bg-white/[0.06]' : 'border-zinc-200 bg-white text-zinc-900 hover:bg-zinc-100'}`}
		>
			{#if googleLoading}
				<span>Connecting…</span>
			{:else}
				<span class={`grid h-7 w-7 place-items-center rounded-full border text-xs font-bold ${theme === 'dark' ? 'border-white/[0.18]' : 'border-zinc-300'}`}>G</span>
				Continue with Google
			{/if}
		</button>

		{#if errorMessage}
			<p class="mt-4 text-center text-xs text-red-400">{errorMessage}</p>
		{/if}

		<p class={`mt-6 text-center text-xs ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-500'}`}>
			Already have an account?
			<a class={`font-semibold underline ${theme === 'dark' ? 'text-zinc-200' : 'text-zinc-700'}`} href="/login">Sign in</a>
		</p>
				</div>
			</div>
		</section>
	</div>
</div>
