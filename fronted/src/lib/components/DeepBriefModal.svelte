<script lang="ts">
  import { X, Zap, Target, Activity, Bot } from 'lucide-svelte';
	import { fade, scale } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';

	interface Props {
		open: boolean;
		loading: boolean;
		title: string;
		briefData: string | null;
		onClose: () => void;
	}

	let { open, loading, title, briefData, onClose }: Props = $props();

	$effect(() => {
		document.body.style.overflow = open ? 'hidden' : '';
	});

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) onClose();
	}

	function parseBrief(text: string) {
		if (!text) return [];

		// Strip HTML before parsing
		const clean = text.replace(/<[^>]*>/g, '').replace(/&[a-z#0-9]+;/gi, ' ').replace(/\s+/g, ' ');

		if (clean.includes('Technical Primitive')) {
			const m1 = clean.match(/(?:Technical Primitive[:\s]*)([^*]+?)(?=Market Impact|2\.)/is);
			const m2 = clean.match(/(?:Market Impact[:\s]*)([^*]+?)(?=Opportunity|3\.)/is);
			const m3 = clean.match(/(?:Opportunity[:\s]*)(.+)$/is);

			if (m1 && m2 && m3) return [
				{ label: 'Technical Primitive', body: m1[1].trim(), icon: Zap, accent: 'border-l-cyan-500 text-cyan-400' },
				{ label: 'Market Impact', body: m2[1].trim(), icon: Target, accent: 'border-l-violet-500 text-violet-400' },
				{ label: 'Opportunity', body: m3[1].trim(), icon: Activity, accent: 'border-l-emerald-500 text-emerald-400' },
			];
		}

		// Fallback
		return clean.split(/\n\n+/).filter(Boolean).map((p, i) => ({
			label: ['Analysis', 'Context', 'Takeaway'][i] ?? `Section ${i + 1}`,
			body: p.trim(),
			icon: Activity,
			accent: 'border-l-zinc-600 text-zinc-400',
		}));
	}

	let segments = $derived(parseBrief(briefData ?? ''));
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div
		class="fixed inset-0 z-[200] flex items-end sm:items-center justify-center"
		in:fade={{ duration: 150 }}
		out:fade={{ duration: 100 }}
		style="font-family: 'Inter', sans-serif;"
	>
		<div class="absolute inset-0 bg-black/70 backdrop-blur-sm" onclick={onClose} aria-hidden="true"></div>

		<div
			class="relative w-full sm:max-w-2xl bg-[#111] border border-white/10 rounded-t-2xl sm:rounded-2xl shadow-2xl flex flex-col overflow-hidden max-h-[90vh]"
			in:scale={{ duration: 250, start: 0.97, easing: cubicOut }}
			role="dialog"
			aria-modal="true"
		>
			<!-- Header -->
			<div class="flex items-start justify-between p-6 border-b border-white/8 shrink-0">
				<div class="flex flex-col gap-1.5 pr-8">
					<div class="flex items-center gap-2 text-[11px] text-violet-400 font-semibold uppercase tracking-widest">
						<Bot class="w-3.5 h-3.5" />
						AI Deep Brief
					</div>
					<h3 class="text-white font-semibold text-[15px] leading-snug">{title}</h3>
				</div>
				<button
					onclick={onClose}
					class="p-1.5 rounded-lg text-zinc-500 hover:text-white hover:bg-white/8 transition-all"
					aria-label="Close"
				>
					<X class="w-4 h-4" />
				</button>
			</div>

			<!-- Body -->
			<div class="flex-1 overflow-y-auto min-h-0 p-6">
				{#if loading}
					<div class="py-16 flex flex-col items-center gap-5">
						<div class="relative w-10 h-10">
							<div class="absolute inset-0 border-2 border-violet-500/20 rounded-full"></div>
							<div class="absolute inset-0 border-t-2 border-violet-500 rounded-full animate-spin"></div>
						</div>
						<p class="text-zinc-500 text-[13px]">Generating intelligence brief via Groq…</p>
					</div>
				{:else if segments.length > 0}
					<div class="flex flex-col gap-7">
						{#each segments as seg, i}
							<div
								class="flex flex-col gap-2 pl-4 border-l-2 {seg.accent.split(' ')[0]}"
								in:fade={{ duration: 400, delay: i * 120 }}
							>
								<div class="flex items-center gap-2">
									<seg.icon class="w-3.5 h-3.5 {seg.accent.split(' ')[1]}" />
									<span class="text-[11px] font-bold uppercase tracking-widest {seg.accent.split(' ')[1]}">
										{seg.label}
									</span>
								</div>
								<p class="text-zinc-300 text-[14px] leading-relaxed">
									{seg.body}
								</p>
							</div>
						{/each}
					</div>
				{:else}
					<div class="py-12 text-center">
						<p class="text-zinc-500 text-[13px]">No briefing data available.</p>
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="px-6 py-4 border-t border-white/8 flex items-center justify-between shrink-0">
				<span class="text-[11px] text-zinc-600">Powered by Groq · LLaMA 3.1 70B</span>
				<button onclick={onClose} class="text-[12px] text-zinc-500 hover:text-white transition-colors font-medium">
					Close
				</button>
			</div>
		</div>
	</div>
{/if}
