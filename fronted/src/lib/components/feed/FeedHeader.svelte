<script lang="ts">
	import { RefreshCw, Search, Zap } from 'lucide-svelte';

	type Props = {
		title: string;
		articleCount: number;
		searchQuery: string;
		syncIndicator: boolean;
		onSearchChange: (value: string) => void;
		onRefresh: () => void;
	};

	let { title, articleCount, searchQuery, syncIndicator, onSearchChange, onRefresh }: Props = $props();
</script>

<header class="sticky top-0 z-20 border-b border-white/[0.04] bg-[#0b0b0b]/90 backdrop-blur-xl">
	<div class="flex items-center gap-3 px-4 py-3 sm:px-5">
		<div class="flex items-center gap-2.5 lg:hidden">
			<div class="flex h-7 w-7 items-center justify-center rounded-md bg-white">
				<Zap class="h-3.5 w-3.5 fill-black text-black" />
			</div>
			<span class="text-[13px] font-black uppercase tracking-[2px] text-white italic">Axon</span>
		</div>

		<div class="hidden items-baseline gap-2.5 lg:flex">
			<h2 class="text-[14px] font-bold text-white">
				{title}
			</h2>
			<span class="text-[10px] font-medium tabular-nums text-zinc-600">
				{articleCount}
			</span>
		</div>

		<div class="ml-auto flex items-center gap-2">
			<label class="group relative">
				<Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-zinc-600 transition-colors group-focus-within:text-zinc-300" />
				<input
					type="text"
					value={searchQuery}
					oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
					placeholder="Search..."
					class="h-8 w-36 rounded-md border border-white/[0.06] bg-white/[0.03] pl-8 pr-3 text-[12px] text-white outline-none transition-all placeholder:text-zinc-600 focus:w-52 focus:border-white/15 focus:bg-white/[0.05] sm:w-44 sm:focus:w-64"
				/>
			</label>

			<button
				onclick={onRefresh}
				class="flex h-8 w-8 items-center justify-center rounded-md border border-white/[0.06] bg-white/[0.03] text-zinc-400 transition-all hover:border-white/15 hover:text-white"
				aria-label="Refresh feed"
			>
				<RefreshCw class={`h-3.5 w-3.5 ${syncIndicator ? 'animate-spin' : ''}`} />
			</button>
		</div>
	</div>

	<div class="flex items-baseline gap-2.5 px-4 pb-2.5 sm:px-5 lg:hidden">
		<h2 class="text-[14px] font-bold text-white">{title}</h2>
		<span class="text-[10px] font-medium tabular-nums text-zinc-600">{articleCount}</span>
	</div>
</header>
