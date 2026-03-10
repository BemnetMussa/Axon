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

<nav class="fixed inset-x-0 bottom-0 z-40 border-t border-white/[0.06] bg-[#090909]/95 px-1.5 pb-[calc(env(safe-area-inset-bottom,0px)+0.35rem)] pt-1 backdrop-blur-xl lg:hidden">
	<div class="flex items-center justify-around">
		{#each items as item}
			<button
				onclick={() => onNavigate(item.id)}
				class={`flex min-w-0 flex-1 flex-col items-center justify-center gap-0.5 rounded-lg px-1 py-1.5 text-[8px] font-bold uppercase tracking-wider transition-all ${activeCategory === item.id && !showSavedOnly ? 'bg-white text-black' : 'text-zinc-500 active:bg-white/5'}`}
			>
				<item.icon class="h-4 w-4 shrink-0" />
				<span class="truncate">{item.label.split(' ')[0]}</span>
			</button>
		{/each}

		<button
			onclick={onShowSaved}
			class={`flex min-w-0 flex-1 flex-col items-center justify-center gap-0.5 rounded-lg px-1 py-1.5 text-[8px] font-bold uppercase tracking-wider transition-all ${showSavedOnly ? 'bg-white text-black' : 'text-zinc-500 active:bg-white/5'}`}
		>
			<Zap class="h-4 w-4 shrink-0" />
			<span>Saved</span>
		</button>
	</div>
</nav>
