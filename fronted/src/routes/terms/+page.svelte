<script lang="ts">
	import { Zap, ArrowLeft } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Terms of Use — AXON</title>
	<meta name="description" content="Terms governing use of the AXON intelligence feed." />
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
		<h1 class="mb-2 text-3xl font-semibold tracking-tight sm:text-4xl">Terms of Use</h1>
		<p class="mb-10 text-sm text-zinc-500 dark:text-[#7B8497]">Last updated: August 25, 2026</p>

		<div class="space-y-8 text-[15px] leading-relaxed text-zinc-700 dark:text-[#A3ADBF]">
			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Agreement</h2>
				<p>
					By accessing or using AXON (the website, app, and related APIs), you agree to these Terms.
					If you do not agree, do not use the service.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">What AXON is</h2>
				<p>
					AXON aggregates publicly available technical and research sources, summarizes them with AI,
					and provides authenticated reading tools (saves, history, article chat, optional push).
					The curation engine and hosted software are proprietary (open-core); see the product license.
					Hosted deployments may have additional operational limits.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Accounts</h2>
				<p>
					You are responsible for your credentials and for activity under your account.
					Provide accurate information and keep your login secure. We may suspend accounts that abuse the service
					(e.g. automated scraping of protected endpoints, spam, or attempts to circumvent rate limits).
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Acceptable use</h2>
				<ul class="list-disc space-y-2 pl-5">
					<li>Do not attempt unauthorized access to other users’ data or admin surfaces.</li>
					<li>Do not use AXON to break the law or to redistribute third-party content in ways that violate their rights.</li>
					<li>Do not overload the API or bypass authentication and internal secrets.</li>
				</ul>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Content &amp; AI output</h2>
				<p>
					Source articles belong to their original publishers. Summaries and chat replies are generated automatically
					and may be incomplete or incorrect — treat them as a starting point, not professional advice.
					Full-text extraction uses readability-style parsing of pages we can fetch; it does not guarantee access to paywalled material.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Availability</h2>
				<p>
					The live demo and APIs are provided as-is, without uptime guarantees.
					Features, sources, and rate limits may change as the project evolves.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Disclaimer of warranty</h2>
				<p>
					AXON is provided “AS IS” without warranties of any kind, express or implied, including merchantability,
					fitness for a particular purpose, and non-infringement, to the fullest extent permitted by law.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Limitation of liability</h2>
				<p>
					To the fullest extent permitted by law, the authors and operators are not liable for any indirect,
					incidental, special, consequential, or punitive damages, or any loss of data, profits, or goodwill,
					arising from your use of AXON.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Privacy</h2>
				<p>
					How we handle personal data is described in our
					<a class="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-[#E8ECF4]" href="/privacy">Privacy Policy</a>.
				</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Changes</h2>
				<p>We may update these Terms. Continued use after changes means you accept the revised Terms.</p>
			</section>

			<section class="space-y-3">
				<h2 class="text-lg font-semibold text-zinc-900 dark:text-[#E8ECF4]">Contact</h2>
				<p>
					Questions:
					<a class="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-[#E8ECF4]" href="https://x.com/BemnetMussa" target="_blank" rel="noopener noreferrer">@BemnetMussa on X</a>
					·
					<a class="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-[#E8ECF4]" href="/privacy">Privacy</a>
				</p>
			</section>
		</div>
	</main>
</div>
