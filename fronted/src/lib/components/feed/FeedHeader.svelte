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

<header class="sticky top-0 z-20 border-b border-white/5 bg-[#0b0b0b]/90 backdrop-blur-xl">
	<div class="flex flex-col gap-4 px-4 py-4 sm:px-6 lg:px-10 lg:py-5">
		<div class="flex items-center justify-between gap-4 lg:hidden">
			<div class="flex items-center gap-3">
				<div class="flex h-9 w-9 items-center justify-center rounded-xl bg-white">
					<Zap class="h-4 w-4 fill-black text-black" />
				</div>
				<div>
					<p class="text-[10px] font-bold uppercase tracking-[2.2px] text-zinc-600">Signal Desk</p>
					<h1 class="text-[18px] font-black uppercase tracking-[3px] text-white italic">Axon</h1>
				</div>
			</div>

			<button
				onclick={onRefresh}
				class="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/8 bg-white/3 text-zinc-300 transition-all hover:border-white/18 hover:text-white"
				aria-label="Refresh feed"
			>
				<RefreshCw class={`h-4 w-4 ${syncIndicator ? 'animate-spin' : ''}`} />
			</button>
		</div>

		<div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
			<div class="flex items-center gap-3 sm:gap-4">
				<div>
					<p class="text-[10px] font-bold uppercase tracking-[2.2px] text-zinc-600 lg:hidden">Current Surface</p>
					<h2 class="text-[16px] font-black uppercase tracking-[3px] text-white italic sm:text-[18px] sm:tracking-[4px]">
						{title}
					</h2>
				</div>
				<div class="h-1 w-1 rounded-full bg-zinc-800"></div>
				<span class="text-[10px] font-bold uppercase tracking-[2px] text-zinc-600 sm:tracking-widest">
					{articleCount} Signals
				</span>
			</div>

			<div class="flex items-center gap-3 lg:min-w-[18rem] lg:max-w-sm lg:flex-1 lg:justify-end">
				<label class="group relative flex-1 lg:max-w-xs">
					<Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-zinc-600 transition-colors group-focus-within:text-white" />
					<input
						type="text"
						value={searchQuery}
						oninput={(event) => onSearchChange((event.currentTarget as HTMLInputElement).value)}
						placeholder="Interrogate feed..."
						class="h-11 w-full rounded-2xl border border-white/8 bg-white/3 pl-10 pr-4 text-[13px] text-white outline-none transition-all placeholder:text-zinc-700 focus:border-white/20 focus:bg-white/5"
					/>
				</label>

				<button
					onclick={onRefresh}
					class="hidden h-11 min-w-11 items-center justify-center rounded-2xl border border-white/8 bg-white/3 text-zinc-300 transition-all hover:border-white/18 hover:text-white lg:flex"
					aria-label="Refresh feed"
				>
					<RefreshCw class={`h-4 w-4 ${syncIndicator ? 'animate-spin' : ''}`} />
				</button>
			</div>
		</div>
	</div>
</header>