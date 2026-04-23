<script lang="ts">
	import { Send, Mic, MicOff, Loader2 } from 'lucide-svelte';
	import { onDestroy } from 'svelte';
	import { inputClass, panelClass, iconButtonClass } from '$lib/ui-styles';

	type Props = {
		chatInput: string;
		chatLoading: boolean;
		suggestions: string[];
		suggestionsLoading?: boolean;
		showSuggestions: boolean;
		theme: 'dark' | 'light';
		onInputChange: (value: string) => void;
		onSend: (message?: string) => void;
	};

	let { chatInput, chatLoading, suggestions, suggestionsLoading = false, showSuggestions, theme, onInputChange, onSend }: Props = $props();
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

<div class={`min-w-0 ${panelClass(theme)}`}>
	{#if showSuggestions}
		<div class={`no-scrollbar flex min-h-[2.75rem] items-center gap-1.5 overflow-x-auto border-b px-3 py-2 ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
			{#each suggestions as tip}
				<button
					type="button"
					onclick={() => onSend(tip)}
					disabled={suggestionsLoading}
					class={`whitespace-nowrap rounded-full border px-2.5 py-1.5 text-[11px] transition-colors disabled:opacity-50 ${dark ? 'border-white/[0.06] text-zinc-400 hover:border-white/15 hover:text-zinc-200' : 'border-zinc-200 text-zinc-500 hover:border-zinc-300 hover:text-zinc-700'}`}
				>{tip}</button>
			{/each}
			{#if suggestionsLoading}
				<Loader2 class={`h-3.5 w-3.5 shrink-0 animate-spin ${dark ? 'text-zinc-500' : 'text-zinc-400'}`} />
			{/if}
		</div>
	{/if}

	<div class="flex items-center gap-1.5 px-3 py-2">
		<input
			type="text"
			value={chatInput}
			oninput={(event) => onInputChange((event.currentTarget as HTMLInputElement).value)}
			onkeydown={(event) => event.key === 'Enter' && onSend()}
			placeholder={isListening ? 'Listening...' : 'Ask about this signal...'}
			class={`${inputClass(theme)} min-w-0 flex-1`}
		/>
		{#if speechSupported}
			<button
				type="button"
				onclick={toggleSpeech}
				class={`${iconButtonClass(theme)} border-0 ${isListening ? (dark ? 'bg-white/15 text-white hover:text-white' : 'bg-zinc-200 text-zinc-900 hover:text-zinc-900') : ''}`}
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
			class={`${iconButtonClass(theme)} border-0 disabled:opacity-20`}
			aria-label="Send message"
		>
			<Send class="h-3.5 w-3.5" />
		</button>
	</div>
</div>
