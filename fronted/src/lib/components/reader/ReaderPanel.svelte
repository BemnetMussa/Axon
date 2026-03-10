<script lang="ts">
	import { tick } from 'svelte';
	import { fly } from 'svelte/transition';
	import { ArrowLeft, ExternalLink, Zap } from 'lucide-svelte';
	import { marked } from 'marked';
	import type { Article } from '$lib/api';
	import ChatDock from '$lib/components/reader/ChatDock.svelte';
	import { getBrandColor } from '$lib/ui';

	type ChatMessage = {
		role: 'user' | 'ai';
		content: string;
	};

	type Props = {
		article: Article;
		isSaved: boolean;
		chatMessages: ChatMessage[];
		chatInput: string;
		chatLoading: boolean;
		suggestions: string[];
		onBack: () => void;
		onToggleSave: (id: number) => void;
		onOpenExternal: (url: string) => void;
		onChatInputChange: (value: string) => void;
		onSendChat: (message?: string) => void;
	};

	let {
		article,
		isSaved,
		chatMessages,
		chatInput,
		chatLoading,
		suggestions,
		onBack,
		onToggleSave,
		onOpenExternal,
		onChatInputChange,
		onSendChat
	}: Props = $props();

	let readerScrollArea = $state<HTMLDivElement | undefined>();

	$effect(() => {
		chatMessages.length;
		chatLoading;
		tick().then(() => {
			readerScrollArea?.scrollTo({ top: readerScrollArea.scrollHeight, behavior: 'smooth' });
		});
	});
</script>

<section class="relative flex h-full min-h-0 flex-1 flex-col bg-[#0a0a0a]" transition:fly={{ x: 80, duration: 350, opacity: 0 }}>
	<header class="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-white/[0.04] bg-[#0a0a0a]/90 px-4 py-2.5 backdrop-blur-md sm:px-5">
		<button onclick={onBack} class="flex items-center gap-2 rounded-md px-2 py-1.5 text-zinc-500 transition-colors hover:bg-white/5 hover:text-white">
			<ArrowLeft class="h-4 w-4" />
			<span class="text-[11px] font-semibold">Back</span>
		</button>

		<div class="flex items-center gap-2">
			<button
				onclick={() => onToggleSave(article.id)}
				class="flex items-center gap-1.5 rounded-md border border-white/[0.06] px-2.5 py-1.5 transition-colors hover:bg-white/5"
			>
				<Zap class={`h-3 w-3 ${isSaved ? 'fill-white text-white' : 'text-zinc-500'}`} />
				<span class={`text-[10px] font-semibold ${isSaved ? 'text-white' : 'text-zinc-500'}`}>
					{isSaved ? 'Saved' : 'Save'}
				</span>
			</button>

			<div class="flex items-center gap-1.5 rounded-md border border-white/[0.06] px-2.5 py-1.5">
				<div class="h-1.5 w-1.5 rounded-full" style={`background-color: ${getBrandColor(article.source)}`}></div>
				<span class="text-[10px] font-semibold text-zinc-400">{article.source}</span>
			</div>

			<button
				onclick={() => onOpenExternal(article.url)}
				class="flex h-8 w-8 items-center justify-center rounded-md border border-white/[0.06] text-zinc-400 transition-all hover:bg-white hover:text-black"
				aria-label="Open original article"
			>
				<ExternalLink class="h-3.5 w-3.5" />
			</button>
		</div>
	</header>

	<div bind:this={readerScrollArea} class="no-scrollbar min-h-0 flex-1 overflow-y-auto scroll-smooth">
		<div class="mx-auto w-full max-w-2xl px-5 py-6 pb-48 sm:px-6 sm:py-8 sm:pb-52 lg:px-8 lg:py-10 lg:pb-56">
			<div class="mb-4 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
				<span>{article.category}</span>
				<span class="text-zinc-700">/</span>
				<span>{new Date(article.published_date).toLocaleDateString()}</span>
			</div>

			<h2 class="mb-6 text-[22px] font-bold leading-tight tracking-tight text-white sm:text-[26px]">
				{article.title}
			</h2>

			<div class="prose prose-invert prose-sm max-w-none text-[14px] leading-7 text-zinc-300 sm:text-[15px] sm:leading-8">
				{@html marked.parse(article.insight || article.content_snippet || '')}
			</div>

			<div class="mt-10 space-y-6">
				{#if chatMessages.length > 0}
					<div class="space-y-4">
						{#each chatMessages as msg}
							<div class={msg.role === 'user' ? 'flex justify-end' : 'block'}>
								{#if msg.role === 'user'}
									<div class="max-w-[85%] rounded-xl bg-white/[0.06] px-4 py-3 text-[13px] leading-relaxed text-zinc-200">
										<div class="prose prose-invert prose-sm max-w-none">
											{@html marked.parse(msg.content)}
										</div>
									</div>
								{:else}
									<div class="text-[14px] leading-7 text-zinc-300">
										<div class="prose prose-invert prose-sm max-w-none">
											{@html marked.parse(msg.content)}
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-[12px] text-zinc-600">
						Ask Axon about this signal below.
					</p>
				{/if}

				{#if chatLoading}
					<div class="flex items-center gap-1.5">
						<span class="h-1 w-1 animate-bounce rounded-full bg-zinc-600"></span>
						<span class="h-1 w-1 animate-bounce rounded-full bg-zinc-600 [animation-delay:0.15s]"></span>
						<span class="h-1 w-1 animate-bounce rounded-full bg-zinc-600 [animation-delay:0.3s]"></span>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="pointer-events-none absolute inset-x-0 bottom-3 z-30 flex justify-center px-4 sm:px-6">
		<div class="pointer-events-auto w-full max-w-xl">
			<ChatDock
				{chatInput}
				{chatLoading}
				{suggestions}
				showSuggestions={chatMessages.length === 0}
				onInputChange={onChatInputChange}
				onSend={onSendChat}
			/>
		</div>
	</div>
</section>
