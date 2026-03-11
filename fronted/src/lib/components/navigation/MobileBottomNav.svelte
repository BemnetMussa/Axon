<script lang="ts">
	import { Zap } from 'lucide-svelte';
	import type { NavItem } from '$lib/ui';

	type Props = {
		items: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		theme: 'dark' | 'light';
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
	};

	let { items, activeCategory, showSavedOnly, theme, onNavigate, onShowSaved }: Props = $props();
	let dark = $derived(theme === 'dark');

	function navBg() {
		return dark ? 'border-white/[0.04] bg-[#0b0b0b]/95' : 'border-zinc-200 bg-white/95';
	}

	function itemColor(active: boolean) {
		if (active) return dark ? 'text-white' : 'text-black';
		return dark ? 'text-zinc-600' : 'text-zinc-400';
	}
</script>

<nav
	class={`fixed inset-x-0 bottom-0 z-40 flex items-center justify-around border-t pb-[env(safe-area-inset-bottom,0px)] lg:hidden ${navBg()}`}
	style="backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px)"
>
	{#each items as item}
		<button
			onclick={() => onNavigate(item.id)}
			class={`flex flex-col items-center gap-0.5 px-1 py-2 transition-colors ${itemColor(activeCategory === item.id && !showSavedOnly)}`}
		>
			<item.icon class="h-4 w-4" />
			<span class="truncate text-[8px] font-semibold">{item.label}</span>
		</button>
	{/each}

	<button
		onclick={onShowSaved}
		class={`flex flex-col items-center gap-0.5 px-1 py-2 transition-colors ${itemColor(showSavedOnly)}`}
	>
		<Zap class={`h-4 w-4 ${showSavedOnly ? (dark ? 'fill-white' : 'fill-black') : ''}`} />
		<span class="truncate text-[8px] font-semibold">Saved</span>
	</button>
</nav>
