<script lang="ts">
	import { Zap } from 'lucide-svelte';
	import type { NavItem } from '$lib/ui';

	type Props = {
		items: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
	};

	let { items, activeCategory, showSavedOnly, onNavigate, onShowSaved }: Props = $props();
</script>

<nav class="fixed inset-x-0 bottom-0 z-40 border-t border-white/[0.06] bg-[#090909]/95 px-2 pb-[calc(env(safe-area-inset-bottom,0px)+0.4rem)] pt-1.5 backdrop-blur-xl lg:hidden">
	<div class="grid grid-cols-4 gap-1">
		{#each items as item}
			<button
				onclick={() => onNavigate(item.id)}
				class={`flex flex-col items-center justify-center gap-0.5 rounded-lg px-2 py-2 text-[9px] font-bold uppercase tracking-wider transition-all ${activeCategory === item.id && !showSavedOnly ? 'bg-white text-black' : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300'}`}
			>
				<item.icon class="h-4 w-4" />
				<span>{item.label.split(' ')[0]}</span>
			</button>
		{/each}

		<button
			onclick={onShowSaved}
			class={`flex flex-col items-center justify-center gap-0.5 rounded-lg px-2 py-2 text-[9px] font-bold uppercase tracking-wider transition-all ${showSavedOnly ? 'bg-white text-black' : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-300'}`}
		>
			<Zap class="h-4 w-4" />
			<span>Saved</span>
		</button>
	</div>
</nav>
