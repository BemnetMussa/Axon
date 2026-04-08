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
		if (selected && dark) return 'border-white/15 bg-white/[0.06] shadow-[0_0_0_1px_rgba(255,255,255,0.04)]';
		if (selected && !dark) return 'border-zinc-300 bg-white shadow-[0_4px_20px_rgba(15,23,42,0.08)]';
		if (isNew && dark) return 'border-white/[0.1] bg-white/[0.04]';
		if (isNew && !dark) return 'border-zinc-200 bg-white';
		if (isRead) return dark ? 'border-transparent opacity-55 hover:opacity-80 hover:bg-white/[0.03]' : 'border-transparent opacity-55 hover:opacity-80 hover:bg-zinc-50';
		if (dark) return 'border-transparent hover:bg-white/[0.03]';
		return 'border-transparent hover:bg-zinc-50';
	}
</script>

<article class={`group relative w-full min-w-0 max-w-full overflow-hidden rounded-2xl border px-3.5 py-3.5 transition-all duration-200 sm:px-4 sm:py-4 ${cardClass()}`}>
	<button type="button" onclick={() => onOpen(article)} class="absolute inset-0 rounded-lg" aria-label={`Open ${article.title}`}></button>

	<div class="flex min-w-0 items-center justify-between gap-2">
		<div class={`flex min-w-0 flex-1 items-center gap-2 overflow-hidden text-[10px] font-semibold uppercase tracking-wider ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>
			{#if isNew}
				<span class={`shrink-0 rounded px-1.5 py-0.5 text-[8px] font-bold tracking-widest ${dark ? 'bg-white/10 text-zinc-300' : 'bg-zinc-200 text-zinc-600'}`}>NEW</span>
			{/if}
			<span class="shrink-0 truncate" style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			<span class={`shrink-0 ${dark ? 'text-zinc-700' : 'text-zinc-300'}`}>/</span>
			<span class="min-w-0 truncate">{article.category}</span>
			{#if formatEngagement(article.likes)}
				<span class={`flex shrink-0 items-center gap-0.5 ${dark ? 'text-zinc-600' : 'text-zinc-400'}`}>
					<ArrowUp class="h-2.5 w-2.5" />{formatEngagement(article.likes)}
				</span>
			{/if}
		</div>
		<span class={`shrink-0 text-[10px] font-semibold ${dark ? 'text-zinc-500' : 'text-zinc-400'}`}>{relativeTime(article.published_date)}</span>
	</div>

	<h3 class={`mt-2 mb-2 line-clamp-2 min-w-0 break-words text-[15px] font-semibold leading-snug tracking-tight transition-colors sm:text-[16px] ${dark ? 'text-zinc-100' : 'text-zinc-800'}`} style="overflow-wrap: anywhere;">{article.title}</h3>

	<div class="flex min-w-0 items-end gap-2">
		<p class={`line-clamp-2 min-w-0 flex-1 overflow-hidden text-[12.5px] leading-relaxed sm:text-[13px] ${dark ? 'text-zinc-400' : 'text-zinc-500'}`} style="overflow-wrap: anywhere;">{stripHtml(article.insight || article.content_snippet || '')}</p>
		<button
			type="button"
			onclick={(event) => { event.stopPropagation(); onToggleSave(article.id); }}
			class={`pointer-events-auto flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors ${dark ? 'text-zinc-500 hover:bg-white/[0.06]' : 'text-zinc-400 hover:bg-zinc-100'}`}
			aria-label={isSaved ? 'Remove from saved' : 'Save article'}
		>
			<Zap class={`h-3.5 w-3.5 ${isSaved ? (dark ? 'fill-white text-white' : 'fill-black text-black') : ''}`} />
		</button>
	</div>
</article>
