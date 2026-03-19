<script lang="ts">
	import { Zap, Sparkles, Menu, Sun, Moon, X } from 'lucide-svelte';
	import type { NavItem } from '$lib/ui';

	type Props = {
		items: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		theme: 'dark' | 'light';
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: () => void;
	};

	let { items, activeCategory, showSavedOnly, theme, onNavigate, onShowSaved, onShowDigest, onToggleTheme }: Props = $props();
	let dark = $derived(theme === 'dark');
	let showMenu = $state(false);

	let mainItem = $derived(items[0]);
	let restItems = $derived(items.slice(1));

	function navBg() {
		return dark ? 'border-white/[0.04] bg-[#0b0b0b]/95' : 'border-zinc-200 bg-white/95';
	}

	function itemColor(active: boolean) {
		if (active) return dark ? 'text-white' : 'text-black';
		return dark ? 'text-zinc-600' : 'text-zinc-400';
	}
</script>

{#if showMenu}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm lg:hidden transition-opacity" onclick={() => showMenu = false}></div>
	<div class={`fixed inset-x-0 bottom-0 z-50 rounded-t-2xl lg:hidden ${dark ? 'bg-[#111]' : 'bg-white'} p-4 transition-transform`}>
		<div class="mb-4 flex items-center justify-between px-2">
			<h3 class={`text-sm font-bold ${dark ? 'text-white' : 'text-black'}`}>Explore</h3>
			<button onclick={() => showMenu = false}><X class={`h-5 w-5 ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} /></button>
		</div>
		
		<div class="flex flex-col gap-2">
			{#each restItems as item}
				<button onclick={() => { onNavigate(item.id); showMenu = false; }} class={`flex items-center gap-3 rounded-lg p-3 ${activeCategory === item.id ? (dark ? 'bg-white/10 text-white' : 'bg-black/5 text-black') : (dark ? 'text-zinc-400' : 'text-zinc-600')}`}>
					<item.icon class="h-5 w-5" />
					<span class="text-xs font-semibold">{item.label}</span>
				</button>
			{/each}
			<hr class={`my-2 w-full ${dark ? 'border-white/10' : 'border-black/5'}`} />
			<button onclick={() => { onToggleTheme(); showMenu = false; }} class={`flex items-center gap-3 rounded-lg p-3 ${dark ? 'text-zinc-400' : 'text-zinc-600'}`}>
				{#if dark}
					<Sun class="h-5 w-5" />
					<span class="text-xs font-semibold">Light Mode</span>
				{:else}
					<Moon class="h-5 w-5" />
					<span class="text-xs font-semibold">Dark Mode</span>
				{/if}
			</button>
		</div>
	</div>
{/if}

<nav
	class={`fixed inset-x-0 bottom-0 z-40 flex items-center justify-around border-t pb-[env(safe-area-inset-bottom,0px)] lg:hidden ${navBg()}`}
	style="backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px)"
>
	<button
		onclick={() => onNavigate(mainItem.id)}
		class={`flex flex-col items-center gap-0.5 px-1 py-2 transition-colors ${itemColor(activeCategory === mainItem.id && !showSavedOnly)}`}
	>
		<mainItem.icon class="h-4 w-4" />
		<span class="truncate text-[8px] font-semibold">{mainItem.label}</span>
	</button>

	<button
		onclick={onShowSaved}
		class={`flex flex-col items-center gap-0.5 px-1 py-2 transition-colors ${itemColor(showSavedOnly)}`}
	>
		<Zap class={`h-4 w-4 ${showSavedOnly ? (dark ? 'fill-white' : 'fill-black') : ''}`} />
		<span class="truncate text-[8px] font-semibold">Saved</span>
	</button>

	<button
		onclick={onShowDigest}
		class={`flex flex-col items-center gap-0.5 px-1 py-2 transition-colors ${itemColor(false)}`}
	>
		<Sparkles class="h-4 w-4" />
		<span class="truncate text-[8px] font-semibold">Digest</span>
	</button>

	<button
		onclick={() => showMenu = true}
		class={`flex flex-col items-center gap-0.5 px-1 py-2 transition-colors ${itemColor(showMenu)}`}
	>
		<Menu class="h-4 w-4" />
		<span class="truncate text-[8px] font-semibold">Menu</span>
	</button>
</nav>
