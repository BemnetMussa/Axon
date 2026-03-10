<script lang="ts">
	import { Send } from 'lucide-svelte';

	type Props = {
		chatInput: string;
		chatLoading: boolean;
		suggestions: string[];
		showSuggestions: boolean;
		onInputChange: (value: string) => void;
		onSend: (message?: string) => void;
	};

	let { chatInput, chatLoading, suggestions, showSuggestions, onInputChange, onSend }: Props = $props();
</script>

<div class="rounded-[1.85rem] border border-white/8 bg-[#111214]/66 p-3 shadow-[0_24px_80px_rgba(0,0,0,0.42)] backdrop-blur-2xl sm:p-4">
	{#if showSuggestions}
		<div class="no-scrollbar mb-3 flex gap-3 overflow-x-auto px-1">
			{#each suggestions as tip}
				<button
					type="button"
					onclick={() => onSend(tip)}
					class="whitespace-nowrap border-0 bg-transparent px-0 py-1 text-[11px] font-medium text-zinc-500 transition-colors hover:text-white"
				>
					{tip}
				</button>
			{/each}
		</div>
	{/if}

	<div class="relative rounded-[1.55rem] border border-white/8 bg-black/20 px-4 py-3">
		<input
			type="text"
			value={chatInput}
			oninput={(event) => onInputChange((event.currentTarget as HTMLInputElement).value)}
			onkeydown={(event) => event.key === 'Enter' && onSend()}
			placeholder="Ask about this signal..."
			class="w-full bg-transparent py-1 pr-12 text-[14px] leading-relaxed text-white outline-none placeholder:text-zinc-600"
		/>
		<button
			type="button"
			onclick={() => onSend()}
			disabled={!chatInput.trim() || chatLoading}
			class="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-2xl text-white transition-all hover:bg-white/5 hover:text-zinc-300 disabled:opacity-20"
			aria-label="Send message"
		>
			<Send class="h-4 w-4" />
		</button>
	</div>
</div>