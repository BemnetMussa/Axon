<script lang="ts">
	import { ArrowUp, Zap, Sparkles } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import { getBrandColor, formatEngagement, relativeTime, stripHtml, readingTime } from '$lib/ui';
	import { analytics } from '$lib/analytics';

	type Props = {
		article: Article;
		selected: boolean;
		isSaved: boolean;
		isNew?: boolean;
		isRead?: boolean;
		theme: 'dark' | 'light';
		onOpen: (article: Article) => void;
		onOpenWithChat: (article: Article, starterQuestion: string) => void;
		onToggleSave: (id: number) => void;
	};

	let { article, selected, isSaved, isNew = false, isRead = false, theme, onOpen, onOpenWithChat, onToggleSave }: Props = $props();
	let dark = $derived(theme === 'dark');

	// A quick, punchy starter question for the card teaser
	const TEASER_QUESTION = 'What can I build or do with this?';

	function cardClass() {
		if (selected && dark) return 'border-white/20 bg-white/[0.06]';
		if (selected && !dark) return 'border-zinc-300 bg-white shadow-[0_4px_20px_rgba(15,23,42,0.08)]';
		if (isNew && dark) return 'border-white/[0.14] bg-white/[0.045]';
		if (isNew && !dark) return 'border-zinc-200 bg-white';
		if (isRead) return dark ? 'border-transparent opacity-60 hover:opacity-90 hover:bg-white/[0.025]' : 'border-transparent opacity-60 hover:opacity-90 hover:bg-zinc-50';
		if (dark) return 'border-white/[0.07] bg-white/[0.02] hover:border-white/[0.14] hover:bg-white/[0.035]';
		return 'border-zinc-200/70 bg-white hover:border-zinc-300 hover:bg-zinc-50/60';
	}

	function handleOpen() {
		analytics.articleOpened(article.id, article.source, article.category);
		onOpen(article);
	}

	function handleChatTeaser(e: MouseEvent) {
		e.stopPropagation();
		analytics.chatStarted(article.id, 'card_teaser');
		onOpenWithChat(article, TEASER_QUESTION);
	}

	function handleSave(e: MouseEvent) {
		e.stopPropagation();
		analytics.articleSaved(article.id, !isSaved);
		onToggleSave(article.id);
	}
</script>

<article class={`group relative w-full min-w-0 max-w-full overflow-hidden rounded-2xl border px-4 py-4 transition duration-300 active:scale-[0.99] sm:px-5 sm:py-5 ${cardClass()}`}>
	<!-- Full-card open button (behind everything) -->
	<button type="button" onclick={handleOpen} class="absolute inset-0 rounded-xl" aria-label={`Open ${article.title}`}></button>

	<!-- Source / category / signal meta row -->
	<div class="flex min-w-0 items-center justify-between gap-3">
		<div class={`flex min-w-0 flex-1 items-center gap-2 overflow-hidden font-mono text-[9px] font-medium uppercase tracking-[0.13em] sm:text-[10px] ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
			{#if isNew}
				<span class={`shrink-0 rounded px-1.5 py-0.5 text-[8px] font-bold tracking-widest ${dark ? 'bg-white/10 text-zinc-300' : 'bg-zinc-200 text-zinc-600'}`}>NEW</span>
			{/if}
			<span class="shrink-0 truncate" style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			<span class={`shrink-0 ${dark ? 'text-zinc-700' : 'text-zinc-300'}`}>/</span>
			<span class="min-w-0 truncate">{article.category}</span>
		</div>
		<div class="flex shrink-0 items-center gap-1.5">
			{#if readingTime(article.insight || article.content_snippet || '')}
				<span class={`text-xs font-medium ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{readingTime(article.insight || article.content_snippet || '')}</span>
				<span class={`${dark ? 'text-zinc-700' : 'text-zinc-300'}`}>·</span>
			{/if}
			<span class={`text-xs font-semibold ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>{relativeTime(article.published_date)}</span>
		</div>
	</div>

	<!-- Title -->
	<h3 class={`mt-3 mb-2 line-clamp-2 min-w-0 break-words text-lg font-semibold leading-[1.3] tracking-[-0.02em] transition-colors sm:text-xl ${dark ? 'text-zinc-100 group-hover:text-white' : 'text-zinc-900'}`} style="overflow-wrap: anywhere;">{article.title}</h3>

	<!-- Snippet + actions row -->
	<p class={`line-clamp-3 min-w-0 overflow-hidden text-sm leading-6 sm:text-[15px] ${dark ? 'text-zinc-400' : 'text-zinc-600'}`} style="overflow-wrap: anywhere;">{stripHtml(article.insight || article.content_snippet || '')}</p>

	<!-- Primary article actions -->
	<div class="mt-4 flex items-center justify-between border-t pt-3 {dark ? 'border-white/[0.05]' : 'border-zinc-100'}">
		{#if formatEngagement(article.likes)}
			<span class={`flex items-center gap-1 text-xs tabular-nums ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
				<ArrowUp class="h-3 w-3" />{formatEngagement(article.likes)}
			</span>
		{:else}
			<span></span>
		{/if}
		<div class="pointer-events-auto flex items-center gap-1.5">
		<button
			type="button"
			onclick={handleChatTeaser}
			class={`inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3 py-1.5 text-[11px] font-semibold transition-all ${
				dark
					? 'border-white/10 bg-white/[0.04] text-zinc-200 hover:border-white/25 hover:bg-white/[0.08] hover:text-white'
					: 'border-black/10 bg-black/[0.03] text-zinc-800 hover:border-black/25 hover:text-black'
			}`}
			aria-label="Ask Axon AI about this article"
		>
			<Sparkles class="h-3 w-3 shrink-0" />
			Ask Axon
		</button>
			<button
				type="button"
				onclick={handleSave}
				class={`flex h-9 w-9 items-center justify-center rounded-full transition-colors ${dark ? 'text-zinc-500 hover:bg-white/[0.06] hover:text-white' : 'text-zinc-400 hover:bg-zinc-100 hover:text-black'}`}
				aria-label={isSaved ? 'Remove from saved' : 'Save article'}
			>
				<Zap class={`h-3.5 w-3.5 ${isSaved ? (dark ? 'fill-white text-white' : 'fill-black text-black') : ''}`} />
			</button>
		</div>
	</div>
</article>
