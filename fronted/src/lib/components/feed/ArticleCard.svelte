<script lang="ts">
	import { Zap } from 'lucide-svelte';
	import type { Article } from '$lib/api';
	import { getBrandColor, relativeTime, stripHtml } from '$lib/ui';

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
	class={`group relative w-full rounded-3xl border border-transparent px-4 py-6 text-left transition-all sm:px-5 sm:py-7 lg:-mx-4 lg:rounded-xl lg:px-4 lg:py-10 ${selected ? 'bg-white/3' : 'hover:bg-white/1.5'}`}
>
	<button
		type="button"
		onclick={() => onOpen(article)}
		class="absolute inset-0 rounded-3xl lg:rounded-xl"
		aria-label={`Open ${article.title}`}
	></button>

	<div
		class={`absolute bottom-6 left-0 top-6 w-0.5 rounded-full transition-opacity lg:bottom-10 lg:top-10 ${selected ? 'opacity-100' : 'opacity-40 group-hover:opacity-100'}`}
		style={`background-color: ${getBrandColor(article.source)}`}
	></div>

	<div class="pointer-events-none relative z-10 flex flex-col gap-3 pl-4 sm:gap-3.5 lg:gap-2.5">
		<div class="flex items-start justify-between gap-3">
			<div class="space-y-2">
				<div class="flex flex-wrap items-center gap-2 text-[10px] font-bold uppercase tracking-[1.8px] text-zinc-600">
					<span style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
					<span class="text-zinc-800">·</span>
					<span>{relativeTime(article.published_date)}</span>
					<span class="rounded-full border border-white/8 px-2 py-1 text-[9px] tracking-[1.6px] text-zinc-500 sm:hidden">
						{article.category}
					</span>
				</div>

				<h3 class="text-[16px] font-semibold leading-snug text-white transition-colors group-hover:text-zinc-200 sm:text-[17px]">
					{article.title}
				</h3>
			</div>

			<button
				type="button"
				onclick={(event) => {
					event.stopPropagation();
					onToggleSave(article.id);
				}}
				class="pointer-events-auto flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl text-zinc-600 transition-colors hover:bg-white/4 hover:text-white"
				aria-label={isSaved ? 'Remove from saved' : 'Save article'}
			>
				<Zap class={`h-4 w-4 ${isSaved ? 'fill-white text-white' : ''}`} />
			</button>
		</div>

		<p class="line-clamp-3 max-w-2xl text-[13px] font-medium leading-6 text-zinc-400 sm:text-[13.5px] lg:line-clamp-2 lg:text-zinc-500">
			{stripHtml(article.insight || article.content_snippet || '')}
		</p>

		<div class="hidden items-center justify-between pt-1 lg:flex">
			<div class="flex items-center gap-3 text-[10.5px] font-bold uppercase tracking-widest text-zinc-700">
				<span style={`color: ${getBrandColor(article.source)}`}>{article.source}</span>
				<span class="text-zinc-800">·</span>
				<span>{relativeTime(article.published_date)}</span>
			</div>
		</div>
	</div>
</article>