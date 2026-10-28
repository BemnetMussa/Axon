<script lang="ts">
	import { api } from '$lib/api';
	import { X } from 'lucide-svelte';
	import SignalLoader from '$lib/components/ui/SignalLoader.svelte';
	import { fade } from 'svelte/transition';

	let { show = $bindable(false), theme = 'dark' } = $props();

	let rating = $state(0);
	let comment = $state('');
	let submitting = $state(false);
	let success = $state(false);
	let error = $state<string | null>(null);

	let dark = $derived(theme === 'dark');
	let muted = $derived(dark ? 'text-white/40' : 'text-black/45');
	let rule = $derived(dark ? 'border-white/10' : 'border-black/10');

	async function handleSubmit() {
		if (rating === 0) {
			error = 'Pick a number first.';
			return;
		}
		submitting = true;
		error = null;
		try {
			await api.submitFeedback(rating, comment);
			success = true;
			setTimeout(() => {
				show = false;
				setTimeout(() => {
					success = false;
					rating = 0;
					comment = '';
				}, 300);
			}, 1600);
		} catch {
			error = 'Could not send. Try again.';
		} finally {
			submitting = false;
		}
	}

	function close() {
		if (!submitting) show = false;
	}

	function ratingClass(n: number) {
		if (rating === n) return dark ? 'border-white bg-white text-black' : 'border-black bg-black text-white';
		return dark
			? 'border-white/15 text-white/60 hover:border-white/40 hover:text-white'
			: 'border-black/15 text-black/60 hover:border-black/40 hover:text-black';
	}
</script>

{#if show}
	<div class="fixed inset-0 z-[100] flex items-center justify-center p-4" transition:fade={{ duration: 150 }}>
		<button type="button" class="absolute inset-0 cursor-default bg-black/60" onclick={close} aria-label="Close feedback"></button>

		<div
			class={`relative w-full max-w-sm border ${rule} ${dark ? 'bg-[#0a0a0a] text-[#ededed]' : 'bg-[#fafafa] text-[#0a0a0a]'}`}
			role="dialog"
			aria-modal="true"
			aria-labelledby="feedback-title"
		>
			<div class={`flex h-12 items-center justify-between border-b px-5 ${rule}`}>
				<h2 id="feedback-title" class="axon-label">Feedback</h2>
				<button type="button" onclick={close} class={`-mr-2 p-2 transition-colors ${muted} ${dark ? 'hover:text-white' : 'hover:text-black'}`} aria-label="Close feedback">
					<X class="h-4 w-4" />
				</button>
			</div>

			{#if success}
				<div class="px-5 py-10 text-center" in:fade>
					<p class="text-[15px] font-semibold">Thanks. Got it.</p>
					<p class={`mt-1.5 text-[13px] ${muted}`}>Every note gets read.</p>
				</div>
			{:else}
				<div class="space-y-5 px-5 py-5">
					<fieldset>
						<legend class={`axon-label mb-2.5 ${muted}`}>How useful is Axon? 1–5</legend>
						<div class="grid grid-cols-5 gap-1.5">
							{#each [1, 2, 3, 4, 5] as n}
								<button
									type="button"
									onclick={() => { rating = n; error = null; }}
									class={`h-10 border text-[14px] font-medium tabular-nums transition-colors ${ratingClass(n)}`}
									aria-pressed={rating === n}
									aria-label={`${n} out of 5`}
								>{n}</button>
							{/each}
						</div>
					</fieldset>

					<div>
						<label for="feedback-comment" class={`axon-label mb-2.5 block ${muted}`}>What should change?</label>
						<textarea
							id="feedback-comment"
							bind:value={comment}
							placeholder="Optional"
							class={`min-h-[110px] w-full resize-none border bg-transparent p-3 text-[14px] outline-none transition-colors ${dark ? 'border-white/15 placeholder:text-white/30 focus:border-white/40' : 'border-black/15 placeholder:text-black/30 focus:border-black/40'}`}
						></textarea>
					</div>

					{#if error}
						<p role="alert" class="text-[12px] text-red-500">{error}</p>
					{/if}

					<button
						type="button"
						onclick={handleSubmit}
						disabled={submitting}
						class={`axon-label inline-flex h-11 w-full items-center justify-center gap-2 transition-opacity disabled:opacity-50 ${dark ? 'bg-white text-black hover:opacity-90' : 'bg-black text-white hover:opacity-90'}`}
					>
						{#if submitting}
							<SignalLoader size={14} />
							Sending
						{:else}
							Send
						{/if}
					</button>
				</div>
			{/if}
		</div>
	</div>
{/if}
