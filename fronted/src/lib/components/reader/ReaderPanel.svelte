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

<section class="relative flex h-full min-h-0 flex-1 flex-col bg-[#0a0a0a] lg:border-l lg:border-white/5 lg:shadow-[20px_0_60px_rgba(0,0,0,0.5)]" transition:fly={{ x: 100, duration: 500, opacity: 0 }}>
	<header class="sticky top-0 z-20 flex min-h-16 items-center justify-between gap-3 border-b border-white/5 bg-[#0a0a0a]/90 px-4 py-3 backdrop-blur-md sm:px-6 lg:px-6">
		<button onclick={onBack} class="flex min-h-11 items-center gap-2 rounded-2xl px-2 text-zinc-500 transition-colors hover:text-white">
			<ArrowLeft class="h-4 w-4" />
			<span class="text-[10px] font-bold uppercase tracking-[1.8px] sm:text-[11px] sm:tracking-widest">Back to Feed</span>
		</button>

		<div class="flex items-center gap-2 sm:gap-3">
			<button
				onclick={() => onToggleSave(article.id)}
				class="flex min-h-11 items-center gap-2 rounded-full border border-white/8 px-3 py-2 transition-colors hover:bg-white/4"
			>
				<Zap class={`h-3.5 w-3.5 ${isSaved ? 'fill-white text-white' : 'text-zinc-500'}`} />
				<span class={`hidden text-[10px] font-bold uppercase tracking-[1.8px] sm:inline ${isSaved ? 'text-white' : 'text-zinc-500'}`}>
					{isSaved ? 'Saved' : 'Save'}
				</span>
			</button>

			<div class="hidden items-center gap-2 rounded-full border border-white/8 bg-white/2 px-3 py-2 sm:flex">
				<div class="h-1.5 w-1.5 rounded-full" style={`background-color: ${getBrandColor(article.source)}`}></div>
				<span class="text-[10px] font-bold uppercase tracking-[1.8px] text-zinc-400">{article.source}</span>
			</div>

			<button
				onclick={() => onOpenExternal(article.url)}
				class="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 transition-all hover:bg-white hover:text-black"
				aria-label="Open original article"
			>
				<ExternalLink class="h-4 w-4" />
			</button>
		</div>
	</header>

	<div bind:this={readerScrollArea} class="no-scrollbar min-h-0 flex-1 overflow-y-auto scroll-smooth">
		<div class="mx-auto w-full max-w-2xl px-5 py-8 pb-52 sm:px-6 sm:py-10 sm:pb-56 lg:px-8 lg:py-16 lg:pb-60 xl:px-10">
			<div class="mb-5 flex flex-wrap items-center gap-2 text-[10px] font-black uppercase tracking-[1.8px] text-zinc-600 sm:mb-6 sm:tracking-[2px]">
				<span>{article.category}</span>
				<span>·</span>
				<span>{new Date(article.published_date).toLocaleDateString()}</span>
				<span class="sm:hidden">·</span>
				<span class="sm:hidden" style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			</div>

			<h2 class="mb-8 text-[26px] font-bold leading-[1.08] tracking-tight text-white sm:mb-10 sm:text-[32px]">
				{article.title}
			</h2>

			<div class="prose prose-invert prose-sm max-w-none space-y-4 text-[15px] font-medium leading-8 text-zinc-300 sm:text-[15.5px]">
				{@html marked.parse(article.insight || article.content_snippet || '')}
			</div>

			<div class="mt-12 space-y-8">
				{#if chatMessages.length > 0}
					<div class="space-y-6">
						{#each chatMessages as msg}
							<div class={msg.role === 'user' ? 'flex justify-end' : 'block'}>
								{#if msg.role === 'user'}
									<div class="max-w-[85%] rounded-[1.6rem] border border-sky-200/12 bg-sky-200/8 px-5 py-4 text-[14px] leading-7 text-sky-50 shadow-[0_16px_40px_rgba(90,160,255,0.08)] backdrop-blur-md">
										<div class="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-black/40">
											{@html marked.parse(msg.content)}
										</div>
									</div>
								{:else}
									<div class="max-w-none text-[15px] leading-8 text-zinc-200">
										<div class="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-black/40 prose-headings:text-white prose-strong:text-white">
											{@html marked.parse(msg.content)}
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{:else}
					<div class="text-[13px] leading-7 text-zinc-500">
						Ask Axon directly from the field below while you read.
					</div>
				{/if}

				{#if chatLoading}
					<div class="flex items-center gap-2 text-zinc-500">
						<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-700"></span>
						<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-700 [animation-delay:0.2s]"></span>
						<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-700 [animation-delay:0.4s]"></span>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="pointer-events-none absolute inset-x-0 bottom-4 z-30 flex justify-center px-4 sm:px-6 lg:px-8">
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