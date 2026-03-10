<script lang="ts">
	import { tick } from 'svelte';
	import { fly } from 'svelte/transition';
	import { ArrowLeft, ArrowUp, ExternalLink, Share2, Zap, Check } from 'lucide-svelte';
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
		theme: 'dark' | 'light';
		suggestions: string[];
		onBack: () => void;
		onToggleSave: (id: number) => void;
		onOpenExternal: (url: string) => void;
		onChatInputChange: (value: string) => void;
		onSendChat: (message?: string) => void;
	};

	let {
		article, isSaved, chatMessages, chatInput, chatLoading, theme, suggestions,
		onBack, onToggleSave, onOpenExternal, onChatInputChange, onSendChat
	}: Props = $props();

	let scrollArea = $state<HTMLDivElement | undefined>();
	let shareSuccess = $state(false);
	let dark = $derived(theme === 'dark');

	$effect(() => {
		chatMessages.length;
		chatLoading;
		tick().then(() => {
			scrollArea?.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
		});
	});

	async function shareArticle() {
		const shareData = { title: article.title, url: article.url };
		try {
			if (navigator.share) {
				await navigator.share(shareData);
			} else {
				await navigator.clipboard.writeText(`${article.title}\n${article.url}`);
				shareSuccess = true;
				setTimeout(() => (shareSuccess = false), 2000);
			}
		} catch {
			try {
				await navigator.clipboard.writeText(`${article.title}\n${article.url}`);
				shareSuccess = true;
				setTimeout(() => (shareSuccess = false), 2000);
			} catch { /* silently fail */ }
		}
	}

	function savedStyle() {
		if (isSaved) return dark ? 'fill-white text-white' : 'fill-black text-black';
		return dark ? 'text-zinc-500' : 'text-zinc-400';
	}

	function savedLabel() {
		if (isSaved) return dark ? 'text-white' : 'text-black';
		return dark ? 'text-zinc-500' : 'text-zinc-400';
	}
</script>

<section
	class={`relative flex h-full min-h-0 flex-1 flex-col ${dark ? 'bg-[#0a0a0a]' : 'bg-white'}`}
	transition:fly={{ x: 60, duration: 300, opacity: 0 }}
