<script lang="ts">
	import { Zap, Sparkles, Menu, Sun, Moon, X } from 'lucide-svelte';
	import type { NavItem } from '$lib/ui';
	import NotificationToggle from '../ui/NotificationToggle.svelte';

	type Props = {
		items: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		showDigestView: boolean;
		theme: 'dark' | 'light';
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: () => void;
	};

	let { items, activeCategory, showSavedOnly, showDigestView, theme, onNavigate, onShowSaved, onShowDigest, onToggleTheme }: Props = $props();
	let dark = $derived(theme === 'dark');
	let showMenu = $state(false);

	// Frontier + Trending as primary tabs
	let mainTabs = $derived(items.filter(i => i.id === null || i.id === 'Trending'));
	// Everything else goes into overflow menu
	let overflowTabs = $derived(items.filter(i => i.id !== null && i.id !== 'Trending'));

	function navBg() {
		return dark ? 'border-white/10 bg-[#0a0a0a]/95' : 'border-black/10 bg-[#fafafa]/95';
	}

	function tabColor(active: boolean) {
		if (active) return dark ? 'text-white' : 'text-black';
		return dark ? 'text-white/40' : 'text-black/40';
	}

	function marker(active: boolean) {
		return active ? (dark ? 'bg-white' : 'bg-black') : 'bg-transparent';
	}
</script>

<!-- Overflow menu sheet -->
{#if showMenu}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-[51] bg-black/60 backdrop-blur-sm lg:hidden"
		onclick={() => (showMenu = false)}
	></div>
	<div
		class={`fixed inset-x-0 z-[52] max-h-[min(85vh,calc(100dvh-5rem))] overflow-y-auto border-t px-3 pt-4 lg:hidden ${dark ? 'border-white/10 bg-[#0a0a0a]' : 'border-black/10 bg-[#fafafa]'}`}
		style="bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)); padding-bottom: calc(0.75rem + env(safe-area-inset-bottom, 0px));"
	>
		<div class="mb-3 flex items-center justify-between px-1">
			<h3 class={`text-sm font-bold ${dark ? 'text-white' : 'text-black'}`}>Explore</h3>
			<button
				onclick={() => (showMenu = false)}
				class={`flex h-8 w-8 items-center justify-center rounded-lg ${dark ? 'text-zinc-400 hover:text-zinc-200' : 'text-zinc-500 hover:text-zinc-700'}`}
			>
				<X class="h-5 w-5" />
			</button>
		</div>

		<div class="flex flex-col gap-1">
			{#each overflowTabs as item}
				<button
					onclick={() => { onNavigate(item.id); showMenu = false; }}
					class={`flex items-center gap-3 rounded-xl px-3 py-3 text-left ${
						activeCategory === item.id
							? dark ? 'bg-white/10 text-white' : 'bg-black/5 text-black'
							: dark ? 'text-zinc-400 hover:bg-white/[0.04]' : 'text-zinc-600 hover:bg-zinc-50'
					}`}
				>
					<item.icon class="h-5 w-5 shrink-0" />
					<span class="text-[13px] font-semibold">{item.label}</span>
				</button>
			{/each}

			<button
				onclick={() => { onShowDigest(); showMenu = false; }}
				class={`flex items-center gap-3 rounded-xl px-3 py-3 ${
					showDigestView
						? dark ? 'bg-white/10 text-white' : 'bg-black/5 text-black'
						: dark ? 'text-zinc-400 hover:bg-white/[0.04]' : 'text-zinc-600 hover:bg-zinc-50'
				}`}
			>
				<Sparkles class="h-5 w-5 shrink-0" />
				<span class="text-[13px] font-semibold">Weekly Digest</span>
			</button>

			<div class={`my-2 h-px ${dark ? 'bg-white/[0.06]' : 'bg-zinc-100'}`}></div>

			<NotificationToggle {theme} variant="mobile" />

			<button
				onclick={() => { onToggleTheme(); showMenu = false; }}
				class={`flex items-center gap-3 rounded-xl px-3 py-3 ${dark ? 'text-zinc-400 hover:bg-white/[0.04]' : 'text-zinc-600 hover:bg-zinc-50'}`}
			>
				{#if dark}
					<Sun class="h-5 w-5 shrink-0" />
					<span class="text-[13px] font-semibold">Light mode</span>
				{:else}
					<Moon class="h-5 w-5 shrink-0" />
					<span class="text-[13px] font-semibold">Dark mode</span>
				{/if}
			</button>
		</div>
	</div>
{/if}

<!-- Bottom nav bar -->
<nav
	class={`fixed inset-x-0 bottom-0 z-40 flex items-stretch justify-around border-t backdrop-blur-md lg:hidden ${navBg()}`}
	style="padding-bottom: env(safe-area-inset-bottom, 0px);"
>
	{#each mainTabs as item}
		{@const active = activeCategory === item.id && !showSavedOnly && !showDigestView}
		<button onclick={() => onNavigate(item.id)} class={`relative flex h-14 min-w-0 flex-1 flex-col items-center justify-center gap-1 transition-colors ${tabColor(active)}`}>
			<span class={`absolute top-0 h-[2px] w-8 ${marker(active)}`}></span>
			<item.icon class="h-5 w-5 shrink-0" />
			<span class="axon-label truncate !text-[9px] leading-none">{item.label}</span>
		</button>
	{/each}

	<button onclick={onShowSaved} class={`relative flex h-14 min-w-0 flex-1 flex-col items-center justify-center gap-1 transition-colors ${tabColor(showSavedOnly)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(showSavedOnly)}`}></span>
		<Zap class={`h-5 w-5 shrink-0 ${showSavedOnly ? 'fill-current' : ''}`} />
		<span class="axon-label truncate !text-[9px] leading-none">Saved</span>
	</button>

	<button onclick={onShowDigest} class={`relative flex h-14 min-w-0 flex-1 flex-col items-center justify-center gap-1 transition-colors ${tabColor(showDigestView)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(showDigestView)}`}></span>
		<Sparkles class="h-5 w-5 shrink-0" />
		<span class="axon-label truncate !text-[9px] leading-none">Digest</span>
	</button>

	<button onclick={() => (showMenu = true)} class={`relative flex h-14 min-w-0 flex-1 flex-col items-center justify-center gap-1 transition-colors ${tabColor(showMenu)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(showMenu)}`}></span>
		<Menu class="h-5 w-5 shrink-0" />
		<span class="axon-label truncate !text-[9px] leading-none">More</span>
	</button>
</nav>
