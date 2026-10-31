<script lang="ts">
	import { onMount } from 'svelte';
	import { enhance } from '$app/forms';
	import { api, type AdminStats } from '$lib/api';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let stats = $state<AdminStats | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let lastUpdated = $state<Date | null>(null);
	let copied = $state(false);
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
			actionResult = `${name}: ${describe(await fn())}`;
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

	// --- formatting ---
	const fmtNum = (n: number | null | undefined) => (n ?? 0).toLocaleString();

	function fmtAgo(iso: string | null): string {
		if (!iso) return '—';
		const then = new Date(iso).getTime();
		if (Number.isNaN(then)) return '—';
		const secs = Math.round((Date.now() - then) / 1000);
		const a = Math.abs(secs);
		let out: string;
		if (a < 60) out = `${a}s`;
		else if (a < 3600) out = `${Math.floor(a / 60)}m`;
		else if (a < 86400) out = `${Math.floor(a / 3600)}h`;
		else out = `${Math.floor(a / 86400)}d`;
		return secs >= 0 ? `${out} ago` : `in ${out}`;
	}

	function staleClass(hours: number | null): string {
		if (hours === null) return 'text-zinc-600';
		if (hours <= 24) return 'text-emerald-400';
		if (hours <= 120) return 'text-amber-400';
		return 'text-red-400';
	}

	function uaShort(ua: string | null): string {
		if (!ua) return 'unknown';
		const b = /Edg/.test(ua) ? 'Edge' : /Chrome/.test(ua) ? 'Chrome' : /Firefox/.test(ua) ? 'Firefox' : /Safari/.test(ua) ? 'Safari' : 'Browser';
		const os = /Windows/.test(ua) ? 'Windows' : /Android/.test(ua) ? 'Android' : /iPhone|iPad/.test(ua) ? 'iOS' : /Mac OS X|Macintosh/.test(ua) ? 'macOS' : /Linux/.test(ua) ? 'Linux' : '';
		return os ? `${b} · ${os}` : b;
	}

	type Level = 'ok' | 'warn' | 'down';
	const health = $derived.by((): { level: Level; label: string; reasons: string[] } => {
		if (!stats) return { level: 'warn', label: 'Loading', reasons: [] };
		const reasons: string[] = [];
		let level: Level = 'ok';
		const bump = (l: Level) => {
			if (l === 'down') level = 'down';
			else if (l === 'warn' && level !== 'down') level = 'warn';
		};

		if (!stats.ai.reachable) {
			reasons.push(
				stats.ai.key_present
					? `AI engine unreachable — insights can't generate: ${stats.ai.error}${stats.ai_last_error ? ` · last error: ${stats.ai_last_error}` : ''}`
					: 'GROQ_API_KEY is not set — AI insights are disabled.',
			);
			bump('down');
		}
		if (!stats.scheduler.ap_scheduler_running) {
			reasons.push('Scheduler is not running — ingestion will not fire on its own.');
			bump('down');
		}
		if (stats.last_scheduled_ingest.ok === false) {
			reasons.push(`Last scheduled ingest failed${stats.last_scheduled_ingest.detail ? `: ${stats.last_scheduled_ingest.detail}` : ''}`);
			bump('down');
		}
		if (stats.totals.missing_insight > 0) {
			reasons.push(`${stats.totals.missing_insight.toLocaleString()} articles missing an AI insight — run Process backlog.`);
			bump('warn');
		}
		const dead = Object.entries(stats.fetch_report?.sources ?? {}).filter(([, v]) => v.raw === 0).map(([k]) => k);
		if (stats.fetch_report?.at && dead.length) {
			reasons.push(`Last fetch returned nothing from: ${dead.join(', ')}`);
			bump('warn');
		}

		const label = level === 'ok' ? 'Healthy' : level === 'warn' ? 'Degraded' : 'Down';
		return { level, label, reasons };
	});

	const dot = { ok: 'bg-emerald-400', warn: 'bg-amber-400', down: 'bg-red-400' } as const;
	const glow = { ok: 'shadow-emerald-400/50', warn: 'shadow-amber-400/50', down: 'shadow-red-400/50' } as const;

	const maxVolume = $derived(Math.max(1, ...(stats?.daily_volume.map((d) => d.count) ?? [1])));
	const procPct = $derived(stats?.processing?.total ? Math.round((stats.processing.done / stats.processing.total) * 100) : 0);
