<script lang="ts">
	import { Send } from 'lucide-svelte';

	type Props = {
		chatInput: string;
		chatLoading: boolean;
		suggestions: string[];
		showSuggestions: boolean;
		theme: 'dark' | 'light';
		onInputChange: (value: string) => void;
		onSend: (message?: string) => void;
	};

	let { chatInput, chatLoading, suggestions, showSuggestions, theme, onInputChange, onSend }: Props = $props();
	let dark = $derived(theme === 'dark');
</script>

<div class={`rounded-xl border shadow-lg backdrop-blur-2xl ${dark ? 'border-white/[0.08] bg-[#111]/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)]' : 'border-zinc-200 bg-white/95 shadow-[0_4px_24px_rgba(0,0,0,0.08)]'}`}>
	{#if showSuggestions}
		<div class={`no-scrollbar flex gap-1.5 overflow-x-auto border-b px-3 py-2 ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
			{#each suggestions as tip}
				<button
					type="button"
					onclick={() => onSend(tip)}
					class={`whitespace-nowrap rounded-md border px-2.5 py-1.5 text-[10.5px] transition-colors ${dark ? 'border-white/[0.06] text-zinc-400 hover:border-white/15 hover:text-zinc-200' : 'border-zinc-200 text-zinc-500 hover:border-zinc-300 hover:text-zinc-700'}`}
				>{tip}</button>
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
			class={`h-8 min-w-0 flex-1 bg-transparent text-[13px] outline-none ${dark ? 'text-white placeholder:text-zinc-600' : 'text-zinc-900 placeholder:text-zinc-400'}`}
		/>
		<button
			type="button"
			onclick={() => onSend()}
			disabled={!chatInput.trim() || chatLoading}
			class={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-all disabled:opacity-20 ${dark ? 'bg-white/[0.06] text-zinc-400' : 'bg-zinc-100 text-zinc-500'}`}
			aria-label="Send message"
		>
			<Send class="h-3.5 w-3.5" />
		</button>
	</div>
</div>
