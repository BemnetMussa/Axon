<script lang="ts">
    import { api } from '$lib/api';
    import { Sparkles, Star, MessageSquare, Send, X } from 'lucide-svelte';
    import SignalLoader from '$lib/components/ui/SignalLoader.svelte';
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
    >
        <button type="button" class="absolute inset-0 cursor-default" onclick={close} aria-label="Close feedback dialog"></button>
        <!-- Modal -->
        <div 
            class={`relative w-full max-w-md overflow-hidden rounded-[2rem] border shadow-2xl transition-all ${theme === 'dark' ? 'border-white/10 bg-[#0B0F17]/95 text-white shadow-black/20' : 'border-zinc-200 bg-white/95 text-zinc-900 shadow-xl'}`}
            transition:fly={{ y: 20, duration: 300, delay: 100 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="feedback-title"
        >
            <div class="p-8">
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center gap-3">
                        <div class={`flex h-10 w-10 items-center justify-center rounded-xl ${theme === 'dark' ? 'bg-white/10 text-white' : 'bg-black/10 text-black'}`}>
                            <Sparkles class="h-5 w-5" />
                        </div>
                        <h2 id="feedback-title" class="text-xl font-bold">Feedback</h2>
                    </div>
                    <button 
                        type="button"
                        onclick={close}
                        class={`p-2 rounded-full transition-colors ${theme === 'dark' ? 'hover:bg-white/5 text-zinc-400' : 'hover:bg-zinc-100 text-zinc-500'}`}
                        aria-label="Close feedback dialog"
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
                        <p class={`text-sm ${theme === 'dark' ? 'text-zinc-400' : 'text-zinc-600'}`}>Your feedback helps us build a better Axon.</p>
                    </div>
                {:else}
                    <div class="space-y-6">
                        <fieldset>
                            <legend class={`block text-xs font-semibold uppercase tracking-wider mb-3 ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
                                Overall Rating
                            </legend>
                            <div class="flex gap-2">
                                {#each [1, 2, 3, 4, 5] as star}
                                    <button 
                                        type="button"
                                        onclick={() => rating = star}
                                        class={`group relative p-2 transition-transform hover:scale-110 active:scale-95`}
                                        aria-label={`${star} out of 5 stars`}
                                        aria-pressed={rating === star}
                                    >
                                        <Star 
                                            class={`h-8 w-8 transition-colors ${rating >= star ? 'fill-yellow-400 text-yellow-400' : theme === 'dark' ? 'text-zinc-700' : 'text-zinc-300'}`} 
                                        />
                                    </button>
                                {/each}
                            </div>
                        </fieldset>

                        <div>
                            <label for="feedback-comment" class={`block text-xs font-semibold uppercase tracking-wider mb-3 ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}>
                                Thoughts & Suggestions
                            </label>
                            <div class="relative">
                                <textarea
                                    id="feedback-comment"
                                    name="feedback-comment"
                                    bind:value={comment}
                                    placeholder="Tell us what you think..."
                                    class={`w-full rounded-2xl border p-4 text-sm min-h-[120px] outline-none transition-all resize-none ${theme === 'dark' ? 'bg-[#0B0F17]/50 border-white/10 focus:border-white/30 text-white placeholder:text-zinc-600' : 'bg-zinc-50 border-zinc-200 focus:border-black/30 text-zinc-900 placeholder:text-zinc-400'}`}
                                ></textarea>
                                <MessageSquare class={`absolute right-4 bottom-4 h-4 w-4 ${theme === 'dark' ? 'text-zinc-700' : 'text-zinc-300'}`} />
                            </div>
                        </div>

                        {#if error}
                            <p role="alert" class="text-xs font-medium text-red-500">{error}</p>
                        {/if}

                        <button 
                            type="button"
                            onclick={handleSubmit}
                            disabled={submitting}
                            class={`w-full group inline-flex h-12 items-center justify-center gap-2 rounded-xl px-6 font-bold transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none shadow-lg ${theme === 'dark' ? 'bg-black text-white hover:bg-zinc-800 shadow-black/10' : 'bg-white text-black hover:bg-zinc-200 shadow-black/20'}`}
                        >
                            {#if submitting}
                                <SignalLoader size={16} />
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
