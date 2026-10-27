<script lang="ts">
	import { MessageSquare, Moon, Sun, Zap, Sparkles, LogOut } from 'lucide-svelte';
	import { authClient } from '$lib/auth-client';
	import type { NavItem } from '$lib/ui';
	import type { Trend } from '$lib/api';
	import { pulseStore } from '$lib/pulse-store.svelte';
	import { sweepAgo, sweepIn, keptPercent, pulseWindow, formatCount } from '$lib/pulse';
	import FeedbackModal from '../feedback/FeedbackModal.svelte';
	import NotificationToggle from '../ui/NotificationToggle.svelte';
	import SignalTrace from '../ui/SignalTrace.svelte';

	type Props = {
		navigation: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		showDigestView: boolean;
		trends?: Trend[];
		theme: 'dark' | 'light';
		newSignalCount?: number;
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: () => void;
		onTopicSearch: (keyword: string) => void;
	};

	let {
		navigation, activeCategory, showSavedOnly, showDigestView, trends = [],
		theme, newSignalCount = 0, onNavigate, onShowSaved, onShowDigest, onToggleTheme, onTopicSearch
	}: Props = $props();

	let showFeedbackModal = $state(false);
	let dark = $derived(theme === 'dark');

	let pulse = $derived(pulseStore.value);
	let win = $derived(pulseWindow(pulse));
	let pct = $derived(win ? keptPercent(win.scanned, win.kept) : null);
	let lastAgo = $derived(sweepAgo(pulse?.last_sweep_at, pulseStore.now));
	let nextIn = $derived(pulse?.next_sweep_at ? sweepIn(pulse.next_sweep_at, pulseStore.now) : null);

	const pad = (n: number) => String(n).padStart(2, '0');

	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');
	let rule = $derived(dark ? 'border-white/10' : 'border-black/10');

	function rowClass(active: boolean) {
		if (active) return dark ? 'bg-white text-black' : 'bg-black text-white';
		return dark ? 'text-white/60 hover:bg-white/[0.05] hover:text-white' : 'text-black/60 hover:bg-black/[0.04] hover:text-black';
	}

	function velocityMark(t: Trend): string {
		if (t.is_new || t.velocity === 'New') return 'New';
		if (t.velocity === 'Surging') return '↑↑';
		if (t.velocity === 'Rising') return '↑';
		return '·';
	}
</script>

