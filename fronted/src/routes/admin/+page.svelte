<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type AdminStats } from '$lib/api';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let stats = $state<AdminStats | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let lastUpdated = $state<Date | null>(null);
	let copied = $state(false);

	// One busy/result slot per manual action.
	let actionBusy = $state<string | null>(null);
	let actionResult = $state<string | null>(null);

	const POLL_MS = 30_000;

	async function fetchStats() {
		try {
			stats = await api.getAdminStats();
			error = null;
			lastUpdated = new Date();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load stats';
		} finally {
			loading = false;
		}
	}

	async function runAction(name: string, fn: () => Promise<unknown>, describe: (r: any) => string) {
		actionBusy = name;
		actionResult = null;
		try {
			const r = await fn();
			actionResult = `${name}: ${describe(r)}`;
			await fetchStats();
		} catch (e) {
			actionResult = `${name} failed: ${e instanceof Error ? e.message : 'error'}`;
		} finally {
			actionBusy = null;
		}
	}

	onMount(() => {
		if (!data.isAdmin) {
			loading = false;
			return;
		}
		fetchStats();
		const id = setInterval(fetchStats, POLL_MS);
		return () => clearInterval(id);
	});

	function copyId() {
		navigator.clipboard?.writeText(data.userId).then(() => {
			copied = true;
			setTimeout(() => (copied = false), 1500);
		});
	}

	// --- formatting helpers ---
	function fmtNum(n: number | null | undefined): string {
		return (n ?? 0).toLocaleString();
	}

	function fmtAgo(iso: string | null): string {
		if (!iso) return '—';
		const then = new Date(iso).getTime();
		if (Number.isNaN(then)) return '—';
		const secs = Math.round((Date.now() - then) / 1000);
		const ago = secs >= 0;
		const a = Math.abs(secs);
		let out: string;
		if (a < 60) out = `${a}s`;
		else if (a < 3600) out = `${Math.floor(a / 60)}m`;
		else if (a < 86400) out = `${Math.floor(a / 3600)}h`;
		else out = `${Math.floor(a / 86400)}d`;
		return ago ? `${out} ago` : `in ${out}`;
	}

	// Heuristic per-source freshness color (sources publish at different cadences,
	// so treat this as a glance signal, not an SLA).
	function staleClass(hours: number | null): string {
		if (hours === null) return 'text-zinc-600';
		if (hours <= 24) return 'text-emerald-400';
		if (hours <= 72) return 'text-amber-400';
		return 'text-red-400';
	}

	// Overall system status rolled up from the most severe signal.
	type Level = 'ok' | 'warn' | 'down';
	const health = $derived.by((): { level: Level; label: string; reasons: string[] } => {
		if (!stats) return { level: 'warn', label: 'Loading', reasons: [] };
		const reasons: string[] = [];
		let level: Level = 'ok';
		const bump = (l: Level) => {
			if (l === 'down') level = 'down';
			else if (l === 'warn' && level !== 'down') level = 'warn';
		};

		const sch = stats.scheduler;
		const li = stats.last_scheduled_ingest;
		if (!sch.ap_scheduler_running) {
			reasons.push('Scheduler is not running — ingestion will not fire on its own.');
			bump('down');
		}
		if (li.ok === false) {
			reasons.push(`Last scheduled ingest failed${li.detail ? `: ${li.detail}` : ''}`);
			bump('down');
		}
		if (stats.totals.missing_insight > 0) {
			reasons.push(`${stats.totals.missing_insight} articles missing an AI insight (check GROQ_API_KEY).`);
			bump('warn');
		}
		if (stats.totals.unprocessed > 0) {
			reasons.push(`${stats.totals.unprocessed} unprocessed articles in the pipeline.`);
			bump('warn');
		}
		const stale = stats.sources.filter((s) => (s.hours_since_latest ?? 0) > 72);
		if (stale.length) {
			reasons.push(`${stale.length} source(s) have no item in 3+ days: ${stale.map((s) => s.source).join(', ')}`);
			bump('warn');
		}

		const label = level === 'ok' ? 'Healthy' : level === 'warn' ? 'Degraded' : 'Down';
		return { level, label, reasons };
	});

	const dot = { ok: 'bg-emerald-400', warn: 'bg-amber-400', down: 'bg-red-400' } as const;
	const dotGlow = { ok: 'shadow-emerald-400/50', warn: 'shadow-amber-400/50', down: 'shadow-red-400/50' } as const;

	const maxVolume = $derived(Math.max(1, ...(stats?.daily_volume.map((d) => d.count) ?? [1])));
</script>

<svelte:head><title>Axon · Admin</title></svelte:head>

