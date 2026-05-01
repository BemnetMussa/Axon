<script lang="ts">
	import { Zap, Sparkles, Menu, Sun, Moon, X } from 'lucide-svelte';
	import type { NavItem } from '$lib/ui';

	type Props = {
		items: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		showDigestView: boolean;
		theme: 'dark' | 'light';
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: (e: MouseEvent) => void;
	};

	let { items, activeCategory, showSavedOnly, showDigestView, theme, onNavigate, onShowSaved, onShowDigest, onToggleTheme }: Props = $props();
	let dark = $derived(theme === 'dark');
	let showMenu = $state(false);

	// Frontier + Trending as primary tabs
	let mainTabs = $derived(items.filter(i => i.id === null || i.id === 'Trending'));
	// Everything else goes into overflow menu
	let overflowTabs = $derived(items.filter(i => i.id !== null && i.id !== 'Trending'));

	function navBg() {
		return dark
			? 'border-white/[0.06] bg-[#0b0b0b]/92 shadow-[0_-1px_0_rgba(255,255,255,0.04)]'
			: 'border-zinc-200 bg-white/92 shadow-[0_-1px_0_rgba(0,0,0,0.04)]';
	}

	function tabColor(active: boolean) {
		if (active) return dark ? 'text-white' : 'text-black';
		return dark ? 'text-zinc-500' : 'text-zinc-400';
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
		class={`fixed inset-x-0 z-[52] max-h-[min(85vh,calc(100dvh-5rem))] overflow-y-auto rounded-t-2xl px-3 pt-4 lg:hidden ${dark ? 'bg-[#111]' : 'bg-white'}`}
		style="bottom: calc(5.75rem + env(safe-area-inset-bottom, 0px)); padding-bottom: calc(0.75rem + env(safe-area-inset-bottom, 0px));"
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

			<button
				onclick={(e) => { onToggleTheme(e); showMenu = false; }}
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
	class={`fixed inset-x-2 bottom-2 z-40 flex items-stretch justify-around rounded-2xl border backdrop-blur-2xl lg:hidden ${navBg()}`}
	style="padding-bottom: env(safe-area-inset-bottom, 0px);"
>
	{#each mainTabs as item}
		<button
			onclick={() => onNavigate(item.id)}
			class={`flex min-w-0 flex-1 flex-col items-center gap-1 px-1 py-3.5 transition-colors ${tabColor(activeCategory === item.id && !showSavedOnly && !showDigestView)}`}
		>
			<item.icon class="h-[22px] w-[22px] shrink-0" />
			<span class="truncate text-[10px] font-bold leading-none">{item.label}</span>
		</button>
	{/each}

	<!-- Saved -->
	<button
		onclick={onShowSaved}
		class={`flex min-w-0 flex-1 flex-col items-center gap-1 px-1 py-3.5 transition-colors ${tabColor(showSavedOnly)}`}
	>
		<Zap class={`h-[22px] w-[22px] shrink-0 ${showSavedOnly ? (dark ? 'fill-white' : 'fill-black') : ''}`} />
		<span class="truncate text-[10px] font-bold leading-none">Saved</span>
	</button>

	<!-- Digest -->
	<button
		onclick={onShowDigest}
		class={`flex min-w-0 flex-1 flex-col items-center gap-1 px-1 py-3.5 transition-colors ${tabColor(showDigestView)}`}
	>
		<Sparkles class="h-[22px] w-[22px] shrink-0" />
		<span class="truncate text-[10px] font-bold leading-none">Weekly Digest</span>
	</button>

	<!-- More -->
	<button
		onclick={() => (showMenu = true)}
		class={`flex min-w-0 flex-1 flex-col items-center gap-1 px-1 py-3.5 transition-colors ${tabColor(showMenu)}`}
	>
		<Menu class="h-[22px] w-[22px] shrink-0" />
		<span class="truncate text-[10px] font-bold leading-none">More</span>
	</button>
</nav>
