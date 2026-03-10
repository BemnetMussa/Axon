<script lang="ts">
	import { ArrowUp, Zap } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import { getBrandColor, formatEngagement, relativeTime, stripHtml } from '$lib/ui';

	type Props = {
		article: Article;
		selected: boolean;
		isSaved: boolean;
		theme: 'dark' | 'light';
		onOpen: (article: Article) => void;
		onToggleSave: (id: number) => void;
	};

	let { article, selected, isSaved, theme, onOpen, onToggleSave }: Props = $props();
	let dark = $derived(theme === 'dark');

	function cardClass() {
		if (selected && dark) return 'border-white/10 bg-white/[0.04]';
		if (selected && !dark) return 'border-zinc-300 bg-zinc-50';
		if (dark) return 'border-transparent hover:bg-white/[0.02]';
		return 'border-transparent hover:bg-zinc-50';
	}
</script>

<article class={`group relative flex gap-3 rounded-lg border px-3 py-3 transition-all sm:gap-4 sm:px-4 sm:py-3.5 ${cardClass()}`}>
	<button type="button" onclick={() => onOpen(article)} class="absolute inset-0 rounded-lg" aria-label={`Open ${article.title}`}></button>

	<div class="mt-1 h-2 w-2 shrink-0 rounded-full" style={`background-color: ${getBrandColor(article.source)}`}></div>

	<div class="min-w-0 flex-1">
		<div class={`mb-1 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
			<span style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			<span class={dark ? 'text-zinc-700' : 'text-zinc-300'}>/</span>
			<span>{article.category}</span>
			{#if formatEngagement(article.likes)}
				<span class={`flex items-center gap-0.5 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>
					<ArrowUp class="h-2.5 w-2.5" />{formatEngagement(article.likes)}
				</span>
			{/if}
			<span class={`ml-auto ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{relativeTime(article.published_date)}</span>
		</div>

		<h3 class={`mb-1.5 text-[14px] font-semibold leading-snug transition-colors sm:text-[15px] ${dark ? 'text-zinc-100' : 'text-zinc-800'}`}>{article.title}</h3>

		<p class={`line-clamp-2 text-[12.5px] leading-relaxed sm:text-[13px] ${dark ? 'text-zinc-500' : 'text-zinc-500'}`}>{stripHtml(article.insight || article.content_snippet || '')}</p>
	</div>

	<button
		type="button"
		onclick={(event) => { event.stopPropagation(); onToggleSave(article.id); }}
		class={`pointer-events-auto mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md transition-colors ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}
		aria-label={isSaved ? 'Remove from saved' : 'Save article'}
	>
		<Zap class={`h-3.5 w-3.5 ${isSaved ? (dark ? 'fill-white text-white' : 'fill-black text-black') : ''}`} />
	</button>
</article>
