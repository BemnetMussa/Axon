<script lang="ts">
	// Oscilloscope-style trace: dense noise streams in from the left, crosses the
	// filter gate, and only a few clean pulses come out the right side.
	// Deterministic (seeded) so the SSR markup and the hydrated client match.
	type Props = {
		/** Where the gate sits, as a fraction of the width. */
		gate?: number;
		seed?: number;
		/** Small sidebar variant: no ruler, no labels, tighter amplitude. */
		compact?: boolean;
		inLabel?: string;
		outLabel?: string;
		gateLabel?: string;
		class?: string;
	};

	let {
		gate = 0.58,
		seed = 11,
		compact = false,
		inLabel,
		outLabel,
		gateLabel = 'Filter',
		class: klass = ''
	}: Props = $props();

	const uid = $props.id();
	const W = 1200;
	const H = 200;
	const MID = H / 2;
	const SPEED = 70; // user units per second, same on both sides of the gate

	function rng(a: number) {
		return () => {
			a |= 0;
			a = (a + 0x6d2b79f5) | 0;
			let t = Math.imul(a ^ (a >>> 15), 1 | a);
			t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
	}

	let gateX = $derived(Math.round(W * gate));
	let outW = $derived(W - gateX);

	let noise = $derived.by(() => {
		const r = rng(seed);
		const amp = compact ? H * 0.3 : H * 0.26;
		const step = compact ? 9 : 6;
		let d = `M 0 ${MID}`;
		for (let x = step; x < gateX - step; x += step) {
			const spike = r() < 0.07 ? 1.7 : 1;
			const y = MID + (r() - 0.5) * 2 * amp * spike;
			d += ` L ${x} ${y.toFixed(1)}`;
		}
		return `${d} L ${gateX} ${MID}`;
	});

	let signal = $derived.by(() => {
		const peaks = [0.2, 0.55, 0.82];
		const tall = compact ? H * 0.42 : H * 0.4;
		let d = `M 0 ${MID}`;
		for (const p of peaks) {
			const x = Math.round(outW * p);
			d += ` L ${x - 10} ${MID} L ${x - 3} ${MID - tall * 0.18} L ${x} ${MID - tall}`;
			d += ` L ${x + 4} ${MID + tall * 0.22} L ${x + 9} ${MID}`;
		}
		return `${d} L ${outW} ${MID}`;
	});

	let ticks = $derived.by(() => {
		const out: { x: number; major: boolean }[] = [];
		for (let x = 0; x <= W; x += 15) out.push({ x, major: x % 75 === 0 });
		return out;
	});
</script>

<div class={`trace relative ${klass}`} aria-hidden="true">
	<svg class="h-full w-full" viewBox="0 0 {W} {H}" preserveAspectRatio="none" fill="none">
		<defs>
			<clipPath id="{uid}-in"><rect x="0" y="0" width={gateX} height={H} /></clipPath>
			<clipPath id="{uid}-out"><rect x={gateX} y="0" width={outW} height={H} /></clipPath>
		</defs>

		<line class="baseline" x1="0" y1={MID} x2={W} y2={MID} />

		{#if !compact}
			{#each ticks as t}
				<line class="tick" x1={t.x} y1={H} x2={t.x} y2={H - (t.major ? 12 : 5)} />
			{/each}
		{/if}

		<g clip-path="url(#{uid}-in)">
			<g class="flow" style={`--len: ${gateX}px; --dur: ${gateX / SPEED}s`}>
				<path class="noise" d={noise} />
				<path class="noise" d={noise} transform="translate({gateX} 0)" />
			</g>
		</g>

		<g clip-path="url(#{uid}-out)">
			<g transform="translate({gateX} 0)">
				<g class="flow" style={`--len: ${outW}px; --dur: ${outW / SPEED}s`}>
					<path class="signal" d={signal} />
					<path class="signal" d={signal} transform="translate({outW} 0)" />
				</g>
			</g>
		</g>

		<line class="gate" x1={gateX} y1="0" x2={gateX} y2={H} />
		<rect class="gate-box" x={gateX - 5} y={MID - 5} width="10" height="10" />
	</svg>

	{#if !compact}
		{#if inLabel}
			<span class="label left-0 top-0">{inLabel}</span>
		{/if}
		<span class="label top-0 hidden -translate-x-1/2 sm:block" style={`left: ${gate * 100}%`}>{gateLabel}</span>
		{#if outLabel}
			<span class="label right-0 top-0 text-right">{outLabel}</span>
		{/if}
	{/if}
</div>

<style>
	.trace {
		color: inherit;
	}

	path,
	line,
	rect {
		vector-effect: non-scaling-stroke;
	}

	.baseline {
		stroke: currentColor;
		stroke-width: 1;
		opacity: 0.12;
	}

	.tick {
		stroke: currentColor;
		stroke-width: 1;
		opacity: 0.22;
	}

	.noise {
		stroke: currentColor;
		stroke-width: 1;
		stroke-linejoin: round;
		opacity: 0.38;
	}

	.signal {
		stroke: currentColor;
		stroke-width: 1.6;
		stroke-linejoin: miter;
	}

	.gate {
		stroke: currentColor;
		stroke-width: 1;
		stroke-dasharray: 3 4;
		opacity: 0.55;
	}

	.gate-box {
		fill: var(--trace-bg, transparent);
		stroke: currentColor;
		stroke-width: 1.2;
	}

	.flow {
		animation: flow var(--dur) linear infinite;
	}

	@keyframes flow {
		from {
			transform: translateX(calc(var(--len) * -1));
		}
		to {
			transform: translateX(0);
		}
	}

	.label {
		position: absolute;
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 500;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		white-space: nowrap;
		opacity: 0.6;
	}

	@media (prefers-reduced-motion: reduce) {
		.flow {
			animation: none;
		}
	}
</style>
