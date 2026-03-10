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

<nav class="hidden w-52 shrink-0 flex-col border-r border-white/[0.04] bg-[#0b0b0b] lg:flex">
	<div class="flex items-center gap-2.5 px-5 py-4">
		<div class="flex h-7 w-7 items-center justify-center rounded-md bg-white">
			<Zap class="h-3.5 w-3.5 fill-black text-black" />
		</div>
		<span class="text-[13px] font-black uppercase tracking-[2px] text-white italic">Axon</span>
	</div>

	<div class="flex flex-col gap-0.5 px-2.5 pt-2">
		{#each navigation as item}
			<button
				onclick={() => onNavigate(item.id)}
				class={`relative flex items-center gap-3 rounded-md px-3 py-2 transition-all ${activeCategory === item.id && !showSavedOnly ? 'bg-white/[0.06] text-white' : 'text-zinc-500 hover:bg-white/[0.03] hover:text-zinc-300'}`}
			>
				<item.icon class="h-4 w-4 shrink-0" />
				<span class="text-[11px] font-semibold">{item.label}</span>

				{#if activeCategory === item.id && !showSavedOnly}
					<div class="absolute -left-2.5 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-r-full bg-white"></div>
				{/if}
			</button>
		{/each}

		<button
			onclick={onShowSaved}
			class={`relative flex items-center gap-3 rounded-md px-3 py-2 transition-all ${showSavedOnly ? 'bg-white/[0.06] text-white' : 'text-zinc-500 hover:bg-white/[0.03] hover:text-zinc-300'}`}
		>
			<Zap class="h-4 w-4 shrink-0" />
			<span class="text-[11px] font-semibold">Saved</span>

			{#if showSavedOnly}
				<div class="absolute -left-2.5 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-r-full bg-white"></div>
			{/if}
		</button>
	</div>

	<div class="mt-auto px-5 pb-3">
		<p class="mb-2 text-[9px] font-bold uppercase tracking-widest text-zinc-700">Sources</p>
		<div class="flex flex-col gap-0.5">
			{#each Object.entries(sourceCounts) as [source, count]}
				<div class="flex items-center justify-between py-0.5 text-[10px]">
					<span class="text-zinc-500">{source}</span>
					<span class="tabular-nums text-zinc-700">{count}</span>
				</div>
			{/each}
		</div>
	</div>

	<div class="border-t border-white/[0.04] px-2.5 py-2">
		<button class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-zinc-600 transition-all hover:bg-white/[0.03] hover:text-zinc-300">
			<Command class="h-4 w-4 shrink-0" />
			<span class="text-[10px] font-semibold">Feedback</span>
		</button>
	</div>
</nav>
