<script lang="ts">
	import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Zap, ArrowRight, AlertCircle } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';
	import { slide } from 'svelte/transition';

	let googleLoading = $state(false);
	let formLoading = $state(false);
	let errorMessage = $state('');
	let name = $state('');
	let email = $state('');
	let password = $state('');

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
				errorMessage = error.message || 'Unable to create account. Please verify your details.';
				return;
			}
			await goto(redirectTo);
		} catch {
			errorMessage = 'A network anomaly occurred. Please try again.';
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
				errorMessage = error.message || 'Google authentication failed.';
				return;
			}
			if (data?.url && browser) {
				window.location.href = data.url;
			}
		} catch {
			errorMessage = 'Unable to connect to Google right now.';
		} finally {
			googleLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Sign up — AXON</title>
</svelte:head>

<div class="min-h-screen w-full bg-white dark:bg-[#050505] text-zinc-900 dark:text-zinc-100 transition-colors duration-500 selection:bg-zinc-900 selection:text-white dark:selection:bg-white dark:selection:text-black">
	<div class="grid min-h-screen lg:grid-cols-2">
		
		<!-- The Vision (Left Panel) -->
		<aside class="relative hidden lg:block overflow-hidden bg-zinc-100 dark:bg-black">
			<img 
				src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=90&w=2000&auto=format&fit=crop" 
				alt="Axon global signal network" 
				class="absolute inset-0 h-full w-full object-cover opacity-90 dark:opacity-80 mix-blend-luminosity hover:mix-blend-normal hover:scale-105 transition-all duration-[3s] ease-out" 
			/>
			<div class="absolute inset-0 bg-gradient-to-t from-white via-white/20 to-transparent dark:from-[#050505] dark:via-[#050505]/40 dark:to-transparent"></div>
			
			<div class="absolute inset-0 flex flex-col justify-between p-12">
				<div class="flex items-center gap-2">
					<div class="flex h-8 w-8 items-center justify-center rounded bg-black dark:bg-white text-white dark:text-black shadow-lg">
						<Zap class="h-4 w-4 fill-current" />
					</div>
					<span class="text-lg font-black uppercase tracking-[0.2em] italic text-zinc-900 dark:text-white">Axon</span>
				</div>

				<div class="max-w-md">
					<p class="mb-4 text-xs font-bold uppercase tracking-[0.25em] text-zinc-500 dark:text-emerald-400/90">
						High-Signal, Low-Noise
					</p>
					<h2 class="text-3xl font-medium tracking-tight text-zinc-900 dark:text-white mb-4">
						The bleeding edge of tech, summarized in minutes.
					</h2>
					<p class="text-base text-zinc-600 dark:text-zinc-400 leading-relaxed">
						AXON pulls real-time signals from HackerNews, GitHub, ArXiv, and top AI feeds. <br>
						Get a personalized	 feed you can skim in minutes.
					</p>
				</div>
			</div>
		</aside>

		<!-- The Interaction (Right Panel) -->
		<section class="flex flex-col items-center justify-center px-6 py-12 sm:px-12 lg:px-20">
			<div class="w-full max-w-[380px]">
				
				<!-- Mobile Logo -->
				<div class="mb-12 flex lg:hidden items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-black dark:bg-white text-white dark:text-black shadow-md">
						<Zap class="h-5 w-5 fill-current" />
					</div>
					<span class="text-xl font-black uppercase tracking-[0.2em] italic text-zinc-900 dark:text-white">Axon</span>
				</div>

				<!-- Header -->
				<div class="mb-8">
					<h1 class="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">Create account</h1>
					<p class="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
						Sign up to catch up on today's tech and AI shifts.
					</p>
				</div>

				<!-- Form -->
				<form class="space-y-4" onsubmit={(e) => { e.preventDefault(); signUpEmail(); }}>
					<div class="space-y-3">
						
						<!-- Name Field -->
						<div class="relative">
							<input
								type="text"
								bind:value={name}
								placeholder="Full name"
								autocomplete="name"
								required
								class="peer w-full rounded-xl border border-zinc-200 dark:border-white/10 bg-zinc-50/50 dark:bg-white/5 px-4 py-3.5 text-sm text-zinc-900 dark:text-white placeholder-transparent focus:border-black dark:focus:border-white focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white transition-all duration-200"
							/>
							<label class="pointer-events-none absolute left-4 top-3.5 text-sm text-zinc-400 transition-all duration-200 peer-focus:-translate-y-[1.1rem] peer-focus:scale-[0.8] peer-focus:bg-white dark:peer-focus:bg-[#050505] peer-focus:px-1 peer-valid:-translate-y-[1.1rem] peer-valid:scale-[0.8] peer-valid:bg-white dark:peer-valid:bg-[#050505] peer-valid:px-1">
								Full name
							</label>
						</div>

						<!-- Email Field -->
						<div class="relative">
							<input
								type="email"
								bind:value={email}
								placeholder="name@example.com"
								autocomplete="email"
								required
								class="peer w-full rounded-xl border border-zinc-200 dark:border-white/10 bg-zinc-50/50 dark:bg-white/5 px-4 py-3.5 text-sm text-zinc-900 dark:text-white placeholder-transparent focus:border-black dark:focus:border-white focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white transition-all duration-200"
							/>
							<label class="pointer-events-none absolute left-4 top-3.5 text-sm text-zinc-400 transition-all duration-200 peer-focus:-translate-y-[1.1rem] peer-focus:scale-[0.8] peer-focus:bg-white dark:peer-focus:bg-[#050505] peer-focus:px-1 peer-valid:-translate-y-[1.1rem] peer-valid:scale-[0.8] peer-valid:bg-white dark:peer-valid:bg-[#050505] peer-valid:px-1">
								Email address
							</label>
						</div>

						<!-- Password Field -->
						<div class="relative">
							<input
								type="password"
								bind:value={password}
								placeholder="Password"
								autocomplete="new-password"
								required
								class="peer w-full rounded-xl border border-zinc-200 dark:border-white/10 bg-zinc-50/50 dark:bg-white/5 px-4 py-3.5 text-sm text-zinc-900 dark:text-white placeholder-transparent focus:border-black dark:focus:border-white focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white transition-all duration-200"
							/>
							<label class="pointer-events-none absolute left-4 top-3.5 text-sm text-zinc-400 transition-all duration-200 peer-focus:-translate-y-[1.1rem] peer-focus:scale-[0.8] peer-focus:bg-white dark:peer-focus:bg-[#050505] peer-focus:px-1 peer-valid:-translate-y-[1.1rem] peer-valid:scale-[0.8] peer-valid:bg-white dark:peer-valid:bg-[#050505] peer-valid:px-1">
								Create a password
							</label>
						</div>
					</div>

					<button
						type="submit"
						disabled={formLoading || googleLoading}
						class="group relative w-full overflow-hidden rounded-xl bg-black dark:bg-white px-4 py-3.5 text-sm font-medium text-white dark:text-black shadow-[0_0_40px_-10px_rgba(0,0,0,0.4)] dark:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-70 disabled:hover:scale-100"
					>
						<div class="flex items-center justify-center gap-2">
							{#if formLoading}
								<span class="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white dark:border-black/20 dark:border-t-black"></span>
								<span>Initializing...</span>
							{:else}
								<span>Initialize Account</span>
								<ArrowRight class="h-4 w-4 opacity-70 transition-transform group-hover:translate-x-1" />
							{/if}
						</div>
					</button>
				</form>

				<div class="relative flex items-center py-6">
					<div class="flex-grow border-t border-zinc-200 dark:border-white/10"></div>
					<span class="mx-4 flex-shrink-0 text-xs font-medium uppercase tracking-widest text-zinc-400">or</span>
					<div class="flex-grow border-t border-zinc-200 dark:border-white/10"></div>
				</div>

				<button
					type="button"
					onclick={signInGoogle}
					disabled={googleLoading || formLoading}
					class="flex w-full items-center justify-center gap-3 rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-transparent px-4 py-3.5 text-sm font-medium text-zinc-700 dark:text-zinc-200 shadow-sm transition-all hover:bg-zinc-50 dark:hover:bg-white/5 active:scale-[0.99] disabled:opacity-50 disabled:hover:bg-transparent"
				>
					{#if googleLoading}
						<span class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
						<span>Connecting via Google...</span>
					{:else}
						<svg class="h-5 w-5" viewBox="0 0 24 24">
							<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
							<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
							<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
							<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
						</svg>
						<span>Sign up with Google</span>
					{/if}
				</button>

				<!-- Error State -->
				{#if errorMessage}
					<div transition:slide={{ duration: 300, axis: 'y' }} class="mt-4">
						<div class="flex items-center gap-2 rounded-lg bg-red-50 dark:bg-red-500/10 p-3 text-sm text-red-600 dark:text-red-400 border border-red-100 dark:border-red-500/20">
							<AlertCircle class="h-4 w-4 shrink-0" />
							<p>{errorMessage}</p>
						</div>
					</div>
				{/if}

				<p class="mt-10 text-center text-sm text-zinc-500 dark:text-zinc-400">
					Already an operative?
					<a class="font-medium text-zinc-900 dark:text-white underline decoration-zinc-300 dark:decoration-zinc-600 underline-offset-4 hover:decoration-zinc-900 dark:hover:decoration-white transition-colors" href="/login">Sign in here</a>
				</p>
			</div>
		</section>
	</div>
</div>