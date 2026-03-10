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

<div class="rounded-xl border border-white/[0.06] bg-[#111]/80 p-2.5 shadow-[0_16px_48px_rgba(0,0,0,0.4)] backdrop-blur-2xl sm:p-3">
	{#if showSuggestions}
		<div class="no-scrollbar mb-2 flex gap-2 overflow-x-auto px-1">
			{#each suggestions as tip}
				<button
					type="button"
					onclick={() => onSend(tip)}
					class="whitespace-nowrap rounded-md bg-white/[0.04] px-2.5 py-1 text-[10px] font-medium text-zinc-500 transition-colors hover:bg-white/[0.08] hover:text-zinc-300"
				>
					{tip}
				</button>
			{/each}
		</div>
	{/if}

	<div class="relative flex items-center rounded-lg bg-white/[0.03] px-3">
		<input
			type="text"
			value={chatInput}
			oninput={(event) => onInputChange((event.currentTarget as HTMLInputElement).value)}
			onkeydown={(event) => event.key === 'Enter' && onSend()}
			placeholder="Ask about this signal..."
			class="h-9 w-full bg-transparent pr-10 text-[13px] text-white outline-none placeholder:text-zinc-600"
		/>
		<button
			type="button"
			onclick={() => onSend()}
			disabled={!chatInput.trim() || chatLoading}
			class="absolute right-1.5 flex h-7 w-7 items-center justify-center rounded-md text-zinc-400 transition-all hover:bg-white/5 hover:text-white disabled:opacity-20"
			aria-label="Send message"
		>
			<Send class="h-3.5 w-3.5" />
		</button>
	</div>
</div>
