<script lang="ts">
	import { tick } from 'svelte';
	import { fly } from 'svelte/transition';
	import { ArrowLeft, ArrowUp, ExternalLink, Zap } from 'lucide-svelte';
	import { marked } from 'marked';
	import type { Article } from '$lib/api';
	import ChatDock from '$lib/components/reader/ChatDock.svelte';
	import { formatEngagement, getBrandColor } from '$lib/ui';

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

	let scrollArea = $state<HTMLDivElement | undefined>();

	$effect(() => {
		chatMessages.length;
		chatLoading;
		tick().then(() => {
			scrollArea?.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
		});
	});
</script>

<section
	class="relative flex h-full min-h-0 flex-1 flex-col bg-[#0a0a0a]"
	transition:fly={{ x: 60, duration: 300, opacity: 0 }}
>
	<!-- Header -->
	<header class="flex items-center justify-between gap-3 border-b border-white/[0.04] bg-[#0a0a0a] px-4 py-2.5 sm:px-5">
		<button
			onclick={onBack}
			class="flex items-center gap-2 rounded-md px-2 py-1.5 text-zinc-500 transition-colors hover:bg-white/5 hover:text-white"
		>
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

			<div class="hidden items-center gap-1.5 rounded-md border border-white/[0.06] px-2.5 py-1.5 sm:flex">
				<div class="h-1.5 w-1.5 rounded-full" style={`background-color: ${getBrandColor(article.source)}`}></div>
				<span class="text-[10px] font-semibold text-zinc-400">{article.source}</span>
			</div>

			{#if formatEngagement(article.likes)}
				<div class="hidden items-center gap-1 rounded-md border border-white/[0.06] px-2 py-1.5 sm:flex">
					<ArrowUp class="h-3 w-3 text-zinc-500" />
					<span class="text-[10px] font-semibold tabular-nums text-zinc-400">{formatEngagement(article.likes)}</span>
				</div>
			{/if}

			<button
				onclick={() => onOpenExternal(article.url)}
				class="flex h-8 w-8 items-center justify-center rounded-md border border-white/[0.06] text-zinc-400 transition-all hover:bg-white hover:text-black"
				aria-label="Open original article"
			>
				<ExternalLink class="h-3.5 w-3.5" />
			</button>
		</div>
	</header>

	<!-- Scrollable content -->
	<div bind:this={scrollArea} class="no-scrollbar min-h-0 flex-1 overflow-y-auto scroll-smooth">
		<div class="mx-auto w-full max-w-2xl px-5 pb-44 pt-6 sm:px-6 sm:pb-48 sm:pt-8 lg:px-8 lg:pb-52 lg:pt-10">
			<!-- Article meta -->
			<div class="mb-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
				<span>{article.category}</span>
				<span class="text-zinc-700">/</span>
				<span>{new Date(article.published_date).toLocaleDateString()}</span>
				<span class="text-zinc-700 sm:hidden">/</span>
				<span class="sm:hidden" style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			</div>

			<!-- Title -->
			<h2 class="mb-6 text-[22px] font-bold leading-tight tracking-tight text-white sm:text-[26px]">
				{article.title}
			</h2>

			<!-- Article body -->
			<div class="prose prose-invert prose-sm max-w-none text-[14px] leading-7 text-zinc-300 sm:text-[15px] sm:leading-8">
				{@html marked.parse(article.insight || article.content_snippet || '')}
			</div>

			<!-- Chat section -->
			<div class="mt-8 border-t border-white/[0.04] pt-6">
				<p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-zinc-600">
					Ask Axon
				</p>

				{#if chatMessages.length > 0}
					<div class="space-y-4">
						{#each chatMessages as msg}
							{#if msg.role === 'user'}
								<div class="flex justify-end">
									<div class="max-w-[80%] rounded-lg rounded-br-sm bg-white/[0.07] px-4 py-2.5">
										<p class="text-[13px] leading-relaxed text-zinc-200">{msg.content}</p>
									</div>
								</div>
							{:else}
								<div class="rounded-lg rounded-bl-sm border border-white/[0.04] bg-white/[0.02] px-4 py-3">
									<div class="prose prose-invert prose-sm max-w-none text-[13.5px] leading-7 text-zinc-300">
										{@html marked.parse(msg.content)}
									</div>
								</div>
							{/if}
						{/each}
					</div>
				{/if}

				{#if chatLoading}
					<div class="mt-4 flex items-center gap-2 px-1">
						<div class="flex items-center gap-1">
							<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-500"></span>
							<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-500 [animation-delay:0.15s]"></span>
							<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-500 [animation-delay:0.3s]"></span>
						</div>
						<span class="text-[11px] text-zinc-600">Analyzing...</span>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<!-- Chat dock -->
	<div class="pointer-events-none absolute inset-x-0 bottom-0 z-30 px-4 pb-3 pt-8 sm:px-6" style="background: linear-gradient(to top, #0a0a0a 60%, transparent)">
		<div class="pointer-events-auto mx-auto w-full max-w-xl">
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
