<script lang="ts">
	import { Search, X } from 'lucide-svelte';
	import { inputClass } from '$lib/ui-styles';
	import AxonMark from '$lib/components/ui/AxonMark.svelte';

	type Props = {
		title: string;
		articleCount: number;
		searchQuery: string;
		syncIndicator: boolean;
		theme: 'dark' | 'light';
		onSearchChange: (value: string) => void;
		hasSemanticSearch?: boolean;
	};

	let { title, articleCount, searchQuery, syncIndicator, theme, onSearchChange, hasSemanticSearch = false }: Props = $props();

	let dark = $derived(theme === 'dark');
	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');
</script>

<header class={`sticky top-0 z-20 min-w-0 overflow-hidden border-b ${dark ? 'border-white/10 bg-[#0a0a0a]/95' : 'border-black/10 bg-[#fafafa]/95'}`}>
	<div class="flex h-14 min-w-0 items-center gap-3 px-4 sm:px-5">
		<!-- Mobile brand mark -->
		<div class="flex shrink-0 items-center gap-2.5 lg:hidden">
			<span class={`flex h-6 w-6 items-center justify-center ${dark ? 'bg-white text-black' : 'bg-black text-white'}`}>
				<AxonMark class="h-4 w-4" />
			</span>
			<span class={`text-[12px] font-semibold uppercase tracking-[0.24em] ${dark ? 'text-white' : 'text-black'}`}>Axon</span>
		</div>

		<!-- Desktop title -->
		<div class="hidden min-w-0 items-baseline gap-3 lg:flex">
			<h2 class={`text-[15px] font-semibold tracking-tight ${dark ? 'text-white' : 'text-black'}`}>{title}</h2>
			<span class={`axon-label tabular-nums ${muted}`}>{articleCount} shown</span>
			{#if syncIndicator}
				<span class={`axon-label ${dark ? 'text-white/70' : 'text-black/70'}`}>Syncing</span>
			{/if}
			{#if hasSemanticSearch}
				<span class={`axon-label border px-1.5 py-0.5 ${dark ? 'border-white/20 text-white/70' : 'border-black/20 text-black/70'}`}>Semantic</span>
			{/if}
		</div>

		<label class="group relative ml-auto min-w-0 flex-1 sm:flex-none">
			<Search class={`pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 lg:left-3 ${muted}`} />
			<input
				type="search"
				value={searchQuery}
				oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
				placeholder="Search the feed"
				class={`${inputClass(theme)} w-full pl-8 pr-8 sm:w-48 sm:focus:w-60 lg:w-56 lg:pl-9 lg:focus:w-72 [&::-webkit-search-cancel-button]:hidden`}
			/>
			{#if searchQuery}
				<button
					type="button"
					onclick={() => onSearchChange('')}
					class={`absolute right-1.5 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center ${muted} ${dark ? 'hover:text-white' : 'hover:text-black'}`}
					aria-label="Clear search"
				>
					<X class="h-3.5 w-3.5" />
				</button>
			{/if}
		</label>
	</div>
</header>