<div class="min-h-screen bg-[#0a0a0a] text-zinc-200">
	{#if !data.isAdmin}
		<!-- First-run setup only (allow-list empty). Surfaces the owner's user ID so
		     they can configure AXON_ADMIN_USER_IDS. Once set, non-admins get a 404. -->
		<div class="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6 text-center">
			<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-2xl">🔧</div>
			<h1 class="text-lg font-semibold text-white">Admin setup</h1>
			<p class="mt-2 text-[13px] leading-relaxed text-zinc-500">
				The admin dashboard isn't configured yet. Add the ID below to
				<code class="rounded bg-white/[0.06] px-1 py-0.5 text-[11px] text-zinc-300">AXON_ADMIN_USER_IDS</code>
				on <strong>both</strong> the frontend and backend, restart the server, then reload.
			</p>
			<button
				onclick={copyId}
				class="mt-4 w-full break-all rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 font-mono text-[12px] text-zinc-300 transition-colors hover:border-white/20"
			>
				{data.userId}
				<span class="ml-2 text-[10px] uppercase tracking-wide text-zinc-600">{copied ? 'copied' : 'tap to copy'}</span>
			</button>
			<a href="/app" class="mt-6 text-[12px] text-zinc-600 underline underline-offset-2 hover:text-zinc-400">← Back to app</a>
		</div>
	{:else}
		<div class="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-8">
			<!-- Header / status banner -->
			<header class="mb-6 flex flex-wrap items-center justify-between gap-3">
				<div class="flex items-center gap-3">
					<span class="relative flex h-3 w-3">
						{#if health.level === 'ok'}
							<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400/40"></span>
						{/if}
						<span class="relative inline-flex h-3 w-3 rounded-full shadow-lg {dot[health.level]} {dotGlow[health.level]}"></span>
					</span>
					<div>
						<h1 class="text-[15px] font-semibold text-white">Axon · System {health.label}</h1>
						<p class="text-[11px] text-zinc-600">
							{#if lastUpdated}Updated {lastUpdated.toLocaleTimeString()} · auto every 30s{:else}Loading…{/if}
						</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					<button
						onclick={fetchStats}
						class="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[12px] text-zinc-300 transition-colors hover:border-white/20"
					>Refresh</button>
					<a href="/app" class="rounded-lg border border-white/10 px-3 py-1.5 text-[12px] text-zinc-500 transition-colors hover:text-zinc-300">App ↗</a>
				</div>
			</header>

			{#if error}
				<div class="mb-6 rounded-lg border border-red-500/30 bg-red-500/[0.06] px-4 py-3 text-[12px] text-red-300">{error}</div>
			{/if}

			{#if health.reasons.length}
				<div class="mb-6 rounded-xl border {health.level === 'down' ? 'border-red-500/30 bg-red-500/[0.05]' : 'border-amber-500/30 bg-amber-500/[0.05]'} px-4 py-3">
					<ul class="space-y-1 text-[12px] {health.level === 'down' ? 'text-red-300' : 'text-amber-300'}">
						{#each health.reasons as r}<li>• {r}</li>{/each}
					</ul>
				</div>
			{/if}

			{#if stats}
				<!-- Scheduler + pipeline cards -->
				<div class="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
					{#snippet stat(label: string, value: string, sub: string = '')}
						<div class="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
							<p class="text-[11px] uppercase tracking-wide text-zinc-600">{label}</p>
							<p class="mt-1 text-xl font-semibold text-white">{value}</p>
							{#if sub}<p class="mt-0.5 text-[11px] text-zinc-600">{sub}</p>{/if}
						</div>
					{/snippet}
					{@render stat('Scheduler', stats.scheduler.ap_scheduler_running ? 'Running' : 'Stopped', `every ${stats.scheduler.interval_hours}h · next ${fmtAgo(stats.scheduler.next_run_at_utc)}`)}
					{@render stat('Last ingest', stats.last_scheduled_ingest.relative ?? '—', stats.last_scheduled_ingest.ok === false ? 'failed' : (stats.last_scheduled_ingest.detail ?? 'ok'))}
					{@render stat('Articles', fmtNum(stats.totals.articles), `${fmtNum(stats.totals.unprocessed)} unprocessed`)}
					{@render stat('Missing insight', fmtNum(stats.totals.missing_insight), 'AI step pending/failed')}
				</div>

				<!-- Manual actions -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Actions</h2>
					<div class="flex flex-wrap gap-2">
						<button
							disabled={actionBusy !== null}
							onclick={() => runAction('Ingest', () => api.adminRunIngest(true), (r) => r.status === 'skipped' ? (r.reason ?? 'skipped') : `${r.new_articles ?? 0} new`)}
							class="rounded-lg border border-emerald-500/30 bg-emerald-500/[0.08] px-3 py-1.5 text-[12px] font-medium text-emerald-300 transition-colors hover:bg-emerald-500/15 disabled:opacity-40"
						>{actionBusy === 'Ingest' ? 'Running…' : 'Run ingest now'}</button>
						<button
							disabled={actionBusy !== null}
							onclick={() => runAction('Analyze', () => api.adminRunAnalyze(), (r) => `${r.processed ?? 0} processed`)}
							class="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-zinc-300 transition-colors hover:border-white/20 disabled:opacity-40"
						>{actionBusy === 'Analyze' ? 'Running…' : 'Run analyze'}</button>
						<button
							disabled={actionBusy !== null}
							onclick={() => runAction('Retry insights', () => api.adminRetryInsights(), (r) => `${r.retried ?? 0} retried`)}
							class="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-zinc-300 transition-colors hover:border-white/20 disabled:opacity-40"
						>{actionBusy === 'Retry insights' ? 'Running…' : 'Retry failed insights'}</button>
					</div>
					{#if actionResult}<p class="mt-3 text-[12px] text-zinc-400">{actionResult}</p>{/if}
				</section>

				<!-- Daily volume sparkline -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Articles / day (14d)</h2>
					{#if stats.daily_volume.length}
						<div class="flex h-24 items-end gap-1">
							{#each stats.daily_volume as d}
								<div class="group relative flex flex-1 flex-col items-center justify-end">
									<div
										class="w-full rounded-sm bg-emerald-500/40 transition-colors group-hover:bg-emerald-400/70"
										style="height: {Math.max(4, (d.count / maxVolume) * 88)}px"
									></div>
									<span class="pointer-events-none absolute -top-5 hidden rounded bg-black px-1.5 py-0.5 text-[10px] text-zinc-300 group-hover:block">{d.count}</span>
								</div>
							{/each}
						</div>
						<div class="mt-2 flex justify-between text-[10px] text-zinc-600">
							<span>{stats.daily_volume[0]?.day}</span>
							<span>{stats.daily_volume[stats.daily_volume.length - 1]?.day}</span>
						</div>
					{:else}
						<p class="text-[12px] text-zinc-600">No articles in the last 14 days.</p>
					{/if}
				</section>

				<!-- Per-source health -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Source health <span class="font-normal normal-case text-zinc-600">· stalest first</span></h2>
					<div class="overflow-x-auto">
						<table class="w-full text-left text-[12px]">
							<thead class="text-[10px] uppercase tracking-wide text-zinc-600">
								<tr class="border-b border-white/[0.06]">
									<th class="py-2 pr-3 font-medium">Source</th>
									<th class="py-2 pr-3 text-right font-medium">Latest</th>
									<th class="py-2 pr-3 text-right font-medium">24h</th>
									<th class="py-2 pr-3 text-right font-medium">7d</th>
									<th class="py-2 pr-3 text-right font-medium">Total</th>
									<th class="py-2 text-right font-medium">No insight</th>
								</tr>
							</thead>
							<tbody>
								{#each stats.sources as s}
									<tr class="border-b border-white/[0.03]">
										<td class="py-2 pr-3 font-medium text-zinc-300">{s.source}</td>
										<td class="py-2 pr-3 text-right {staleClass(s.hours_since_latest)}">{fmtAgo(s.latest_published)}</td>
										<td class="py-2 pr-3 text-right text-zinc-400">{s.last_24h}</td>
										<td class="py-2 pr-3 text-right text-zinc-400">{s.last_7d}</td>
										<td class="py-2 pr-3 text-right text-zinc-500">{fmtNum(s.total)}</td>
										<td class="py-2 text-right {s.missing_insight ? 'text-amber-400' : 'text-zinc-600'}">{s.missing_insight}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</section>

				<!-- Engagement + feedback -->
				<section class="grid gap-3 sm:grid-cols-2">
					<div class="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
						<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Engagement</h2>
						<div class="grid grid-cols-2 gap-3">
							<div><p class="text-lg font-semibold text-white">{fmtNum(stats.engagement.total_views)}</p><p class="text-[11px] text-zinc-600">total views</p></div>
							<div><p class="text-lg font-semibold text-white">{fmtNum(stats.engagement.total_likes)}</p><p class="text-[11px] text-zinc-600">total likes</p></div>
							<div><p class="text-lg font-semibold text-white">{stats.engagement.avg_feedback_rating ?? '—'}</p><p class="text-[11px] text-zinc-600">avg rating ({stats.engagement.feedback_count})</p></div>
							<div><p class="text-lg font-semibold text-white">{fmtNum(stats.totals.trends)}</p><p class="text-[11px] text-zinc-600">trend rows</p></div>
						</div>
					</div>
					<div class="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
						<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Recent feedback</h2>
						{#if stats.engagement.recent_feedback.length}
							<ul class="space-y-2">
								{#each stats.engagement.recent_feedback as f}
									<li class="flex items-start gap-2 text-[12px]">
										<span class="shrink-0 text-amber-400">{'★'.repeat(f.rating)}<span class="text-zinc-700">{'★'.repeat(5 - f.rating)}</span></span>
										<span class="min-w-0 flex-1 text-zinc-400">{f.comment || '—'}</span>
										<span class="shrink-0 text-[10px] text-zinc-600">{fmtAgo(f.created_at)}</span>
									</li>
								{/each}
							</ul>
						{:else}
							<p class="text-[12px] text-zinc-600">No feedback yet.</p>
						{/if}
					</div>
				</section>
			{:else if loading}
				<p class="py-20 text-center text-[13px] text-zinc-600">Loading system stats…</p>
			{/if}
		</div>
	{/if}
</div>