>
	<header class={`flex items-center justify-between gap-3 border-b px-4 py-2.5 sm:px-5 ${dark ? 'border-white/[0.04] bg-[#0a0a0a]' : 'border-zinc-100 bg-white'}`}>
		<button
			onclick={onBack}
			class={`flex items-center gap-2 rounded-md px-2 py-1.5 transition-colors ${dark ? 'text-zinc-500 hover:text-white' : 'text-zinc-400 hover:text-black'}`}
		>
			<ArrowLeft class="h-4 w-4" />
			<span class="text-[11px] font-semibold">Back</span>
		</button>

		<div class="flex items-center gap-2">
			<button
				onclick={() => onToggleSave(article.id)}
				class={`flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 transition-colors ${dark ? 'border-white/[0.06] hover:bg-white/5' : 'border-zinc-200 hover:bg-zinc-50'}`}
			>
				<Zap class={`h-3 w-3 ${savedStyle()}`} />
				<span class={`text-[10px] font-semibold ${savedLabel()}`}>
					{isSaved ? 'Saved' : 'Save'}
				</span>
			</button>

			<button
				onclick={shareArticle}
				class={`flex h-8 w-8 items-center justify-center rounded-md border transition-all ${dark ? 'border-white/[0.06] text-zinc-400 hover:bg-white hover:text-black' : 'border-zinc-200 text-zinc-500 hover:bg-black hover:text-white'}`}
				aria-label="Share article"
			>
				{#if shareSuccess}
					<Check class="h-3.5 w-3.5 text-emerald-500" />
				{:else}
					<Share2 class="h-3.5 w-3.5" />
				{/if}
			</button>

			<div class={`hidden items-center gap-1.5 rounded-md border px-2.5 py-1.5 sm:flex ${dark ? 'border-white/[0.06]' : 'border-zinc-200'}`}>
				<div class="h-1.5 w-1.5 rounded-full" style={`background-color: ${getBrandColor(article.source)}`}></div>
				<span class={`text-[10px] font-semibold ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>{article.source}</span>
			</div>

			{#if formatEngagement(article.likes)}
				<div class={`hidden items-center gap-1 rounded-md border px-2 py-1.5 sm:flex ${dark ? 'border-white/[0.06]' : 'border-zinc-200'}`}>
					<ArrowUp class={`h-3 w-3 ${dark ? 'text-zinc-500' : 'text-zinc-400'}`} />
					<span class={`text-[10px] font-semibold tabular-nums ${dark ? 'text-zinc-400' : 'text-zinc-500'}`}>{formatEngagement(article.likes)}</span>
				</div>
			{/if}

			<button
				onclick={() => onOpenExternal(article.url)}
				class={`flex h-8 w-8 items-center justify-center rounded-md border transition-all ${dark ? 'border-white/[0.06] text-zinc-400 hover:bg-white hover:text-black' : 'border-zinc-200 text-zinc-500 hover:bg-black hover:text-white'}`}
				aria-label="Open original article"
			>
				<ExternalLink class="h-3.5 w-3.5" />
			</button>
		</div>
	</header>

	<div bind:this={scrollArea} class="no-scrollbar min-h-0 flex-1 overflow-y-auto scroll-smooth">
		<div class="mx-auto w-full max-w-2xl px-4 pb-48 pt-5 sm:px-6 sm:pb-52 sm:pt-8 lg:px-8 lg:pb-52 lg:pt-10">
			<div class={`mb-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-[10px] font-semibold uppercase tracking-wider ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
				<span>{article.category}</span>
				<span class={dark ? 'text-zinc-700' : 'text-zinc-300'}>/</span>
				<span>{new Date(article.published_date).toLocaleDateString()}</span>
				<span class={`sm:hidden ${dark ? 'text-zinc-700' : 'text-zinc-300'}`}>/</span>
				<span class="sm:hidden" style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			</div>

			<h2 class={`mb-6 text-[22px] font-bold leading-tight tracking-tight sm:text-[26px] ${dark ? 'text-white' : 'text-zinc-900'}`}>{article.title}</h2>

			{#if dark}
				<div class="prose prose-invert prose-sm max-w-none text-[14px] leading-7 text-zinc-300 sm:text-[15px] sm:leading-8">
					{@html marked.parse(article.insight || article.content_snippet || '')}
				</div>
			{:else}
				<div class="prose prose-sm max-w-none text-[14px] leading-7 text-zinc-700 sm:text-[15px] sm:leading-8">
					{@html marked.parse(article.insight || article.content_snippet || '')}
				</div>
			{/if}

			<div class={`mt-8 border-t pt-6 ${dark ? 'border-white/[0.04]' : 'border-zinc-100'}`}>
				<p class={`mb-4 text-[10px] font-bold uppercase tracking-widest ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Ask Axon</p>

				{#if chatMessages.length > 0}
					<div class="space-y-4">
						{#each chatMessages as msg}
							{#if msg.role === 'user'}
								<div class="flex justify-end">
									<div class={`max-w-[80%] rounded-lg rounded-br-sm px-4 py-2.5 ${dark ? 'bg-white/[0.07]' : 'bg-zinc-100'}`}>
										<p class={`text-[13px] leading-relaxed ${dark ? 'text-zinc-200' : 'text-zinc-800'}`}>{msg.content}</p>
									</div>
								</div>
							{:else}
								<div class={`rounded-lg rounded-bl-sm border px-4 py-3 ${dark ? 'border-white/[0.04] bg-white/[0.02]' : 'border-zinc-100 bg-zinc-50'}`}>
									{#if dark}
										<div class="prose prose-invert prose-sm max-w-none text-[13.5px] leading-7 text-zinc-300">
											{@html marked.parse(msg.content)}
										</div>
									{:else}
										<div class="prose prose-sm max-w-none text-[13.5px] leading-7 text-zinc-700">
											{@html marked.parse(msg.content)}
										</div>
									{/if}
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
						<span class={`text-[11px] ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Analyzing...</span>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div
		class="pointer-events-none absolute inset-x-0 bottom-0 z-30 px-3 pb-[calc(env(safe-area-inset-bottom,0px)+0.75rem)] pt-8 sm:px-6"
		style={dark ? 'background: linear-gradient(to top, #0a0a0a 60%, transparent)' : 'background: linear-gradient(to top, #ffffff 60%, transparent)'}
	>
		<div class="pointer-events-auto mx-auto w-full max-w-xl">
			<ChatDock
				{chatInput}
				{chatLoading}
				{suggestions}
				{theme}
				showSuggestions={chatMessages.length === 0}
				onInputChange={onChatInputChange}
				onSend={onSendChat}
			/>
		</div>
	</div>
</section>
