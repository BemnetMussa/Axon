<script lang="ts">
	import { Send, Mic, MicOff } from 'lucide-svelte';
	import { onDestroy } from 'svelte';

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

	let isListening = $state(false);
	let recognition: any = null;
	let speechSupported = $state(false);

	if (typeof window !== 'undefined') {
		const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
		if (SR) {
			speechSupported = true;
			recognition = new SR();
			recognition.continuous = false;
			recognition.interimResults = true;
			recognition.lang = 'en-US';

			recognition.onresult = (event: any) => {
				let transcript = '';
				for (let i = 0; i < event.results.length; i++) {
					transcript += event.results[i][0].transcript;
				}
				onInputChange(transcript);
			};

			recognition.onend = () => { isListening = false; };
			recognition.onerror = () => { isListening = false; };
		}
	}

	function toggleSpeech() {
		if (!recognition) return;
		if (isListening) {
			recognition.stop();
			isListening = false;
		} else {
			recognition.start();
			isListening = true;
		}
	}

	onDestroy(() => {
		if (recognition && isListening) recognition.stop();
	});
</script>

<div class={`min-w-0 rounded-xl border shadow-lg backdrop-blur-2xl ${dark ? 'border-white/[0.08] bg-[#111]/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)]' : 'border-zinc-200 bg-white/95 shadow-[0_4px_24px_rgba(0,0,0,0.08)]'}`}>
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

	<div class="flex items-center gap-1.5 px-3 py-2">
		<input
			type="text"
			value={chatInput}
			oninput={(event) => onInputChange((event.currentTarget as HTMLInputElement).value)}
			onkeydown={(event) => event.key === 'Enter' && onSend()}
			placeholder={isListening ? 'Listening...' : 'Ask about this signal...'}
			class={`h-8 min-w-0 flex-1 bg-transparent text-[13px] outline-none ${dark ? 'text-white placeholder:text-zinc-600' : 'text-zinc-900 placeholder:text-zinc-400'}`}
		/>
		{#if speechSupported}
			<button
				type="button"
				onclick={toggleSpeech}
				class={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-all ${isListening ? (dark ? 'bg-white/15 text-white' : 'bg-zinc-200 text-zinc-900') : (dark ? 'bg-white/[0.06] text-zinc-500 hover:text-zinc-300' : 'bg-zinc-100 text-zinc-400 hover:text-zinc-600')}`}
				aria-label={isListening ? 'Stop listening' : 'Voice input'}
			>
				{#if isListening}
					<MicOff class="h-3.5 w-3.5" />
				{:else}
					<Mic class="h-3.5 w-3.5" />
				{/if}
			</button>
		{/if}
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
