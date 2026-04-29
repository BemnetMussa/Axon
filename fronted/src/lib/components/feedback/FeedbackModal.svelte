<script lang="ts">
    import { api } from '$lib/api';
    import { Sparkles, Star, MessageSquare, Send, X } from 'lucide-svelte';
    import { fade, fly } from 'svelte/transition';

    let { show = $bindable(false), theme = 'dark' } = $props();

    let rating = $state(0);
    let comment = $state('');
    let submitting = $state(false);
    let success = $state(false);
    let error = $state<string | null>(null);

    async function handleSubmit() {
        if (rating === 0) {
            error = "Please select a rating.";
            return;
        }
        submitting = true;
        error = null;
        try {
            await api.submitFeedback(rating, comment);
            success = true;
            setTimeout(() => {
                show = false;
                // Reset after closing
                setTimeout(() => {
                    success = false;
                    rating = 0;
                    comment = '';
                }, 500);
            }, 2000);
        } catch (e: any) {
            error = "Failed to submit feedback. Please try again.";
        } finally {
            submitting = false;
        }
    }

    function close() {
        if (!submitting) show = false;
    }
</script>

{#if show}
    <!-- Backdrop -->
    <div 
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-md bg-black/40"
        transition:fade={{ duration: 200 }}
        onclick={close}
    >
        <!-- Modal -->
        <div 
            class={`relative w-full max-w-md overflow-hidden rounded-[2rem] border shadow-2xl transition-all ${theme === 'dark' ? 'border-white/10 bg-[#0F1522]/95 text-white shadow-blue-500/10' : 'border-zinc-200 bg-white/95 text-zinc-900 shadow-xl'}`}
            transition:fly={{ y: 20, duration: 300, delay: 100 }}
            onclick={(e) => e.stopPropagation()}
        >
            <div class="p-8">
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center gap-3">
                        <div class={`flex h-10 w-10 items-center justify-center rounded-xl ${theme === 'dark' ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>
                            <Sparkles class="h-5 w-5" />
                        </div>
                        <h2 class="text-xl font-bold">Feedback</h2>
                    </div>
                    <button 
                        onclick={close}
                        class={`p-2 rounded-full transition-colors ${theme === 'dark' ? 'hover:bg-white/5 text-zinc-400' : 'hover:bg-zinc-100 text-zinc-500'}`}
                    >
                        <X class="h-5 w-5" />
                    </button>
                </div>

                {#if success}
                    <div class="flex flex-col items-center justify-center py-10 text-center" in:fade>
                        <div class="mb-4 h-16 w-16 items-center justify-center rounded-full bg-green-500/20 text-green-500 flex">
                            <Send class="h-8 w-8" />
                        </div>
                        <h3 class="text-lg font-bold mb-2">Thank you!</h3>
                        <p class={`text-sm ${theme === 'dark' ? 'text-zinc-400' : 'text-zinc-600'}`}>Your feedback help us build the future of Axon.</p>
                    </div>
                {:else}
                    <div class="space-y-6">
                        <div>
                            <label class={`block text-xs font-semibold uppercase tracking-wider mb-3 ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
                                Overall Rating
                            </label>
                            <div class="flex gap-2">
                                {#each [1, 2, 3, 4, 5] as star}
                                    <button 
                                        onclick={() => rating = star}
                                        class={`group relative p-2 transition-transform hover:scale-110 active:scale-95`}
                                    >
                                        <Star 
                                            class={`h-8 w-8 transition-colors ${rating >= star ? 'fill-yellow-400 text-yellow-400' : theme === 'dark' ? 'text-zinc-700' : 'text-zinc-300'}`} 
                                        />
                                    </button>
                                {/each}
                            </div>
                        </div>

                        <div>
                            <label class={`block text-xs font-semibold uppercase tracking-wider mb-3 ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
                                Thoughts & Suggestions
                            </label>
                            <div class="relative">
                                <textarea
                                    bind:value={comment}
                                    placeholder="Tell us what you think..."
                                    class={`w-full rounded-2xl border p-4 text-sm min-h-[120px] outline-none transition-all resize-none ${theme === 'dark' ? 'bg-[#0B0F17]/50 border-white/10 focus:border-blue-500/50 text-white placeholder:text-zinc-600' : 'bg-zinc-50 border-zinc-200 focus:border-blue-500/50 text-zinc-900 placeholder:text-zinc-400'}`}
                                ></textarea>
                                <MessageSquare class={`absolute right-4 bottom-4 h-4 w-4 ${theme === 'dark' ? 'text-zinc-700' : 'text-zinc-300'}`} />
                            </div>
                        </div>

                        {#if error}
                            <p class="text-xs font-medium text-red-500">{error}</p>
                        {/if}

                        <button 
                            onclick={handleSubmit}
                            disabled={submitting}
                            class={`w-full group inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 font-bold text-white transition-all hover:bg-blue-500 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none shadow-lg shadow-blue-500/20`}
                        >
                            {#if submitting}
                                <div class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                                Sending...
                            {:else}
                                Submit Feedback
                                <Send class="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                            {/if}
                        </button>
                        
                        <p class={`text-[11px] text-center ${theme === 'dark' ? 'text-zinc-600' : 'text-zinc-400'}`}>
                            Your blood and tears made this great. We just keep it running.
                        </p>
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    textarea::-webkit-scrollbar {
        display: none;
    }
</style>
