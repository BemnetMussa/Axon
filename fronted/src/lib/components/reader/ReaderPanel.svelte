<script lang="ts">
	import { tick } from 'svelte';
	import { fly } from 'svelte/transition';
	import { ArrowLeft, ArrowUpRight, ExternalLink, Share2, Bookmark, Check } from 'lucide-svelte';
	import { renderMarkdown } from '$lib/markdown';
	import type { Article } from '$lib/api';
	import ChatDock from '$lib/components/reader/ChatDock.svelte';
	import { categoryLabel, formatDate, getBrandColor, hostname, whyKept } from '$lib/ui';
	import { iconButtonClass } from '$lib/ui-styles';

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
		suggestionsLoading?: boolean;
		theme: 'dark' | 'light';
		suggestions: string[];
		onBack: () => void;
		onToggleSave: (id: number) => void;
		onOpenExternal: (url: string) => void;
		onChatInputChange: (value: string) => void;
		onSendChat: (message?: string) => void;
	};

	let {
		article, isSaved, chatMessages, chatInput, chatLoading, suggestionsLoading = false, theme, suggestions,
		onBack, onToggleSave, onOpenExternal, onChatInputChange, onSendChat
	}: Props = $props();

	let scrollArea = $state<HTMLDivElement | undefined>();
	let shareSuccess = $state(false);
	let dark = $derived(theme === 'dark');
	let why = $derived(whyKept(article));
	let host = $derived(hostname(article.url));
	let isBrief = $derived(Boolean(article.insight));

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
	class={`relative flex h-full min-h-0 w-full min-w-0 flex-1 flex-col overflow-x-hidden ${dark ? 'bg-[#0a0a0a]' : 'bg-white'}`}
	transition:fly={{ x: 60, duration: 300, opacity: 0 }}
