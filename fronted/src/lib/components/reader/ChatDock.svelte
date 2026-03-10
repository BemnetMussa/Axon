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

<div class="rounded-xl border border-white/[0.08] bg-[#111]/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)] backdrop-blur-2xl">
	{#if showSuggestions}
		<div class="no-scrollbar flex gap-1.5 overflow-x-auto border-b border-white/[0.04] px-3 py-2">
			{#each suggestions as tip}
				<button
					type="button"
					onclick={() => onSend(tip)}
					class="whitespace-nowrap rounded-md border border-white/[0.06] px-2.5 py-1.5 text-[10.5px] text-zinc-400 transition-colors hover:border-white/15 hover:bg-white/[0.04] hover:text-zinc-200"
				>
					{tip}
				</button>
			{/each}
		</div>
	{/if}

	<div class="flex items-center gap-2 px-3 py-2">
		<input
			type="text"
			value={chatInput}
			oninput={(event) => onInputChange((event.currentTarget as HTMLInputElement).value)}
			onkeydown={(event) => event.key === 'Enter' && onSend()}
			placeholder="Ask about this signal..."
			class="h-8 min-w-0 flex-1 bg-transparent text-[13px] text-white outline-none placeholder:text-zinc-600"
		/>
		<button
			type="button"
			onclick={() => onSend()}
			disabled={!chatInput.trim() || chatLoading}
			class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/[0.06] text-zinc-400 transition-all hover:bg-white/[0.12] hover:text-white disabled:opacity-20"
			aria-label="Send message"
		>
			<Send class="h-3.5 w-3.5" />
		</button>
	</div>
</div>
