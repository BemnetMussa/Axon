<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/state';
	import type { Article } from '$lib/api';
	import { NAVIGATION } from '$lib/ui';
	import { pulseStore } from '$lib/pulse-store.svelte';
	import FeedPanel from '$lib/components/feed/FeedPanel.svelte';
	import MobileBottomNav from '$lib/components/navigation/MobileBottomNav.svelte';
	import ReaderPanel from '$lib/components/reader/ReaderPanel.svelte';
	import DigestView from '$lib/components/reader/DigestView.svelte';
	import {
		story,
		suggestions,
		chat,
		digest,
		makeStory,
		KEY_SOURCE,
		type PreviewMessage,
		type PreviewScreen
	} from '$lib/preview-content';
	import '$lib/app-shell.css';

	// The app's own screens, rendered at a phone viewport for the landing page's
	// phone mockups (embedded as iframes so every breakpoint resolves as on a phone).

	const SCREENS: PreviewScreen[] = ['feed', 'read', 'ask', 'digest'];
	const param = page.url.searchParams.get('screen') as PreviewScreen;
	const screen: PreviewScreen = SCREENS.includes(param) ? param : 'feed';

	const themeParam = page.url.searchParams.get('theme');
	let theme = $state<'dark' | 'light'>(
		themeParam === 'light' || themeParam === 'dark'
			? themeParam
			: document.documentElement.classList.contains('light')
				? 'light'
				: 'dark'
	);
	let dark = $derived(theme === 'dark');

	let cursor = 3;
	let articles = $state<Article[]>([makeStory(0, 4), makeStory(1, 22), makeStory(2, 51)]);
	let newArticleIds = $state<Set<number>>(new Set());
	let keepable = $derived(Object.keys(KEY_SOURCE).filter((k) => !articles.some((a) => a.source === KEY_SOURCE[k])));
	let feedScrollArea = $state<HTMLDivElement | undefined>();
	let readerHost = $state<HTMLDivElement | undefined>();

	const noop = () => {};

	function post(message: PreviewMessage) {
		if (window.parent !== window) window.parent.postMessage(message, location.origin);
	}

	function keep(key: string) {
		const article = makeStory(cursor++, 0, key);
		articles = [article, ...articles].slice(0, 6);
		newArticleIds = new Set([article.id, ...[...newArticleIds].slice(0, 1)]);
	}

	$effect(() => {
		document.documentElement.classList.toggle('light', theme === 'light');
	});

	$effect(() => {
		if (screen === 'feed') post({ type: 'axon-preview:keepable', keys: keepable });
	});

	onMount(() => {
		const onMessage = (event: MessageEvent<PreviewMessage>) => {
			if (event.origin !== location.origin) return;
			const msg = event.data;
			if (msg?.type === 'axon-preview:keep') keep(msg.key);
			else if (msg?.type === 'axon-preview:theme') theme = msg.theme;
			else if (msg?.type === 'axon-preview:pulse') pulseStore.set(msg.pulse);
		};
		document.body.classList.add('app-shell-lock');
		window.addEventListener('message', onMessage);
		post({ type: 'axon-preview:ready' });

		// The reader scrolls to its chat on open; the Read screen should rest on the headline.
		let timer: ReturnType<typeof setTimeout> | undefined;
		if (screen === 'read') {
			timer = setTimeout(async () => {
				await tick();
				readerHost?.querySelectorAll<HTMLElement>('.overflow-y-auto').forEach((el) => el.scrollTo({ top: 0, behavior: 'instant' }));
			}, 700);
		}

		return () => {
			document.body.classList.remove('app-shell-lock');
			window.removeEventListener('message', onMessage);
			clearTimeout(timer);
		};
	});
</script>

<svelte:head>
	<title>AXON — preview</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<div class={`preview relative flex h-screen overflow-hidden ${dark ? 'bg-[#0a0a0a] text-[#ededed]' : 'bg-[#fafafa] text-[#0a0a0a]'}`}>
	<div class="mx-auto flex h-full w-full max-w-[1600px] min-w-0 overflow-hidden">
		<div class="relative flex min-w-0 flex-1 overflow-hidden">
			<div class="flex min-w-0 flex-1 overflow-hidden">
				<div class={`flex min-w-0 flex-1 flex-col overflow-hidden ${dark ? 'bg-[#0a0a0a]' : 'bg-[#fafafa]'}`}>
					<FeedPanel
						title="Frontier"
						{articles}
						dbEmpty={false}
						searchQuery=""
						{theme}
						hasMore={false}
						loadingMore={false}
						selectedArticleId={null}
						savedArticleIds={[]}
						readArticleIds={new Set()}
						loading={false}
						syncIndicator={false}
						{newArticleIds}
						tabs={NAVIGATION}
						activeTab={null}
						showSavedOnly={false}
						onTabSelect={noop}
						onSearchChange={noop}
						onArticleOpen={noop}
						onToggleSave={noop}
						onLoadMore={noop}
						bind:scrollArea={feedScrollArea}
					/>
				</div>
			</div>

			{#if screen !== 'feed'}
				<div bind:this={readerHost} class={`absolute inset-0 z-30 flex overflow-hidden ${dark ? 'bg-[#0a0a0a]' : 'bg-white'}`}>
					{#if screen === 'digest'}
						<DigestView {digest} loading={false} {theme} onBack={noop} onGenerate={noop} />
					{:else}
						<ReaderPanel
							article={story}
							isSaved={screen === 'ask'}
							chatMessages={screen === 'ask' ? chat : []}
							chatInput=""
							chatLoading={false}
							{theme}
							{suggestions}
							onBack={noop}
							onToggleSave={noop}
							onOpenExternal={noop}
							onChatInputChange={noop}
							onSendChat={noop}
						/>
					{/if}
				</div>
			{/if}
		</div>

		{#if screen === 'feed' || screen === 'digest'}
			<MobileBottomNav
				activeCategory={null}
				showSavedOnly={false}
				showDigestView={screen === 'digest'}
				{theme}
				onNavigate={noop}
				onShowSaved={noop}
				onShowDigest={noop}
				onToggleTheme={noop}
			/>
		{/if}
	</div>
</div>

<style>
	/* Feed rows are absolutely positioned by VirtualFeed; ease them when a story is prepended. */
	.preview :global([style*='position: absolute'][style*='top:']) {
		transition: top 900ms cubic-bezier(0.22, 1, 0.36, 1);
		animation: preview-row-in 900ms cubic-bezier(0.22, 1, 0.36, 1);
	}
	@keyframes preview-row-in {
		from {
			opacity: 0;
			transform: translateY(-18px);
		}
	}
</style>