>
	<header class={`flex items-center justify-between gap-2 border-b px-3 py-2.5 sm:gap-3 sm:px-5 ${dark ? 'border-white/10 bg-[#0a0a0a]' : 'border-black/10 bg-white'}`}>
		<button
			onclick={onBack}
			class={`flex shrink-0 items-center gap-1.5 rounded-md px-1.5 py-1.5 transition-colors sm:gap-2 sm:px-2 ${dark ? 'text-zinc-500 hover:text-white' : 'text-zinc-400 hover:text-black'}`}
		>
			<ArrowLeft class="h-4 w-4" />
			<span class="text-[11px] font-semibold hidden sm:inline">Back</span>
		</button>

		<div class="flex items-center gap-1.5 sm:gap-2">
			<button
				onclick={() => onToggleSave(article.id)}
				class={`${iconButtonClass(theme)} sm:w-auto sm:gap-1.5 sm:px-2.5`}
				aria-label={isSaved ? 'Unsave' : 'Save'}
			>
				<Bookmark class={`h-3.5 w-3.5 ${savedStyle()}`} />
				<span class={`hidden text-[10px] font-semibold sm:inline ${savedLabel()}`}>
					{isSaved ? 'Saved' : 'Save'}
				</span>
			</button>

			<button
				onclick={shareArticle}
				class={`${iconButtonClass(theme, 'muted')} ${dark ? 'hover:bg-white hover:text-black' : 'hover:bg-black hover:text-white'}`}
				aria-label="Share article"
			>
				{#if shareSuccess}
					<Check class="h-3.5 w-3.5 text-emerald-500" />
				{:else}
					<Share2 class="h-3.5 w-3.5" />
				{/if}
			</button>

			<button
				onclick={() => onOpenExternal(article.url)}
				class={`${iconButtonClass(theme, 'muted')} !hidden sm:!flex sm:w-auto sm:gap-1.5 sm:px-3 ${dark ? 'hover:border-white/30 hover:text-white' : 'hover:border-black/30 hover:text-black'}`}
				aria-label="Open original article"
			>
				<ExternalLink class="h-3.5 w-3.5" />
				<span class="hidden text-[10px] font-semibold sm:inline">Original</span>
			</button>
		</div>
	</header>

	<div bind:this={scrollArea} class="no-scrollbar min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto scroll-smooth">
		<div class="mx-auto w-full min-w-0 max-w-[720px] px-5 pb-8 pt-7 sm:px-9 sm:pb-10 sm:pt-11 lg:px-12 lg:pt-14" style="overflow-wrap: anywhere;">
			<div class={`mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[10px] font-medium uppercase tracking-[0.14em] ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
				<button type="button" onclick={() => onOpenExternal(article.url)} class="uppercase underline-offset-2 hover:underline" style={`color: ${getBrandColor(article.source)}`} title={host ? `Open on ${host}` : 'Open the original'}>{article.source}</button>
				<span class={dark ? 'text-zinc-700' : 'text-zinc-300'}>/</span>
				<span>{categoryLabel(article.category)}</span>
				<span class={dark ? 'text-zinc-700' : 'text-zinc-300'}>/</span>
				<span>{formatDate(article.published_date)}</span>
			</div>

			<h2 class={`axon-editorial-title mb-5 text-[29px] font-bold leading-[1.08] sm:text-[38px] lg:text-[42px] ${dark ? 'text-white' : 'text-zinc-950'}`}>{article.title}</h2>

			<div class={`mb-8 flex flex-wrap items-center gap-x-3 gap-y-1 border-y py-3 text-[12px] ${dark ? 'border-white/10 text-zinc-500' : 'border-black/10 text-zinc-500'}`}>
				{#if why}
					<span>Made the cut: <span class={`font-medium ${dark ? 'text-zinc-200' : 'text-zinc-800'}`}>{why}</span></span>
				{/if}
				<span class="sm:ml-auto">{isBrief ? 'Axon brief · AI summary of the original' : 'Excerpt from the source'}</span>
			</div>

			<div class={`axon-reader-body prose max-w-none text-[16px] leading-[1.7] sm:text-[17px] sm:leading-[1.75] prose-headings:tracking-tight ${dark ? 'prose-invert text-zinc-300 prose-strong:text-white' : 'text-zinc-700 prose-strong:text-zinc-950'}`}>
				{@html renderMarkdown(article.insight || article.content_snippet)}
			</div>

			<button
				type="button"
				onclick={() => onOpenExternal(article.url)}
				class={`group mt-8 flex w-full items-center justify-between gap-4 rounded-xl border px-4 py-3.5 text-left transition-colors ${dark ? 'border-white/10 hover:border-white/25 hover:bg-white/[0.03]' : 'border-black/10 hover:border-black/25 hover:bg-black/[0.02]'}`}
			>
				<span class="min-w-0">
					<span class={`block text-[14px] font-semibold ${dark ? 'text-white' : 'text-black'}`}>Read the original</span>
					{#if host}<span class={`block truncate text-[12px] ${dark ? 'text-zinc-500' : 'text-zinc-500'}`}>{host}</span>{/if}
				</span>
				<ArrowUpRight class={`h-4 w-4 shrink-0 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5 ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} />
			</button>

			{#if chatMessages.length > 0 || chatLoading}
			<div class={`mt-10 border-t pt-8 ${dark ? 'border-white/10' : 'border-black/10'}`}>
				{#if chatMessages.length > 0}
					<div class="min-w-0 max-w-full space-y-4">
						{#each chatMessages as msg}
							{#if msg.role === 'user'}
								<div class="flex min-w-0 justify-end">
									<div class={`min-w-0 max-w-[85%] rounded-lg rounded-br-sm px-4 py-2.5 ${dark ? 'bg-white/[0.07]' : 'bg-zinc-100'}`} style="overflow-wrap: anywhere;">
										<p class={`break-words text-[13px] leading-relaxed ${dark ? 'text-zinc-200' : 'text-zinc-800'}`}>{msg.content}</p>
									</div>
								</div>
							{:else}
								<div class="min-w-0 max-w-full overflow-hidden px-1">
									{#if dark}
										<div class="prose prose-invert prose-sm max-w-full overflow-hidden break-words text-[14px] leading-6 text-zinc-300 prose-p:break-words prose-pre:max-w-full prose-pre:overflow-x-auto prose-li:break-words">
											{@html renderMarkdown(msg.content)}
										</div>
									{:else}
										<div class="prose prose-sm max-w-full overflow-hidden break-words text-[14px] leading-6 text-zinc-700 prose-p:break-words prose-pre:max-w-full prose-pre:overflow-x-auto prose-li:break-words">
											{@html renderMarkdown(msg.content)}
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
						<span class={`text-[11px] ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>Reading this article...</span>
					</div>
				{/if}
			</div>
			{/if}
		</div>
	</div>

	<div
		class={`shrink-0 border-t px-3 pb-[calc(env(safe-area-inset-bottom,0px)+0.5rem)] pt-2 sm:px-6 ${dark ? 'border-white/[0.04] bg-[#0a0a0a]' : 'border-zinc-100 bg-white'}`}
	>
		<div class="mx-auto w-full min-w-0 max-w-xl">
			<ChatDock
				{chatInput}
				{chatLoading}
				{suggestions}
				{suggestionsLoading}
				{theme}
				showSuggestions={chatMessages.length === 0}
				onInputChange={onChatInputChange}
				onSend={onSendChat}
			/>
		</div>
	</div>
</section>
