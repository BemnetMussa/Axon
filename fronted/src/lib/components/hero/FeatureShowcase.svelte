<script lang="ts">
	import { onMount } from 'svelte';
	import { BookOpen, MessageSquare, CalendarDays } from 'lucide-svelte';
	import { reveal } from '$lib/actions/reveal';
	import type { PreviewScreen } from '$lib/preview-content';
	import PhoneFrame from './PhoneFrame.svelte';

	let theme = $state<'dark' | 'light'>('dark');
	onMount(() => {
		const read = () => (theme = document.documentElement.classList.contains('light') ? 'light' : 'dark');
		read();
		const mo = new MutationObserver(read);
		mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
		return () => mo.disconnect();
	});

	const features: { key: PreviewScreen; n: string; icon: typeof BookOpen; label: string; title: string; body: string; points: string[] }[] = [
		{
			key: 'read',
			n: '01',
			icon: BookOpen,
			label: 'Read',
			title: 'A brief for every story.',
			body: 'Axon fetches the full article and writes a brief from it: the main point, the specifics, and the caveats the source itself states. No added opinions. The original is one tap away.',
			points: ['Written from the full text, not the headline', 'Source, date and traction on every story']
		},
		{
			key: 'ask',
			n: '02',
			icon: MessageSquare,
			label: 'Ask',
			title: 'Ask the story, not the internet.',
			body: 'Every story has its own chat. Answers come from that article, so they stay on topic and tell you what it does not cover. Suggested questions get you started.',
			points: ['Grounded in the article you are reading', 'Voice input on supported phones']
		},
		{
			key: 'digest',
			n: '03',
			icon: CalendarDays,
			label: 'Catch up',
			title: 'The week, in one read.',
			body: 'Once a week Axon writes a synthesis of what moved: the big picture, the breakthroughs, and where builders should look next. Miss a few days and you are still current.',
			points: ['Built from the stories the filter kept', 'Install it as an app and get push alerts']
		}
	];
</script>

<div class="space-y-24 sm:space-y-32">
	{#each features as f, i (f.key)}
		<div class="grid items-center gap-12 lg:grid-cols-2 lg:gap-20">
			<div use:reveal class={i % 2 === 1 ? 'lg:order-2' : ''}>
				<p class="axon-label flex items-center gap-3 text-black/45 dark:text-white/40">
					<span class="tabular-nums">{f.n}</span>
					<span class="h-px w-6 bg-current"></span>
					<f.icon class="h-3.5 w-3.5" />
					{f.label}
				</p>
				<h3 class="mt-6 max-w-md text-3xl font-semibold leading-tight tracking-[-0.03em] sm:text-4xl">{f.title}</h3>
				<p class="mt-5 max-w-md text-[15px] leading-relaxed text-black/60 dark:text-white/55">{f.body}</p>
				<ul class="mt-8 max-w-md border-t border-black/10 dark:border-white/10">
					{#each f.points as point}
						<li class="flex items-center gap-3 border-b border-black/10 py-3 text-sm text-black/70 dark:border-white/10 dark:text-white/65">
							<span class="h-1 w-1 shrink-0 bg-current"></span>{point}
						</li>
					{/each}
				</ul>
			</div>

			<div use:reveal={{ delay: 80 }} class={`flex justify-center ${i % 2 === 1 ? 'lg:order-1' : ''}`}>
				<PhoneFrame screen={f.key} {theme} title={`Axon ${f.label.toLowerCase()} screen on a phone`} />
			</div>
		</div>
	{/each}
</div>
