<script lang="ts">
	import { Home, Bookmark, Sparkles, Menu, Sun, Moon, X, MessageSquare, LogOut } from 'lucide-svelte';
	import { signOutToHome } from '$lib/auth-client';
	import NotificationToggle from '../ui/NotificationToggle.svelte';
	import FeedbackModal from '../feedback/FeedbackModal.svelte';

	type Props = {
		activeCategory: string | null;
		showSavedOnly: boolean;
		showDigestView: boolean;
		theme: 'dark' | 'light';
		onNavigate: (id: string | null) => void;
		onShowSaved: () => void;
		onShowDigest: () => void;
		onToggleTheme: () => void;
	};

	let { activeCategory, showSavedOnly, showDigestView, theme, onNavigate, onShowSaved, onShowDigest, onToggleTheme }: Props = $props();
	let dark = $derived(theme === 'dark');
	let showMenu = $state(false);
	let showFeedback = $state(false);

	let feedActive = $derived(!showSavedOnly && !showDigestView && !showMenu);

	function tabColor(active: boolean) {
		if (active) return dark ? 'text-white' : 'text-black';
		return dark ? 'text-white/40' : 'text-black/40';
	}

	function marker(active: boolean) {
		return active ? (dark ? 'bg-white' : 'bg-black') : 'bg-transparent';
	}

	let rowClass = $derived(
		`flex w-full items-center gap-3 px-3 py-3 text-left ${dark ? 'text-white/70 active:bg-white/[0.05]' : 'text-black/70 active:bg-black/[0.04]'}`
	);
	const tabClass = 'relative flex h-14 min-w-0 flex-1 flex-col items-center justify-center gap-1 transition-colors';
</script>

{#if showMenu}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="fixed inset-0 z-[51] bg-black/60 lg:hidden" onclick={() => (showMenu = false)}></div>
	<div
		class={`fixed inset-x-0 z-[52] border-t px-2 pt-2 lg:hidden ${dark ? 'border-white/10 bg-[#0a0a0a]' : 'border-black/10 bg-[#fafafa]'}`}
		style="bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)); padding-bottom: 0.5rem;"
	>
		<div class="flex items-center justify-between px-3 py-2">
			<p class={`axon-label ${dark ? 'text-white/40' : 'text-black/45'}`}>More</p>
			<button onclick={() => (showMenu = false)} class={`-mr-1 p-1 ${dark ? 'text-white/50' : 'text-black/50'}`} aria-label="Close menu">
				<X class="h-4 w-4" />
			</button>
		</div>

		<NotificationToggle {theme} variant="mobile" />

		<button onclick={() => { onToggleTheme(); showMenu = false; }} class={rowClass}>
			{#if dark}
				<Sun class="h-[18px] w-[18px] shrink-0" />
				<span class="text-[14px] font-medium">Light mode</span>
			{:else}
				<Moon class="h-[18px] w-[18px] shrink-0" />
				<span class="text-[14px] font-medium">Dark mode</span>
			{/if}
		</button>

		<button onclick={() => { showMenu = false; showFeedback = true; }} class={rowClass}>
			<MessageSquare class="h-[18px] w-[18px] shrink-0" />
			<span class="text-[14px] font-medium">Feedback</span>
		</button>

		<button onclick={signOutToHome} class={rowClass}>
			<LogOut class="h-[18px] w-[18px] shrink-0" />
			<span class="text-[14px] font-medium">Sign out</span>
		</button>
	</div>
{/if}

<nav
	class={`fixed inset-x-0 bottom-0 z-40 flex items-stretch justify-around border-t lg:hidden ${dark ? 'border-white/10 bg-[#0a0a0a]' : 'border-black/10 bg-[#fafafa]'}`}
	style="padding-bottom: env(safe-area-inset-bottom, 0px);"
>
	<button onclick={() => { showMenu = false; onNavigate(activeCategory); }} class={`${tabClass} ${tabColor(feedActive)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(feedActive)}`}></span>
		<Home class="h-5 w-5 shrink-0" />
		<span class="axon-label truncate !text-[9px] leading-none">Feed</span>
	</button>

	<button onclick={() => { showMenu = false; onShowSaved(); }} class={`${tabClass} ${tabColor(showSavedOnly && !showMenu)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(showSavedOnly && !showMenu)}`}></span>
		<Bookmark class={`h-5 w-5 shrink-0 ${showSavedOnly ? 'fill-current' : ''}`} />
		<span class="axon-label truncate !text-[9px] leading-none">Saved</span>
	</button>

	<button onclick={() => { showMenu = false; onShowDigest(); }} class={`${tabClass} ${tabColor(showDigestView && !showMenu)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(showDigestView && !showMenu)}`}></span>
		<Sparkles class="h-5 w-5 shrink-0" />
		<span class="axon-label truncate !text-[9px] leading-none">Digest</span>
	</button>

	<button onclick={() => (showMenu = !showMenu)} class={`${tabClass} ${tabColor(showMenu)}`}>
		<span class={`absolute top-0 h-[2px] w-8 ${marker(showMenu)}`}></span>
		<Menu class="h-5 w-5 shrink-0" />
		<span class="axon-label truncate !text-[9px] leading-none">More</span>
	</button>
</nav>

<FeedbackModal bind:show={showFeedback} {theme} />
