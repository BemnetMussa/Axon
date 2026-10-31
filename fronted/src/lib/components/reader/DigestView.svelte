<script lang="ts">
	import { renderMarkdown } from '$lib/markdown';
	import SignalLoader from '$lib/components/ui/SignalLoader.svelte';
	import { formatDateLong } from '$lib/ui';

	type Props = {
		digest: { content: string; created_at: string } | null;
		loading: boolean;
		theme: 'dark' | 'light';
		onBack: () => void;
	};

	let { digest, loading, theme, onBack }: Props = $props();
</script>

<div class="flex h-full w-full flex-col overflow-y-auto pb-24 lg:pb-0">
	<!-- sticky back header on mobile -->
	<div class={`sticky top-0 z-10 flex items-center gap-3 border-b px-4 py-3 sm:px-6 ${theme === 'dark' ? 'border-white/[0.05] bg-[#0a0a0a]' : 'border-zinc-100 bg-white'}`}>
		<button
			onclick={onBack}
			class={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border transition-all sm:h-8 sm:w-8 sm:rounded-md ${theme === 'dark' ? 'border-white/[0.06] text-zinc-400 hover:bg-white/[0.06] hover:text-zinc-200' : 'border-zinc-200 text-zinc-500 hover:bg-zinc-50 hover:text-zinc-700'}`}
			aria-label="Back to feed"
		>
			←
		</button>
		<span class={`text-[13px] font-semibold ${theme === 'dark' ? 'text-zinc-300' : 'text-zinc-700'}`}>Weekly Digest</span>
	</div>

	<div class="mx-auto w-full max-w-3xl px-5 pt-8 pb-12 sm:px-10 sm:pt-12">
		{#if loading && !digest}
			<div class="flex flex-col items-center justify-center py-24 gap-3">
				<SignalLoader size={22} class={theme === 'dark' ? 'text-zinc-400' : 'text-zinc-500'} />
				<p class={`text-[12px] font-semibold ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>Loading digest…</p>
			</div>
		{:else if digest}
			<p class={`mb-8 text-[12px] sm:text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
				{digest.created_at ? formatDateLong(digest.created_at) : 'Recent'}
			</p>

			<div class={`prose max-w-none text-[15px] leading-[1.7] sm:text-[16px] ${theme === 'dark' ? 'prose-invert prose-p:text-[#d4d4d8] prose-headings:text-white' : 'prose-p:text-zinc-700 prose-headings:text-black'}`}>
				{@html renderMarkdown(digest.content)}
			</div>
		{/if}
	</div>
</div>
