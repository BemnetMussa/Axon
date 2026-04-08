<script lang="ts">
	import { MessageSquare, Moon, Sun, Zap, Sparkles, LogOut } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';
	import type { NavItem } from '$lib/ui';

	type Props = {
		navigation: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		sourceCounts: Record<string, number>;
		theme: 'dark' | 'light';
		newSignalCount?: number;
		hasActiveFilters?: boolean;
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: () => void;
	};

	let {
		navigation, activeCategory, showSavedOnly, sourceCounts, theme, newSignalCount = 0, hasActiveFilters = false,
		onNavigate, onShowSaved, onShowDigest, onToggleTheme
	}: Props = $props();

	let showFeedbackForm = $state(false);
	let feedbackText = $state('');
	let feedbackSent = $state(false);
	let dark = $derived(theme === 'dark');
	let topSources = $derived(Object.entries(sourceCounts).sort((a, b) => b[1] - a[1]).slice(0, 6));
	let activeModeLabel = $derived(showSavedOnly ? 'Saved' : (activeCategory ?? 'Frontier'));

	function openFeedback() {
		showFeedbackForm = !showFeedbackForm;
		feedbackSent = false;
		feedbackText = '';
	}

	function submitFeedback() {
		if (!feedbackText.trim()) return;
		const title = encodeURIComponent(`Feedback: ${feedbackText.slice(0, 60)}`);
		const body = encodeURIComponent(feedbackText);
		window.open(
			`https://github.com/bemnetmussa/axon/issues/new?title=${title}&body=${body}&labels=feedback`,
			'_blank',
			'noopener,noreferrer'
		);
		feedbackSent = true;
		feedbackText = '';
		setTimeout(() => { showFeedbackForm = false; feedbackSent = false; }, 2000);
	}

	function navItemClass(active: boolean) {
		if (active && dark) return 'bg-white/[0.06] text-white';
		if (active && !dark) return 'bg-zinc-100 text-black';
		if (dark) return 'text-zinc-500 hover:bg-white/[0.03] hover:text-zinc-300';
		return 'text-zinc-400 hover:bg-zinc-50 hover:text-zinc-600';
	}

</script>