<nav class={`hidden w-60 shrink-0 flex-col border-r lg:flex ${rule} ${dark ? 'bg-[#0a0a0a] text-[#ededed]' : 'bg-[#fafafa] text-[#0a0a0a]'}`}>
	<!-- Brand -->
	<div class={`flex h-14 shrink-0 items-center justify-between border-b px-5 ${rule}`}>
		<div class="flex items-center gap-2.5">
			<span class={`flex h-6 w-6 items-center justify-center ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}>
				<Zap class="h-3 w-3 fill-current" />
			</span>
			<span class="text-[12px] font-semibold uppercase tracking-[0.24em]">Axon</span>
		</div>
		<span class={`axon-label flex items-center gap-2 ${muted}`}>
			<span class={`axon-live ${dark ? 'text-white' : 'text-black'}`}></span>Live
		</span>
	</div>

	<!-- Sweep readout -->
	<section class={`shrink-0 border-b px-5 py-4 ${rule}`}>
		<div class={`axon-label flex items-center justify-between ${muted}`}>
			<span>Filter</span>
			<span>{pulse?.last_sweep_at ? lastAgo : 'standby'}</span>
		</div>

		<SignalTrace compact class={`mt-3 h-9 ${dark ? '[--trace-bg:#0a0a0a]' : '[--trace-bg:#fafafa]'}`} />

		{#if win}
			<div class="mt-3 flex items-baseline justify-between">
				<p class="text-[22px] font-medium leading-none tracking-tight tabular-nums">
					{formatCount(win.kept)}<span class={`ml-1 text-[13px] ${muted}`}>/ {formatCount(win.scanned)}</span>
				</p>
				{#if pct !== null}
					<span class={`axon-label ${muted}`}>{pct}% kept</span>
				{/if}
			</div>
			<div class={`mt-2.5 h-[3px] ${dark ? 'bg-white/10' : 'bg-black/10'}`}>
				<div class={`h-full ${dark ? 'bg-white' : 'bg-black'}`} style={`width: ${Math.max(pct ?? 0, 2)}%`}></div>
			</div>
			<div class={`axon-label mt-3 space-y-1.5 ${muted}`}>
				<p class="flex justify-between"><span>Kept / scanned</span><span>{win.label}</span></p>
				{#if nextIn}
					<p class="flex justify-between"><span>Next sweep</span><span class="tabular-nums">{nextIn}</span></p>
				{/if}
			</div>
		{:else}
			<p class={`mt-3 text-[12px] leading-relaxed ${muted}`}>Waiting for the first sweep to report.</p>
		{/if}
	</section>

	<!-- Channels -->
	<section class={`shrink-0 border-b px-3 py-4 ${rule}`}>
		<p class={`axon-label px-2 pb-2 ${muted}`}>Channels</p>
		<div class="flex flex-col">
			{#each navigation as item, i}
				{@const active = activeCategory === item.id && !showSavedOnly && !showDigestView}
				<button onclick={() => onNavigate(item.id)} class={`flex items-center gap-3 px-2 py-2 text-left transition-colors ${rowClass(active)}`}>
					<span class="axon-label w-5 opacity-50">{pad(i + 1)}</span>
					<item.icon class="h-3.5 w-3.5 shrink-0" />
					<span class="text-[13px] font-medium">{item.label}</span>
					{#if item.id === null && newSignalCount > 0}
						<span class="axon-label ml-auto tabular-nums">+{newSignalCount}</span>
					{/if}
				</button>
			{/each}
			<button onclick={onShowSaved} class={`flex items-center gap-3 px-2 py-2 text-left transition-colors ${rowClass(showSavedOnly)}`}>
				<span class="axon-label w-5 opacity-50">{pad(navigation.length + 1)}</span>
				<Zap class="h-3.5 w-3.5 shrink-0" />
				<span class="text-[13px] font-medium">Saved</span>
			</button>
			<button onclick={onShowDigest} class={`flex items-center gap-3 px-2 py-2 text-left transition-colors ${rowClass(showDigestView)}`}>
				<span class="axon-label w-5 opacity-50">{pad(navigation.length + 2)}</span>
				<Sparkles class="h-3.5 w-3.5 shrink-0" />
				<span class="text-[13px] font-medium">Weekly digest</span>
			</button>
		</div>
	</section>

	<!-- Rising keywords -->
	<section class="no-scrollbar min-h-0 flex-1 overflow-y-auto px-5 py-4">
		<div class={`axon-label flex justify-between pb-3 ${muted}`}>
			<span>Rising</span>
			<span>today</span>
		</div>
		{#if trends.length > 0}
			<ol class="space-y-0.5">
				{#each trends.slice(0, 8) as trend, i}
					<li>
						<button
							onclick={() => onTopicSearch(trend.keyword)}
							class={`grid w-full grid-cols-[22px_1fr_auto] items-baseline gap-2 py-1 text-left transition-colors ${dark ? 'text-white/70 hover:text-white' : 'text-black/70 hover:text-black'}`}
						>
							<span class={`axon-label ${muted}`}>{pad(i + 1)}</span>
							<span class="truncate text-[12px]">{trend.keyword}</span>
							<span class={`axon-label ${velocityMark(trend) === '·' ? muted : ''}`}>{velocityMark(trend)}</span>
						</button>
					</li>
				{/each}
			</ol>
		{:else}
			<p class={`text-[12px] ${muted}`}>Nothing rising yet.</p>
		{/if}
	</section>

	<!-- Utilities -->
	<div class={`shrink-0 border-t px-2.5 py-2 ${rule}`}>
		<button
			onclick={() => onToggleTheme()}
			class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-white/45 hover:text-white' : 'text-black/45 hover:text-black'}`}
		>
			{#if dark}
				<Sun class="h-4 w-4 shrink-0" />
				<span class="text-[10px] font-semibold">Light mode</span>
			{:else}
				<Moon class="h-4 w-4 shrink-0" />
				<span class="text-[10px] font-semibold">Dark mode</span>
			{/if}
		</button>

		<NotificationToggle {theme} variant="sidebar" />

		<button
			onclick={() => (showFeedbackModal = true)}
			class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-white/45 hover:text-white' : 'text-black/45 hover:text-black'}`}
		>
			<MessageSquare class="h-4 w-4 shrink-0" />
			<span class="text-[10px] font-semibold">Feedback</span>
		</button>

		<button
			type="button"
			onclick={() => authClient.signOut()}
			class={`flex w-full items-center gap-3 rounded-md px-3 py-2 transition-all ${dark ? 'text-white/45 hover:text-red-400' : 'text-black/45 hover:text-red-600'}`}
		>
			<LogOut class="h-4 w-4 shrink-0" />
			<span class="text-[10px] font-semibold">Sign out</span>
		</button>
	</div>
</nav>

<FeedbackModal bind:show={showFeedbackModal} {theme} />
