<script lang="ts">
	import { Zap, ArrowLeft } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Privacy Policy — AXON</title>
	<meta name="description" content="How AXON collects, uses, and protects your data." />
	<meta name="robots" content="index,follow" />
</svelte:head>

<div class="min-h-screen bg-white dark:bg-[#0B0F17] text-zinc-900 dark:text-[#E8ECF4] antialiased">
	<header class="border-b border-zinc-200 dark:border-[#242E43]">
		<div class="mx-auto flex max-w-3xl items-center justify-between px-5 py-5 sm:px-8">
			<a href="/" class="flex items-center gap-2 text-sm font-semibold tracking-wide">
				<span class="flex h-7 w-7 items-center justify-center rounded-md bg-black text-white dark:bg-white dark:text-black">
					<Zap class="h-3.5 w-3.5 fill-current" />
				</span>
				AXON
			</a>
			<a href="/" class="inline-flex items-center gap-1.5 text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-[#7B8497] dark:hover:text-[#E8ECF4]">
				<ArrowLeft class="h-4 w-4" /> Home
			</a>
		</div>
	</header>

	<main class="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
		<p class="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500 dark:text-[#7B8497]">Legal</p>
		<h1 class="mb-2 text-3xl font-semibold tracking-tight sm:text-4xl">Privacy Policy</h1>
		<p class="mb-10 text-sm text-zinc-500 dark:text-[#7B8497]">Last updated: August 25, 2026</p>

		<div class="space-y-8 text-[15px] leading-relaxed text-zinc-700 dark:text-[#A3ADBF]">
			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Who we are</h2>
				<p>
					AXON (“we”, “us”) is an open-source OSINT intelligence feed operated by Bemnet Mussa.
					This policy explains what we collect when you use the website and app, and why.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Information we collect</h2>
				<ul class="list-disc space-y-2 pl-5">
					<li><span class="text-zinc-900 dark:text-[#E8ECF4]">Account data</span> — email, name (if provided), and authentication identifiers when you sign up with email/password or Google OAuth.</li>
					<li><span class="text-zinc-900 dark:text-[#E8ECF4]">Product usage</span> — saved articles, reading history, feedback you submit, and optional Web Push subscription endpoints if you enable notifications.</li>
					<li><span class="text-zinc-900 dark:text-[#E8ECF4]">Technical logs</span> — basic request metadata (timestamps, paths, error codes) needed to run and secure the service.</li>
					<li><span class="text-zinc-900 dark:text-[#E8ECF4]">Analytics (optional)</span> — if PostHog is configured for a deployment, we may collect anonymized or identified product events (e.g. opens, searches, saves).</li>
				</ul>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">How we use it</h2>
				<p>We use this information to authenticate you, sync your reading state across devices, improve the feed, send optional push notifications you enable, and keep the service reliable and secure.</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Third parties</h2>
				<ul class="list-disc space-y-2 pl-5">
					<li>Google — if you choose “Sign in with Google.”</li>
					<li>Groq — to generate article insights and chat replies from public source content you ask about.</li>
					<li>Hosting / database providers used for the live deployment (e.g. Vercel, Postgres hosts).</li>
					<li>PostHog — only when an analytics key is configured.</li>
				</ul>
				<p>We do not sell your personal information.</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Retention &amp; deletion</h2>
				<p>
					We keep account and product data while your account is active. You can request deletion of your account data by contacting
					<a class="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-[#E8ECF4]" href="https://x.com/BemnetMussa" target="_blank" rel="noopener noreferrer">@BemnetMussa</a>
					or opening a GitHub issue on the project repository.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Security</h2>
				<p>Access between the web app and API is gated by shared internal secrets and authenticated sessions. No method of transmission or storage is perfectly secure; we take reasonable steps to protect your data.</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Children</h2>
				<p>AXON is not directed at children under 13, and we do not knowingly collect personal information from them.</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Changes</h2>
				<p>We may update this policy as the product evolves. The “Last updated” date at the top will change when we do.</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Contact</h2>
				<p>
					Questions about privacy:
					<a class="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-[#E8ECF4]" href="https://x.com/BemnetMussa" target="_blank" rel="noopener noreferrer">@BemnetMussa on X</a>
					·
					<a class="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-[#E8ECF4]" href="/terms">Terms of Use</a>
				</p>
			</section>
		</div>
	</main>
</div>