<nav class={`hidden w-56 shrink-0 flex-col border-r lg:flex ${dark ? 'border-white/[0.05] bg-[#0b0b0b]/90' : 'border-zinc-200 bg-white/90'} backdrop-blur-xl`}>
	<div class="flex items-center gap-2.5 px-5 py-4">
		<div class={`flex h-7 w-7 items-center justify-center rounded-md ${dark ? 'bg-white' : 'bg-black'}`}>
			<Zap class={`h-3.5 w-3.5 ${dark ? 'fill-black text-black' : 'fill-white text-white'}`} />
		</div>
		<span class={`text-[13px] font-black uppercase tracking-[2px] italic ${dark ? 'text-white' : 'text-black'}`}>Axon</span>
	</div>

	<div class="px-5 pb-2">
		<p class={`text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-500'}`}>Active</p>
		<p class={`mt-1 text-[12px] font-semibold ${dark ? 'text-zinc-200' : 'text-zinc-800'}`}>{activeModeLabel}</p>
	</div>

	<div class="px-2.5 pb-1">
		<p class={`px-3 text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-700' : 'text-zinc-500'}`}>Navigate</p>
	</div>
	<div class="flex flex-col gap-1 px-2.5">
		{#each navigation as item}
			{@const isActive = activeCategory === item.id && !showSavedOnly}
			<button
				onclick={() => onNavigate(item.id)}
				class={`relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all ${navItemClass(isActive)}`}
			>
				<item.icon class="h-4 w-4 shrink-0" />
				<span class="text-[11px] font-semibold tracking-wide">{item.label}</span>
				{#if isActive}
					<div class={`absolute -left-2.5 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full ${dark ? 'bg-white' : 'bg-black'}`}></div>
				{/if}
			</button>
		{/each}

		<button
			onclick={onShowSaved}
			class={`relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all ${navItemClass(showSavedOnly)}`}
		>
			<Zap class="h-4 w-4 shrink-0" />
			<span class="text-[11px] font-semibold">Saved</span>
			{#if showSavedOnly}
				<div class={`absolute -left-2.5 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full ${dark ? 'bg-white' : 'bg-black'}`}></div>
			{/if}
		</button>
	</div>

	<div class="px-2.5 pt-3">
		<p class={`px-3 text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-700' : 'text-zinc-500'}`}>Context</p>
		<div class={`mx-3 mt-2 rounded-xl border px-3 py-2 ${dark ? 'border-white/[0.06] bg-white/[0.02]' : 'border-zinc-200 bg-zinc-50'}`}>
			<div class="flex items-center justify-between text-[10px]">
				<span class={`${dark ? 'text-zinc-500' : 'text-zinc-600'}`}>New Signals</span>
				<span class={`font-semibold ${newSignalCount > 0 ? 'text-emerald-500' : (dark ? 'text-zinc-300' : 'text-zinc-700')}`}>{newSignalCount}</span>
			</div>
			<div class={`mt-2 border-t pt-2 ${dark ? 'border-white/[0.06]' : 'border-zinc-200'}`}>
				<p class={`mb-1 text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-700' : 'text-zinc-500'}`}>Top Sources</p>
				<div class="space-y-1">
					{#each topSources as [source, count]}
						<div class="flex items-center justify-between text-[10px]">
							<span class={`${dark ? 'text-zinc-400' : 'text-zinc-600'}`}>{source}</span>
							<span class={`tabular-nums ${dark ? 'text-zinc-500' : 'text-zinc-500'}`}>{count}</span>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<div class="mt-auto px-5 pb-3">
		<button
			onclick={onShowDigest}
			class={`mb-4 flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-[11px] font-bold transition-all ${dark ? 'bg-white text-black hover:bg-zinc-200' : 'bg-black text-white hover:bg-zinc-800'}`}
		>
			<Sparkles class="h-4 w-4" />
			Weekly Synthesis
		</button>
		<p class={`mb-4 text-center text-[10px] ${dark ? 'text-zinc-600' : 'text-zinc-500'}`}>3-minute summary of the week</p>
	</div>

	<div class={`flex flex-col gap-0.5 border-t px-2.5 py-2 ${dark ? 'border-white/[0.04]' : 'border-zinc-200'}`}>
		<button
			type="button"
			onclick={() => authClient.signOut()}
			class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-zinc-600 hover:text-red-400' : 'text-zinc-400 hover:text-red-600'}`}
		>
			<LogOut class="h-4 w-4 shrink-0" />
			<span class="text-[10px] font-semibold">Sign out</span>
		</button>

		<button
			onclick={onToggleTheme}
			class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-zinc-600 hover:text-zinc-300' : 'text-zinc-400 hover:text-zinc-600'}`}
		>
			{#if dark}
				<Sun class="h-4 w-4 shrink-0" />
				<span class="text-[10px] font-semibold">Light Mode</span>
			{:else}
				<Moon class="h-4 w-4 shrink-0" />
				<span class="text-[10px] font-semibold">Dark Mode</span>
			{/if}
		</button>

		{#if showFeedbackForm}
			<div class={`rounded-md border p-2.5 ${dark ? 'border-white/[0.06] bg-white/[0.02]' : 'border-zinc-200 bg-zinc-50'}`}>
				{#if feedbackSent}
					<p class="text-center text-[11px] text-emerald-500">Opening GitHub — thanks!</p>
				{:else}
					<textarea
						bind:value={feedbackText}
						placeholder="What's on your mind?"
						rows={3}
						class={`mb-2 w-full resize-none rounded bg-transparent text-[11px] leading-relaxed outline-none ${dark ? 'text-zinc-300 placeholder:text-zinc-600' : 'text-zinc-700 placeholder:text-zinc-400'}`}
					></textarea>
					<div class="flex items-center justify-between">
						<button onclick={() => (showFeedbackForm = false)} class="text-[10px] font-semibold text-zinc-500">Cancel</button>
						<button
							onclick={submitFeedback}
							disabled={!feedbackText.trim()}
							class={`rounded-md px-2.5 py-1 text-[10px] font-bold transition-opacity disabled:opacity-30 ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}
						>Submit</button>
					</div>
				{/if}
			</div>
		{:else}
			<button
				onclick={openFeedback}
				class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-zinc-600 hover:text-zinc-300' : 'text-zinc-400 hover:text-zinc-600'}`}
			>
				<MessageSquare class="h-4 w-4 shrink-0" />
				<span class="text-[10px] font-semibold">Feedback</span>
			</button>
		{/if}
	</div>
</nav>