</script>

<svelte:head><title>Axon · Admin</title></svelte:head>

<div class="min-h-screen bg-[#0a0a0a] text-zinc-200">
	{#if !data.isAdmin}
		<div class="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6 text-center">
			<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-2xl">🔧</div>
			<h1 class="text-lg font-semibold text-white">Admin setup</h1>
			<p class="mt-2 text-[13px] leading-relaxed text-zinc-500">
				The admin dashboard isn't configured yet. Add the ID below to
				<code class="rounded bg-white/[0.06] px-1 py-0.5 text-[11px] text-zinc-300">AXON_ADMIN_USER_IDS</code>
				on <strong>both</strong> the frontend and backend, restart the server, then reload.
			</p>
			<button onclick={copyId} class="mt-4 w-full break-all rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 font-mono text-[12px] text-zinc-300 transition-colors hover:border-white/20">
				{data.userId}
				<span class="ml-2 text-[10px] uppercase tracking-wide text-zinc-600">{copied ? 'copied' : 'tap to copy'}</span>
			</button>
			<a href="/app" class="mt-6 text-[12px] text-zinc-600 underline underline-offset-2 hover:text-zinc-400">← Back to app</a>
		</div>
	{:else}
		<div class="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-8">
			<header class="mb-6 flex flex-wrap items-center justify-between gap-3">
				<div class="flex items-center gap-3">
					<span class="relative flex h-3 w-3">
						{#if health.level === 'ok'}<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400/40"></span>{/if}
						<span class="relative inline-flex h-3 w-3 rounded-full shadow-lg {dot[health.level]} {glow[health.level]}"></span>
					</span>
					<div>
						<h1 class="text-[15px] font-semibold text-white">Axon · System {health.label}</h1>
						<p class="text-[11px] text-zinc-600">{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()} · auto every 30s` : 'Loading…'}</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					<button onclick={fetchStats} class="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[12px] text-zinc-300 transition-colors hover:border-white/20">Refresh</button>
					<a href="/app" class="rounded-lg border border-white/10 px-3 py-1.5 text-[12px] text-zinc-500 transition-colors hover:text-zinc-300">App ↗</a>
				</div>
			</header>

			{#if form?.message}
				<div class="mb-4 rounded-lg border {form.success ? 'border-emerald-500/30 bg-emerald-500/[0.06] text-emerald-300' : 'border-red-500/30 bg-red-500/[0.06] text-red-300'} px-4 py-2.5 text-[12px]">{form.message}</div>
			{/if}
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
				<!-- Top cards -->
				<div class="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
					{#snippet card(label: string, value: string, sub: string, accent: string = 'text-white')}
						<div class="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
							<p class="text-[11px] uppercase tracking-wide text-zinc-600">{label}</p>
							<p class="mt-1 text-xl font-semibold {accent}">{value}</p>
							<p class="mt-0.5 text-[11px] text-zinc-600">{sub}</p>
						</div>
					{/snippet}
					{@render card('AI engine', stats.ai.reachable ? 'Online' : stats.ai.key_present ? 'Error' : 'No key', stats.ai.reachable ? 'Groq reachable' : (stats.ai_last_error ?? stats.ai.error ?? 'set GROQ_API_KEY'), stats.ai.reachable ? 'text-emerald-400' : 'text-red-400')}
					{@render card('Scheduler', stats.scheduler.ap_scheduler_running ? 'Running' : 'Stopped', `every ${stats.scheduler.interval_hours}h · next ${fmtAgo(stats.scheduler.next_run_at_utc)}`, stats.scheduler.ap_scheduler_running ? 'text-emerald-400' : 'text-red-400')}
					{@render card('Last ingest', stats.last_scheduled_ingest.relative ?? '—', stats.last_scheduled_ingest.ok === false ? 'failed' : (stats.last_scheduled_ingest.detail ?? 'ok'))}
					{@render card('Backlog', fmtNum(stats.totals.unprocessed + stats.totals.missing_insight), `${fmtNum(stats.totals.unprocessed)} unprocessed · ${fmtNum(stats.totals.missing_insight)} no insight`, (stats.totals.unprocessed + stats.totals.missing_insight) ? 'text-amber-400' : 'text-emerald-400')}
				</div>

				<!-- Pipeline control -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<div class="mb-3 flex flex-wrap items-center justify-between gap-2">
						<h2 class="text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Pipeline control</h2>
						{#if stats.processing.running}
							<span class="text-[11px] text-amber-400">{stats.processing.phase} · {stats.processing.done}/{stats.processing.total}</span>
						{:else if stats.processing.result}
							<span class="text-[11px] text-zinc-500">last run: {stats.processing.result}</span>
						{/if}
					</div>

					{#if stats.processing.running}
						<div class="mb-3 h-2 w-full overflow-hidden rounded-full bg-white/[0.05]">
							<div class="h-full rounded-full bg-emerald-500/70 transition-all" style="width: {procPct}%"></div>
						</div>
					{/if}

					<div class="flex flex-wrap gap-2">
						<button
							disabled={actionBusy !== null}
							onclick={() => runAction('Ingest', () => api.adminRunIngest(true), (r) => (r.status === 'skipped' ? (r.reason ?? 'skipped') : `${r.new_articles ?? 0} new`))}
							class="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-zinc-300 transition-colors hover:border-white/20 disabled:opacity-40"
						>{actionBusy === 'Ingest' ? 'Running…' : 'Run ingest now'}</button>
						<button
							disabled={actionBusy !== null || stats.processing.running}
							onclick={() => runAction('Process', () => api.adminProcessBacklog(), (r) => (r.status === 'already_running' ? 'already running' : 'started in background'))}
							class="rounded-lg border border-emerald-500/30 bg-emerald-500/[0.08] px-3 py-1.5 text-[12px] font-medium text-emerald-300 transition-colors hover:bg-emerald-500/15 disabled:opacity-40"
						>{stats.processing.running ? 'Processing…' : 'Process backlog (analyze + retry)'}</button>
					</div>
					{#if actionResult}<p class="mt-3 text-[12px] text-zinc-400">{actionResult}</p>{/if}
					{#if !stats.ai.reachable}<p class="mt-2 text-[11px] text-red-400/80">Note: AI engine is offline — processing won't generate insights until GROQ_API_KEY works.</p>{/if}
				</section>

				<!-- Fetch report: the source-of-truth on "is each source being fetched" -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-1 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Last fetch run</h2>
					<p class="mb-3 text-[11px] text-zinc-600">{stats.fetch_report?.at ? `${fmtAgo(stats.fetch_report.at)} · ${stats.fetch_report.ingested} ingested of ${stats.fetch_report.raw} found` : 'No ingest run recorded yet this process.'}</p>
					{#if stats.fetch_report?.at && Object.keys(stats.fetch_report.sources).length}
						<div class="flex flex-wrap gap-1.5">
							{#each Object.entries(stats.fetch_report.sources) as [src, v]}
								<span class="rounded-md border px-2 py-1 text-[11px] {v.raw === 0 ? 'border-red-500/30 bg-red-500/[0.06] text-red-300' : 'border-white/[0.06] bg-white/[0.02] text-zinc-400'}">{src} <span class="text-zinc-600">·</span> {v.ingested}/{v.raw}</span>
							{/each}
						</div>
						<p class="mt-2 text-[10px] text-zinc-600">ingested/found per source. Red = returned nothing last run (rate-limited or dead feed).</p>
					{/if}
				</section>

				<!-- Ingest history (persisted — survives restarts) -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Ingest history <span class="font-normal normal-case text-zinc-600">· last {stats.recent_runs.length} runs</span></h2>
					{#if stats.recent_runs.length}
						<div class="overflow-x-auto">
							<table class="w-full text-left text-[12px]">
								<thead class="text-[10px] uppercase tracking-wide text-zinc-600">
									<tr class="border-b border-white/[0.06]">
										<th class="py-2 pr-3 font-medium">When</th>
										<th class="py-2 pr-3 font-medium">Trigger</th>
										<th class="py-2 pr-3 text-right font-medium">New</th>
										<th class="py-2 pr-3 text-right font-medium">Analyzed</th>
										<th class="py-2 pr-3 text-right font-medium">Found</th>
										<th class="py-2 text-right font-medium">Status</th>
									</tr>
								</thead>
								<tbody>
									{#each stats.recent_runs as r}
										<tr class="border-b border-white/[0.03]">
											<td class="py-2 pr-3 text-zinc-400">{fmtAgo(r.started_at)}</td>
											<td class="py-2 pr-3 text-zinc-500">{r.trigger}</td>
											<td class="py-2 pr-3 text-right text-zinc-300">{r.new_articles}</td>
											<td class="py-2 pr-3 text-right text-zinc-400">{r.analyzed}</td>
											<td class="py-2 pr-3 text-right text-zinc-600">{r.raw_found}</td>
											<td class="py-2 text-right">{#if r.ok}<span class="text-emerald-400">ok</span>{:else}<span class="text-red-400" title={r.detail ?? ''}>failed</span>{/if}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{:else}<p class="text-[12px] text-zinc-600">No runs recorded yet. They'll appear here after the next ingest.</p>{/if}
				</section>

				<!-- Volume -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Articles / day (14d)</h2>
					{#if stats.daily_volume.length}
						<div class="flex h-24 items-end gap-1">
							{#each stats.daily_volume as d}
								<div class="group relative flex flex-1 flex-col items-center justify-end">
									<div class="w-full rounded-sm bg-emerald-500/40 transition-colors group-hover:bg-emerald-400/70" style="height: {Math.max(4, (d.count / maxVolume) * 88)}px"></div>
									<span class="pointer-events-none absolute -top-5 hidden rounded bg-black px-1.5 py-0.5 text-[10px] text-zinc-300 group-hover:block">{d.count}</span>
								</div>
							{/each}
						</div>
						<div class="mt-2 flex justify-between text-[10px] text-zinc-600">
							<span>{stats.daily_volume[0]?.day}</span><span>{stats.daily_volume[stats.daily_volume.length - 1]?.day}</span>
						</div>
					{:else}<p class="text-[12px] text-zinc-600">No articles in the last 14 days.</p>{/if}
				</section>

				<!-- Source health (publish freshness) -->
				<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
					<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Source health <span class="font-normal normal-case text-zinc-600">· stalest first · low-cadence blogs going days without a post is normal</span></h2>
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

				<!-- Engagement -->
				<section class="mb-6 grid gap-3 sm:grid-cols-2">
					<div class="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
						<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Engagement</h2>
						<div class="grid grid-cols-2 gap-3">
							<div><p class="text-lg font-semibold text-white">{fmtNum(stats.engagement.total_views)}</p><p class="text-[11px] text-zinc-600">article views</p></div>
							<div><p class="text-lg font-semibold text-white">{fmtNum(stats.engagement.total_saves)}</p><p class="text-[11px] text-zinc-600">saves</p></div>
							<div><p class="text-lg font-semibold text-white">{stats.engagement.avg_feedback_rating ?? '—'}</p><p class="text-[11px] text-zinc-600">avg rating ({stats.engagement.feedback_count})</p></div>
							<div><p class="text-lg font-semibold text-white">{fmtNum(stats.engagement.source_score_sum)}</p><p class="text-[11px] text-zinc-600">source score Σ (HN/GH, not likes)</p></div>
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
						{:else}<p class="text-[12px] text-zinc-600">No feedback yet.</p>{/if}
					</div>
				</section>
			{/if}

			<!-- Users & visitors (from page load, server-side) -->
			<section class="mb-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
				<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Users <span class="font-normal normal-case text-zinc-600">· {data.totalUsers} total</span></h2>
				<div class="overflow-x-auto">
					<table class="w-full text-left text-[12px]">
						<thead class="text-[10px] uppercase tracking-wide text-zinc-600">
							<tr class="border-b border-white/[0.06]">
								<th class="py-2 pr-3 font-medium">User</th>
								<th class="py-2 pr-3 font-medium">Email</th>
								<th class="py-2 pr-3 text-right font-medium">Joined</th>
								<th class="py-2 pr-3 text-right font-medium">Last seen</th>
								<th class="py-2 pr-3 text-right font-medium">Sessions</th>
								<th class="py-2 text-right font-medium">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each data.users as u}
								<tr class="border-b border-white/[0.03]">
									<td class="py-2 pr-3 font-medium text-zinc-300">{u.name}{#if u.isYou}<span class="ml-1 rounded bg-emerald-500/15 px-1 text-[9px] uppercase text-emerald-400">you</span>{/if}</td>
									<td class="py-2 pr-3 text-zinc-500">{u.email}{#if !u.emailVerified}<span class="ml-1 text-[9px] text-amber-500/70">unverified</span>{/if}</td>
									<td class="py-2 pr-3 text-right text-zinc-500">{fmtAgo(u.createdAt)}</td>
									<td class="py-2 pr-3 text-right text-zinc-400">{fmtAgo(u.lastSeen)}</td>
									<td class="py-2 pr-3 text-right text-zinc-500">{u.sessionCount}</td>
									<td class="py-2 text-right whitespace-nowrap">
										{#if !u.isYou}
											<form method="POST" action="?/revokeSessions" class="inline" use:enhance={() => async ({ update }) => { await update({ reset: false }); await fetchStats(); }}>
												<input type="hidden" name="userId" value={u.id} />
												<button class="rounded border border-white/10 px-2 py-1 text-[11px] text-zinc-400 transition-colors hover:border-amber-500/40 hover:text-amber-300" title="Force logout">Logout</button>
											</form>
											<form method="POST" action="?/deleteUser" class="inline" use:enhance={({ cancel }) => { if (!confirm(`Permanently delete ${u.email}? This cascades to their sessions and cannot be undone.`)) cancel(); return async ({ update }) => { await update({ reset: false }); await fetchStats(); }; }}>
												<input type="hidden" name="userId" value={u.id} />
												<button class="ml-1 rounded border border-white/10 px-2 py-1 text-[11px] text-zinc-400 transition-colors hover:border-red-500/40 hover:text-red-300" title="Delete user">Delete</button>
											</form>
										{:else}
											<span class="text-[11px] text-zinc-700">—</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</section>

			<!-- Recent visits -->
			<section class="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
				<h2 class="mb-3 text-[12px] font-semibold uppercase tracking-wide text-zinc-500">Recent visits <span class="font-normal normal-case text-zinc-600">· last 30 sessions</span></h2>
				{#if data.sessions.length}
					<div class="overflow-x-auto">
						<table class="w-full text-left text-[12px]">
							<thead class="text-[10px] uppercase tracking-wide text-zinc-600">
								<tr class="border-b border-white/[0.06]">
									<th class="py-2 pr-3 font-medium">User</th>
									<th class="py-2 pr-3 font-medium">IP</th>
									<th class="py-2 pr-3 font-medium">Device</th>
									<th class="py-2 pr-3 text-right font-medium">When</th>
									<th class="py-2 text-right font-medium">State</th>
								</tr>
							</thead>
							<tbody>
								{#each data.sessions as s}
									<tr class="border-b border-white/[0.03]">
										<td class="py-2 pr-3 text-zinc-300">{s.name ?? '—'}<span class="block text-[10px] text-zinc-600">{s.email ?? ''}</span></td>
										<td class="py-2 pr-3 font-mono text-[11px] text-zinc-500">{s.ipAddress || '—'}</td>
										<td class="py-2 pr-3 text-zinc-500">{uaShort(s.userAgent)}</td>
										<td class="py-2 pr-3 text-right text-zinc-500">{fmtAgo(s.createdAt)}</td>
										<td class="py-2 text-right">{#if s.active}<span class="text-emerald-400">active</span>{:else}<span class="text-zinc-600">expired</span>{/if}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else}<p class="text-[12px] text-zinc-600">No sessions recorded.</p>{/if}
			</section>
		</div>
	{/if}
</div>
