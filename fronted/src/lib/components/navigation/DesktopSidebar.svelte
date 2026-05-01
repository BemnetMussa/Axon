<script lang="ts">
	import { MessageSquare, Moon, Sun, Zap, Sparkles, LogOut, TrendingUp } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';
	import type { NavItem } from '$lib/ui';
	import { onMount, onDestroy } from 'svelte';
	import { api, type Trend } from '$lib/api';
	import FeedbackModal from '../feedback/FeedbackModal.svelte';

	type Props = {
		navigation: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		showDigestView: boolean;
		sourceCounts: Record<string, number>;
		trends?: Trend[];
		theme: 'dark' | 'light';
		newSignalCount?: number;
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: (e: MouseEvent) => void;
		onTopicSearch: (keyword: string) => void;
	};

	let {
		navigation, activeCategory, showSavedOnly, showDigestView, sourceCounts, trends = [],
		theme, newSignalCount = 0, onNavigate, onShowSaved, onShowDigest, onToggleTheme, onTopicSearch
	}: Props = $props();

	let showFeedbackModal = $state(false);
	let lastSynced = $state<string | null>(null);
    let healthPollTimer: any;

	let dark = $derived(theme === 'dark');
	let topSources = $derived.by(() => {
		// Calculate top sources from whatever articles we have in memory
		// This keeps it stable even when scrolling down
		const counts: Record<string, number> = {};
		sourceCounts && Object.entries(sourceCounts).forEach(([src, count]) => {
			counts[src] = count;
		});
		return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 8);
	});
	let activeModeLabel = $derived(showSavedOnly ? 'Saved' : (activeCategory ?? 'Frontier'));

	async function updateHealth() {
        try {
            const health = await api.getHealth();
            lastSynced = health.last_scheduled_ingest?.relative || null;
        } catch {
            /* silent */
        }
    }

	onMount(() => {
        updateHealth();
        healthPollTimer = setInterval(updateHealth, 60000); // Check health every min
    });

    onDestroy(() => {
        if (healthPollTimer) clearInterval(healthPollTimer);
    });

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

	<!-- Signal count -->
	<div class="px-5 pb-1">
		<div class="flex items-center justify-between">
			<p class={`text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-700' : 'text-zinc-500'}`}>New signals</p>
			<span class={`text-[11px] font-semibold tabular-nums ${newSignalCount > 0 ? 'text-emerald-500' : (dark ? 'text-zinc-600' : 'text-zinc-400')}`}>{newSignalCount}</span>
		</div>
	</div>

	<!-- Trending topics -->
	{#if trends.length > 0}
		<div class="px-2.5 pt-2">
			<div class="flex items-center gap-1.5 px-3 pb-1.5">
				<TrendingUp class={`h-3 w-3 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`} />
				<p class={`text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-700' : 'text-zinc-500'}`}>Trending now</p>
			</div>
			<div class="flex flex-wrap gap-1.5 px-3">
				{#each trends.slice(0, 10) as trend}
					{@const isNew = trend.is_new || trend.velocity === 'New'}
					{@const isSurging = trend.velocity === 'Surging'}
					<button
						onclick={() => onTopicSearch(trend.keyword)}
						class={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold transition-all ${
							dark
								? 'border-white/[0.06] bg-white/[0.03] text-zinc-400 hover:border-white/15 hover:bg-white/[0.07] hover:text-zinc-200'
								: 'border-zinc-200 bg-zinc-50 text-zinc-600 hover:border-zinc-300 hover:bg-zinc-100 hover:text-zinc-800'
						}`}
					>
						{#if isNew}
							<span class="h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0"></span>
						{:else if isSurging}
							<span class="h-1.5 w-1.5 rounded-full bg-amber-400 shrink-0"></span>
						{/if}
						{trend.keyword}
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Top sources -->
	{#if topSources.length > 0}
		<div class="px-5 pt-3">
			<p class={`mb-1.5 text-[9px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-700' : 'text-zinc-500'}`}>Top sources</p>
			<div class="space-y-1">
				{#each topSources as [source, count]}
					<div class="flex items-center justify-between text-[10px]">
						<span class={`${dark ? 'text-zinc-400' : 'text-zinc-600'}`}>{source}</span>
						<span class={`tabular-nums ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{count}</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}

	<div class="mt-auto px-5 pb-3">
		<button
			onclick={onShowDigest}
			class={`mb-3 flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-[11px] font-bold transition-all ${
				showDigestView
					? dark ? 'bg-white text-black' : 'bg-zinc-900 text-white'
					: dark ? 'bg-white/[0.06] text-zinc-300 hover:bg-white/[0.10] hover:text-white' : 'bg-zinc-100 text-zinc-700 hover:bg-zinc-200 hover:text-black'
			}`}
		>
			<Sparkles class="h-4 w-4" />
			Weekly Digest
		</button>
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
			onclick={(e) => onToggleTheme(e)}
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

		<button
			onclick={() => showFeedbackModal = true}
			class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-zinc-600 hover:text-zinc-300' : 'text-zinc-400 hover:text-zinc-600'}`}
		>
			<MessageSquare class="h-4 w-4 shrink-0" />
			<span class="text-[10px] font-semibold">Feedback</span>
		</button>
        
        {#if lastSynced}
            <div class="px-3 py-1 flex items-center gap-2">
                <div class="h-1 w-1 rounded-full bg-emerald-500"></div>
                <span class={`text-[9px] font-medium ${dark ? 'text-zinc-700' : 'text-zinc-400'}`}>Synced {lastSynced}</span>
            </div>
        {/if}
	</div>
</nav>

<FeedbackModal bind:show={showFeedbackModal} {theme} />
