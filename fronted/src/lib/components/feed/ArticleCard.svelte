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

	function signalTier(): 'High' | 'Medium' | 'Low' {
		const score = (article.engagement_score || 0) + (article.likes || 0) * 0.6 + (article.views || 0) * 0.15;
		if (score >= 180) return 'High';
		if (score >= 60) return 'Medium';
		return 'Low';
	}

	function signalClass(tier: 'High' | 'Medium' | 'Low') {
		if (tier === 'High') return dark ? 'bg-emerald-500/20 text-emerald-300' : 'bg-emerald-100 text-emerald-700';
		if (tier === 'Medium') return dark ? 'bg-amber-500/20 text-amber-300' : 'bg-amber-100 text-amber-700';
		return dark ? 'bg-zinc-700/70 text-zinc-300' : 'bg-zinc-200 text-zinc-700';
	}

	function cardClass() {
		if (selected && dark) return 'border-white/15 bg-white/[0.06] shadow-[0_0_0_1px_rgba(255,255,255,0.04)]';
		if (selected && !dark) return 'border-zinc-300 bg-white shadow-[0_4px_20px_rgba(15,23,42,0.08)]';
		if (isNew && dark) return 'border-white/[0.1] bg-white/[0.04]';
		if (isNew && !dark) return 'border-zinc-200 bg-white';
		if (isRead) return dark ? 'border-transparent opacity-55 hover:opacity-80 hover:bg-white/[0.03]' : 'border-transparent opacity-55 hover:opacity-80 hover:bg-zinc-50';
		if (dark) return 'border-transparent hover:bg-white/[0.03]';
		return 'border-transparent hover:bg-zinc-50';
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

<article class={`group relative w-full min-w-0 max-w-full overflow-hidden rounded-xl border px-3.5 py-3.5 transition-all duration-200 sm:px-4 sm:py-4 ${cardClass()}`}>
	<!-- Full-card open button (behind everything) -->
	<button type="button" onclick={handleOpen} class="absolute inset-0 rounded-xl" aria-label={`Open ${article.title}`}></button>

	<!-- Source / category / signal meta row -->
	<div class="flex min-w-0 items-center justify-between gap-2">
		<div class={`flex min-w-0 flex-1 items-center gap-2 overflow-hidden text-xs font-semibold uppercase tracking-wider lg:text-sm ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
			{#if isNew}
				<span class={`shrink-0 rounded px-1.5 py-0.5 text-[8px] font-bold tracking-widest ${dark ? 'bg-white/10 text-zinc-300' : 'bg-zinc-200 text-zinc-600'}`}>NEW</span>
			{/if}
			<span class="shrink-0 truncate" style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			<span class={`shrink-0 ${dark ? 'text-zinc-700' : 'text-zinc-300'}`}>/</span>
			<span class="min-w-0 truncate">{article.category}</span>
			<span class={`shrink-0 rounded-full px-1.5 py-0.5 text-[8px] font-bold normal-case tracking-normal ${signalClass(signalTier())}`}>
				Signal {signalTier()}
			</span>
			{#if formatEngagement(article.likes)}
				<span class={`flex shrink-0 items-center gap-0.5 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>
					<ArrowUp class="h-2.5 w-2.5" />{formatEngagement(article.likes)}
				</span>
			{/if}
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
	<h3 class={`mt-2 mb-2 line-clamp-2 min-w-0 break-words text-base font-semibold leading-snug tracking-tight transition-colors sm:text-lg lg:text-xl ${dark ? 'text-zinc-100' : 'text-zinc-800'}`} style="overflow-wrap: anywhere;">{article.title}</h3>

	<!-- Snippet + actions row -->
	<div class="flex min-w-0 items-end gap-2">
		<p class={`line-clamp-2 min-w-0 flex-1 overflow-hidden text-sm leading-relaxed sm:text-base lg:text-base lg:leading-relaxed ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} style="overflow-wrap: anywhere;">{stripHtml(article.insight || article.content_snippet || '')}</p>

		<div class="pointer-events-auto flex shrink-0 items-center gap-1">
			<!-- Save -->
			<button
				type="button"
				onclick={handleSave}
				class={`flex h-8 w-8 items-center justify-center rounded-md transition-colors ${dark ? 'text-zinc-500 hover:bg-white/[0.06]' : 'text-zinc-400 hover:bg-zinc-100'}`}
				aria-label={isSaved ? 'Remove from saved' : 'Save article'}
			>
				<Zap class={`h-3.5 w-3.5 ${isSaved ? (dark ? 'fill-white text-white' : 'fill-black text-black') : ''}`} />
			</button>
		</div>
	</div>

	<!-- AI chat teaser — always visible, bottom of card -->
	<div class="mt-2.5 pt-2 border-t {dark ? 'border-white/[0.04]' : 'border-zinc-100'}">
		<button
			type="button"
			onclick={handleChatTeaser}
			class={`pointer-events-auto inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-all lg:text-sm lg:px-3 ${
				dark
					? 'border-white/[0.06] text-zinc-500 hover:border-white/15 hover:bg-white/[0.05] hover:text-zinc-300'
					: 'border-zinc-200 text-zinc-400 hover:border-zinc-300 hover:bg-zinc-50 hover:text-zinc-600'
			}`}
			aria-label="Ask Axon AI about this article"
		>
			<Sparkles class="h-3 w-3 shrink-0" />
			Ask Axon
		</button>
	</div>
</article>
