<script lang="ts">
	import { ArrowUp, Zap } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import { getBrandColor, formatEngagement, relativeTime, stripHtml } from '$lib/ui';

	type Props = {
		article: Article;
		selected: boolean;
		isSaved: boolean;
		isNew?: boolean;
		isRead?: boolean;
		theme: 'dark' | 'light';
		onOpen: (article: Article) => void;
		onToggleSave: (id: number) => void;
	};

	let { article, selected, isSaved, isNew = false, isRead = false, theme, onOpen, onToggleSave }: Props = $props();
	let dark = $derived(theme === 'dark');

	function cardClass() {
		if (selected && dark) return 'border-white/10 bg-white/[0.04]';
		if (selected && !dark) return 'border-zinc-300 bg-zinc-50';
		if (isNew && dark) return 'border-white/[0.08] bg-white/[0.03]';
		if (isNew && !dark) return 'border-zinc-200 bg-zinc-50/60';
		if (isRead) return dark ? 'border-transparent opacity-50 hover:opacity-75 hover:bg-white/[0.02]' : 'border-transparent opacity-50 hover:opacity-75 hover:bg-zinc-50';
		if (dark) return 'border-transparent hover:bg-white/[0.02]';
		return 'border-transparent hover:bg-zinc-50';
	}
</script>

<article class={`group relative rounded-lg border px-3 py-3 transition-all sm:px-4 sm:py-3.5 ${cardClass()}`}>
	<button type="button" onclick={() => onOpen(article)} class="absolute inset-0 rounded-lg" aria-label={`Open ${article.title}`}></button>

	<div class="flex items-center justify-between gap-2">
		<div class={`flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
			{#if isNew}
				<span class={`rounded px-1.5 py-0.5 text-[8px] font-bold tracking-widest ${dark ? 'bg-white/10 text-zinc-300' : 'bg-zinc-200 text-zinc-600'}`}>NEW</span>
			{/if}
			<span style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			<span class={dark ? 'text-zinc-700' : 'text-zinc-300'}>/</span>
			<span>{article.category}</span>
			{#if formatEngagement(article.likes)}
				<span class={`flex items-center gap-0.5 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>
					<ArrowUp class="h-2.5 w-2.5" />{formatEngagement(article.likes)}
				</span>
			{/if}
		</div>
		<span class={`shrink-0 text-[10px] font-semibold ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>{relativeTime(article.published_date)}</span>
	</div>

	<h3 class={`mt-1.5 mb-1.5 text-[14px] font-semibold leading-snug transition-colors sm:text-[15px] ${dark ? 'text-zinc-100' : 'text-zinc-800'}`}>{article.title}</h3>

	<div class="flex items-end gap-2">
		<p class={`line-clamp-2 min-w-0 flex-1 text-[12.5px] leading-relaxed sm:text-[13px] ${dark ? 'text-zinc-500' : 'text-zinc-500'}`}>{stripHtml(article.insight || article.content_snippet || '')}</p>
		<button
			type="button"
			onclick={(event) => { event.stopPropagation(); onToggleSave(article.id); }}
			class={`pointer-events-auto flex h-7 w-7 shrink-0 items-center justify-center rounded-md transition-colors ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}
			aria-label={isSaved ? 'Remove from saved' : 'Save article'}
		>
			<Zap class={`h-3.5 w-3.5 ${isSaved ? (dark ? 'fill-white text-white' : 'fill-black text-black') : ''}`} />
		</button>
	</div>
</article>
