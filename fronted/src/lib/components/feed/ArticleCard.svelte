<script lang="ts">
	import { ArrowUp, Zap } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import { getBrandColor, formatEngagement, relativeTime, stripHtml } from '$lib/ui';

	type Props = {
		article: Article;
		selected: boolean;
		isSaved: boolean;
		onOpen: (article: Article) => void;
		onToggleSave: (id: number) => void;
	};

	let { article, selected, isSaved, onOpen, onToggleSave }: Props = $props();
</script>

<article
	class={`group relative flex gap-3 rounded-lg border px-3 py-3 transition-all sm:gap-4 sm:px-4 sm:py-3.5 ${selected ? 'border-white/10 bg-white/[0.04]' : 'border-transparent hover:border-white/5 hover:bg-white/[0.02]'}`}
>
	<button
		type="button"
		onclick={() => onOpen(article)}
		class="absolute inset-0 rounded-lg"
		aria-label={`Open ${article.title}`}
	></button>

	<div
		class="mt-1 h-2 w-2 shrink-0 rounded-full"
		style={`background-color: ${getBrandColor(article.source)}`}
	></div>

	<div class="min-w-0 flex-1">
		<div class="mb-1 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
			<span style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
			<span class="text-zinc-700">/</span>
			<span>{article.category}</span>
			{#if formatEngagement(article.likes)}
				<span class="flex items-center gap-0.5 text-zinc-600">
					<ArrowUp class="h-2.5 w-2.5" />
					{formatEngagement(article.likes)}
				</span>
			{/if}
			<span class="ml-auto text-zinc-600">{relativeTime(article.published_date)}</span>
		</div>

		<h3 class="mb-1.5 text-[14px] font-semibold leading-snug text-zinc-100 transition-colors group-hover:text-white sm:text-[15px]">
			{article.title}
		</h3>

		<p class="line-clamp-2 text-[12.5px] leading-relaxed text-zinc-500 sm:text-[13px]">
			{stripHtml(article.insight || article.content_snippet || '')}
		</p>
	</div>

	<button
		type="button"
		onclick={(event) => {
			event.stopPropagation();
			onToggleSave(article.id);
		}}
		class="pointer-events-auto mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-zinc-600 transition-colors hover:bg-white/5 hover:text-white"
		aria-label={isSaved ? 'Remove from saved' : 'Save article'}
	>
		<Zap class={`h-3.5 w-3.5 ${isSaved ? 'fill-white text-white' : ''}`} />
	</button>
</article>
