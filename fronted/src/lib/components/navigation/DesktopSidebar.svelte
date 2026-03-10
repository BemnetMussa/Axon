<script lang="ts">
	import { Command, Zap } from 'lucide-svelte';
	import type { NavItem } from '$lib/ui';

	type Props = {
		navigation: NavItem[];
		activeCategory: string | null;
		showSavedOnly: boolean;
		sourceCounts: Record<string, number>;
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
	};

	let { navigation, activeCategory, showSavedOnly, sourceCounts, onNavigate, onShowSaved }: Props = $props();
</script>

<nav class="hidden w-56 shrink-0 flex-col items-stretch border-r border-white/[0.04] bg-[#0b0b0b] py-8 lg:flex">
	<div class="mb-12 px-7">
		<div class="flex items-center gap-3">
			<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white">
				<Zap class="h-4 w-4 fill-black text-black" />
			</div>
			<span class="text-[14px] font-black uppercase tracking-[3px] text-white italic">Axon</span>
		</div>
	</div>

	<div class="flex flex-col gap-2 px-3">
		{#each navigation as item}
			<button
				onclick={() => onNavigate(item.id)}
				class={`relative flex min-h-12 items-center gap-4 rounded-xl px-4 py-3 transition-all duration-300 ${activeCategory === item.id && !showSavedOnly ? 'bg-white/[0.05] text-white' : 'text-zinc-500 hover:bg-white/[0.02] hover:text-zinc-300'}`}
			>
				<item.icon class="h-5 w-5 shrink-0" />
				<span class="text-[11px] font-bold uppercase tracking-[2px]">{item.label}</span>

				{#if activeCategory === item.id && !showSavedOnly}
					<div class="absolute -left-[12px] top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-white"></div>
				{/if}
			</button>
		{/each}

		<button
			onclick={onShowSaved}
			class={`relative flex min-h-12 items-center gap-4 rounded-xl px-4 py-3 transition-all duration-300 ${showSavedOnly ? 'bg-white/[0.05] text-white' : 'text-zinc-500 hover:bg-white/[0.02] hover:text-zinc-300'}`}
		>
			<Zap class="h-5 w-5 shrink-0" />
			<span class="text-[11px] font-bold uppercase tracking-[2px]">Saved</span>

			{#if showSavedOnly}
				<div class="absolute -left-[12px] top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-white"></div>
			{/if}
		</button>
	</div>

	<div class="mb-8 mt-auto px-6">
		<span class="mb-4 block px-4 text-[9px] font-bold uppercase tracking-[2px] text-zinc-700">Sources</span>
		<div class="flex flex-col gap-1 px-4">
			{#each Object.entries(sourceCounts) as [source, count]}
				<div class="group flex cursor-default items-center justify-between text-[10px] font-medium transition-colors hover:text-white">
					<span class="text-zinc-500 transition-colors group-hover:text-zinc-300">{source}</span>
					<span class="tabular-nums font-bold uppercase text-zinc-700 transition-colors group-hover:text-zinc-500">{count}</span>
				</div>
			{/each}
		</div>
	</div>

	<div class="px-6">
		<button class="flex min-h-12 w-full items-center gap-4 rounded-xl px-4 py-3 text-zinc-700 transition-all hover:bg-white/[0.02] hover:text-white">
			<Command class="h-5 w-5 shrink-0" />
			<span class="text-[10px] font-bold uppercase tracking-widest">Feedback</span>
		</button>
	</div>
</nav>