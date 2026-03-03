<script lang="ts">
  import { X, Bot, Sparkles, Target, Zap, ChevronRight } from 'lucide-svelte';
	import { fade, scale, slide } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';

	interface Props {
		open: boolean;
		loading: boolean;
		title: string;
		briefData: string | null;
		onClose: () => void;
	}

	let { open, loading, title, briefData, onClose }: Props = $props();

	// Function to parse the Markdown-like response from Groq
	// e.g., "1. **Technical Primitive**: ... 2. **Market Impact**: ... 3. **Opportunity**: ..."
	$effect(() => {
		if (open) {
      document.body.style.overflow = 'hidden';
		} else {
      document.body.style.overflow = '';
		}
	});

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) {
			onClose();
		}
	}

	function parseBriefSegments(text: string) {
    if (!text) return [];
    
    // Split by bullet points or numbers (e.g., "1.", "2.", "-", "*") looking for bold labels
    const regex = /(?:[A-Z][a-zA-Z\s]+:|(?:\d+\.|[-*])\s*\*\*([^*]+)\*\*:?)/g;
    const parts = text.split(regex);
    
    let segments = [];
    
    // For Groq's current prompt "Technical Primitive, Market Impact, Opportunity"
    if (text.includes('Technical Primitive')) {
      const match1 = text.match(/(?:\*\*Technical Primitive\*\*[:\s]*|1\.\s*)([^*]+)(?:\*\*Market Impact\*\*|2\.)/is);
      const match2 = text.match(/(?:\*\*Market Impact\*\*[:\s]*|2\.\s*)([^*]+)(?:\*\*Opportunity\*\*|3\.)/is);
      const match3 = text.match(/(?:\*\*Opportunity\*\*[:\s]*|3\.\s*)([^*]+)$/is);
      
      if (match1 && match2 && match3) {
        segments.push({ title: 'Technical Primitive', content: match1[1].trim(), icon: Zap, color: 'text-violet-400', bg: 'bg-violet-500/10' });
        segments.push({ title: 'Market Impact', content: match2[1].trim(), icon: Target, color: 'text-amber-400', bg: 'bg-amber-500/10' });
        segments.push({ title: 'Opportunity', content: match3[1].trim(), icon: Sparkles, color: 'text-emerald-400', bg: 'bg-emerald-500/10' });
        return segments;
      }
    }
    
    // Fallback if parsing fails - just return chunks
    const paragraphs = text.split('\n\n').filter(p => p.trim() !== '');
    return paragraphs.map((p, i) => ({
      title: i === 0 ? 'Analysis' : i === 1 ? 'Impact' : 'Takeaway',
      content: p,
      icon: ChevronRight,
      color: 'text-zinc-300',
      bg: 'bg-zinc-800'
    }));
  }

  let segments = $derived(parseBriefSegments(briefData || ''));
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div 
    class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
    in:fade={{ duration: 200 }}
    out:fade={{ duration: 150 }}
  >
		<!-- Backdrop -->
		<div 
      class="absolute inset-0 bg-black/60 backdrop-blur-xl transition-opacity" 
      onclick={onClose}
      aria-hidden="true"
    ></div>

		<!-- Modal body -->
		<div 
      class="relative w-full max-w-2xl bg-[#0d0d12] border border-zinc-800/80 rounded-2xl shadow-2xl shadow-emerald-500/5 overflow-hidden flex flex-col max-h-[90vh]"
      in:scale={{ duration: 300, start: 0.95, easing: cubicOut }}
      out:scale={{ duration: 200, start: 0.98 }}
      role="dialog"
      aria-modal="true"
    >
      <!-- Glass reflection top edge -->
      <div class="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-zinc-600/50 to-transparent"></div>
			
      <!-- Header -->
			<div class="flex items-start justify-between p-6 border-b border-zinc-800/60 bg-white/[0.02]">
				<div class="pr-8">
					<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-500 mb-3">
						<Bot class="w-4 h-4" /> 
            Deep Briefing
					</div>
					<h3 class="text-xl font-medium text-white leading-snug">{title}</h3>
				</div>
				<button 
          onclick={onClose}
          class="absolute top-6 right-6 p-2 rounded-full text-zinc-500 hover:text-white hover:bg-zinc-800 transition-colors"
          aria-label="Close modal"
        >
					<X class="w-5 h-5" />
				</button>
			</div>

			<!-- Content Area -->
			<div class="p-6 sm:p-8 overflow-y-auto no-scrollbar relative min-h-[250px] bg-gradient-to-b from-[#0d0d12] to-black">
				{#if loading}
          <div 
            class="absolute inset-0 flex flex-col items-center justify-center p-8 space-y-6"
            in:fade={{ duration: 200 }}
          >
            <div class="relative w-16 h-16">
              <!-- Animated rings -->
              <div class="absolute inset-0 border-2 border-emerald-500/20 rounded-full animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite]"></div>
              <div class="absolute inset-2 border-2 border-emerald-500/40 rounded-full animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite_200ms]"></div>
              <div class="absolute inset-4 border-2 border-emerald-500 rounded-full animate-pulse flex items-center justify-center">
                <Bot class="w-4 h-4 text-emerald-400" />
              </div>
            </div>
            
            <div class="text-center space-y-2">
              <p class="text-emerald-400 text-sm font-medium animate-pulse tracking-wide">ANALYZING SIGNAL</p>
              <p class="text-zinc-500 text-xs">Synthesizing primitives and projecting market impact...</p>
            </div>
          </div>
				{:else if briefData}
					<div class="space-y-6" in:fade={{ duration: 400, delay: 100 }}>
            {#each segments as segment, i}
              <div 
                class="group flex gap-4 p-5 rounded-xl border border-zinc-800/40 bg-white/[0.01] hover:bg-white/[0.03] hover:border-zinc-700/50 transition-all"
                in:slide={{ duration: 400, delay: i * 150 }}
              >
                <div class="{segment.bg} w-10 h-10 rounded-lg flex items-center justify-center shrink-0 border border-white/5">
                  <segment.icon class="w-5 h-5 {segment.color}" />
                </div>
                <div class="space-y-1.5 pt-0.5">
                  <h4 class="text-sm font-medium text-white">{segment.title}</h4>
                  <p class="text-[15px] leading-relaxed text-zinc-400">{segment.content}</p>
                </div>
              </div>
            {/each}
					</div>
				{:else}
					<div class="flex flex-col items-center justify-center h-full text-zinc-500 text-sm space-y-3">
            <Bot class="w-8 h-8 opacity-50" />
            <p>Analysis failed or no data available.</p>
          </div>
				{/if}
			</div>
      
      <!-- Footer details -->
      <div class="px-6 py-4 border-t border-zinc-800/60 bg-black flex justify-between items-center">
        <div class="text-[10px] tracking-widest text-zinc-600 uppercase">Powered by Groq ✨</div>
        <div class="text-[10px] text-zinc-600 flex items-center gap-1">
          Press <kbd class="px-1.5 py-0.5 bg-zinc-800 rounded text-zinc-400 font-sans">Esc</kbd> to close
        </div>
      </div>
		</div>
	</div>
{/if}

<style>
  /* Hide scrollbar for Chrome, Safari and Opera */
  .no-scrollbar::-webkit-scrollbar {
      display: none;
  }
  /* Hide scrollbar for IE, Edge and Firefox */
  .no-scrollbar {
      -ms-overflow-style: none;  /* IE and Edge */
      scrollbar-width: none;  /* Firefox */
  }
</style>
