<script lang="ts">
	import { renderMarkdown } from '$lib/markdown';
	import SignalLoader from '$lib/components/ui/SignalLoader.svelte';

	type Props = {
		digest: { content: string; created_at: string } | null;
		loading: boolean;
		theme: 'dark' | 'light';
		onBack: () => void;
		onGenerate: () => void;
	};

	let { digest, loading, theme, onBack, onGenerate }: Props = $props();
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
			<h1 class={`mb-2 text-2xl font-bold sm:text-4xl ${theme === 'dark' ? 'text-white' : 'text-black'}`}>Weekly Digest</h1>
			<p class={`mb-10 text-[12px] sm:text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
				Synthesized {digest.created_at ? new Date(digest.created_at).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : 'recently'}
			</p>

			<div class={`prose max-w-none text-[14px] leading-[1.8] sm:text-[16px] ${theme === 'dark' ? 'prose-invert prose-p:text-[#d4d4d8] prose-headings:text-white' : 'prose-p:text-zinc-700 prose-headings:text-black'}`}>
				{@html renderMarkdown(digest.content)}
			</div>

			<div class={`mt-10 flex items-center gap-3 border-t pt-6 ${theme === 'dark' ? 'border-white/[0.06]' : 'border-zinc-100'}`}>
				<button
					onclick={onGenerate}
					disabled={loading}
					class={`inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-[13px] font-bold shadow-md transition-all disabled:opacity-60 ${theme === 'dark' ? 'bg-white text-black hover:bg-zinc-200' : 'bg-zinc-900 text-white hover:bg-zinc-700'}`}
				>
					{#if loading}
						<SignalLoader size={14} />
						Generating…
					{:else if digest.content.includes('No weekly digest available')}
						Generate first digest
					{:else}
						Regenerate digest
					{/if}
				</button>
				<span class={`text-[11px] ${theme === 'dark' ? 'text-zinc-600' : 'text-zinc-400'}`}>Takes ~10 seconds</span>
			</div>
		{/if}
	</div>
</div>
