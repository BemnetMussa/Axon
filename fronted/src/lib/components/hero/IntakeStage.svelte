<script lang="ts">
	import { onMount } from 'svelte';
	import { SOURCE_ICONS } from '$lib/source-icons';
	import { MARK_DOTS, MARK_PICK } from '$lib/components/ui/AxonMark.svelte';

	// Source bubbles wired into the Axon core. A canvas firehose of items runs
	// along the wires; nearly all die at the core, and every few seconds one
	// is kept and travels the output wire (reported through `onKeep`). Only
	// sources listed in `keepable` produce kept items; their logo lights up in
	// its brand color while the item is in flight.
	type Layout = 'wide' | 'tall';
	type Props = {
		layout: Layout;
		onScan?: (n: number) => void;
		onKeep?: (key: string) => void;
		keepable?: string[];
	};

	let { layout, onScan, onKeep, keepable }: Props = $props();
	const uid = $props.id();

	const BRAND: Record<string, string> = {
		hn: '#F0652F',
		github: '#8B949E',
		openai: '#10A37F',
		anthropic: '#D97757',
		arxiv: '#B31B1B',
		huggingface: '#FFD21E',
		deepmind: '#4F8DFD',
		nvidia: '#76B900',
		google: '#4285F4',
		producthunt: '#DA552F',
		lobsters: '#AC130D',
		techcrunch: '#0A9E01',
		arstechnica: '#FF4E00',
		together: '#6366F1',
		simonw: '#5BA65B',
		theverge: '#FA002A'
	};

	let lit = $state<number | null>(null);

	type Pt = { x: number; y: number };
	type Bubble = { key: string; x: number; y: number; r: number; name: string; mono?: string };
	type Geometry = { W: number; H: number; core: Pt & { r: number }; bubbles: Bubble[]; out: [Pt, Pt] };

	const B = (key: string, x: number, y: number, r: number, name: string, mono?: string): Bubble => ({ key, x, y, r, name, mono });

	const WIDE: Geometry = {
		W: 760,
		H: 520,
		core: { x: 640, y: 260, r: 42 },
		out: [{ x: 682, y: 260 }, { x: 772, y: 260 }],
		bubbles: [
			B('hn', 60, 60, 25, 'Hacker News'),
			B('arxiv', 60, 160, 23, 'ArXiv'),
			B('google', 60, 260, 23, 'Google AI & Research'),
			B('nvidia', 60, 360, 22, 'NVIDIA'),
			B('together', 60, 460, 20, 'Together AI', 'TGR'),
			B('github', 160, 110, 25, 'GitHub'),
			B('openai', 160, 210, 25, 'OpenAI', 'OAI'),
			B('huggingface', 160, 310, 24, 'Hugging Face'),
			B('simonw', 160, 410, 20, 'Simon Willison', 'SW'),
			B('anthropic', 260, 60, 22, 'Anthropic'),
			B('deepmind', 260, 160, 22, 'DeepMind', 'DM'),
			B('producthunt', 260, 260, 20, 'Product Hunt'),
			B('lobsters', 260, 360, 19, 'Lobsters'),
			B('theverge', 260, 460, 19, 'The Verge', 'VRG'),
			B('techcrunch', 350, 130, 17, 'TechCrunch'),
			B('arstechnica', 350, 390, 17, 'Ars Technica')
		]
	};

	const TALL: Geometry = {
		W: 400,
		H: 430,
		core: { x: 200, y: 330, r: 32 },
		out: [{ x: 200, y: 362 }, { x: 200, y: 442 }],
		bubbles: [
			B('hn', 40, 40, 18, 'Hacker News'),
			B('github', 104, 40, 18, 'GitHub'),
			B('openai', 168, 40, 18, 'OpenAI', 'OAI'),
			B('anthropic', 232, 40, 18, 'Anthropic'),
			B('arxiv', 296, 40, 18, 'ArXiv'),
			B('huggingface', 360, 40, 18, 'Hugging Face'),
			B('deepmind', 72, 98, 16, 'DeepMind', 'DM'),
			B('nvidia', 136, 98, 16, 'NVIDIA'),
			B('google', 200, 98, 16, 'Google AI & Research'),
			B('producthunt', 264, 98, 16, 'Product Hunt'),
			B('lobsters', 328, 98, 16, 'Lobsters'),
			B('together', 72, 152, 14, 'Together AI', 'TGR'),
			B('simonw', 136, 152, 14, 'Simon Willison', 'SW'),
			B('techcrunch', 200, 152, 14, 'TechCrunch'),
			B('theverge', 264, 152, 14, 'The Verge', 'VRG'),
			B('arstechnica', 328, 152, 14, 'Ars Technica')
		]
	};

	const REASONS = ['Listicle', 'Duplicate ×4', 'Hype', 'Career post', 'Evergreen list', 'Low traction', 'Tutorial', 'Repost', 'Clickbait', 'Stale'];

	let G = $derived(layout === 'wide' ? WIDE : TALL);

	/** One cubic Bézier per bubble, ending on the core's rim. */
	let wires = $derived.by(() => {
		const { core } = G;
		return G.bubbles.map((b) => {
			let p0: Pt, p1: Pt, p2: Pt, p3: Pt;
			if (layout === 'wide') {
				const ey = core.y + (b.y - core.y) * 0.18;
				const ex = core.x - Math.sqrt(core.r ** 2 - (ey - core.y) ** 2);
				p0 = { x: b.x + b.r, y: b.y };
				p1 = { x: p0.x + (ex - p0.x) * 0.45, y: b.y };
				p2 = { x: ex - 110, y: ey };
				p3 = { x: ex, y: ey };
			} else {
				const ex = core.x + (b.x - core.x) * 0.2;
				const ey = core.y - Math.sqrt(core.r ** 2 - (ex - core.x) ** 2);
				p0 = { x: b.x, y: b.y + b.r };
				p1 = { x: b.x, y: p0.y + (ey - p0.y) * 0.45 };
				p2 = { x: ex, y: ey - 80 };
				p3 = { x: ex, y: ey };
			}
			const f = (n: number) => n.toFixed(1);
			return {
				pts: [p0, p1, p2, p3] as const,
				weight: b.r * b.r,
				d: `M ${f(p0.x)} ${f(p0.y)} C ${f(p1.x)} ${f(p1.y)}, ${f(p2.x)} ${f(p2.y)}, ${f(p3.x)} ${f(p3.y)}`
			};
		});
	});

	/**
	 * Topographic contours around the core: rings that grow wobblier with
	 * distance and stretch toward the sources, as if the core were a basin the
	 * whole field drains into. Deterministic so SSR and hydration match.
	 */
	let contours = $derived.by(() => {
		const { core } = G;
		const wide = layout === 'wide';
		const rings = wide ? 18 : 12;
		const gap = wide ? 30 : 22;
		const out: string[] = [];
		for (let k = 0; k < rings; k++) {
			const base = core.r + 20 + k * gap;
			const wob = 0.025 + k * 0.006;
			let d = '';
			for (let j = 0; j <= 120; j++) {
				const a = (j / 120) * Math.PI * 2;
				const r =
					base *
					(1 +
						wob * Math.sin(3 * a + k * 0.55) +
						wob * 0.7 * Math.sin(5 * a - k * 0.35 + 1.3) +
						wob * 0.4 * Math.sin(8 * a + k * 0.9));
				// Stretch toward the inputs: left in the wide layout, up in the tall one.
				const toward = wide ? -Math.cos(a) : -Math.sin(a);
				const s = 1 + Math.max(0, toward) * (wide ? 0.9 : 0.5);
				const x = core.x + Math.cos(a) * r * (wide ? s : 1);
				const y = core.y + Math.sin(a) * r * (wide ? 0.85 : s);
				d += `${j ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
			}
			out.push(d + 'Z');
		}
		return out;
	});

	const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

	function bez(p: readonly [Pt, Pt, Pt, Pt], t: number): Pt {
		const u = 1 - t;
		const a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
		return { x: a * p[0].x + b * p[1].x + c * p[2].x + d * p[3].x, y: a * p[0].y + b * p[1].y + c * p[2].y + d * p[3].y };
	}

	type Tag = { id: number; text: string; x: number; y: number };
	let tags = $state<Tag[]>([]);
	let tagId = 0;

	let canvas: HTMLCanvasElement;
	let root: HTMLDivElement;

	onMount(() => {
		const ctx = canvas.getContext('2d');
		if (!ctx) return;
		const { W, H, core, out } = G;
		const paths = wires;
		const total = paths.reduce((s, p) => s + p.weight, 0);
		const pickPath = () => {
			let r = Math.random() * total;
			for (let i = 0; i < paths.length; i++) {
				r -= paths[i].weight;
				if (r <= 0) return i;
			}
			return paths.length - 1;
		};

		const pickKept = () => {
			const idx = G.bubbles.flatMap((b, i) => (!keepable || keepable.includes(b.key) ? [i] : []));
			return idx[Math.floor(Math.random() * idx.length)] ?? pickPath();
		};
		const rgbOf = (hex: string) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(',');

		const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
		let ink = '237,237,237';
		const setInk = () => {
			ink = document.documentElement.classList.contains('light') ? '10,10,10' : '237,237,237';
		};
		setInk();

		type Particle = { p: number; t: number; v: number; s: number; a: number };
		const spawn = (initial: boolean): Particle => ({
			p: pickPath(),
			t: initial ? Math.random() : -Math.random() * 0.25,
			v: 0.11 + Math.random() * 0.12,
			s: 1 + Math.random() * 1.4,
			a: 0.25 + Math.random() * 0.55
		});
		const parts = Array.from({ length: layout === 'wide' ? 240 : 140 }, () => spawn(true));
		const flashes: { x: number; y: number; life: number }[] = [];
		let kept: { p: number; t: number; rgb: string } | null = null;
		let outRgb = ink;
		let outT: number | null = null;
		let pulse = 0;
		let keepClock = 1.6;
		let tagClock = 0;
		let scanned = 0;
		let scanClock = 0;

		let scale = 1;
		let dpr = 1;
		const resize = () => {
			const w = canvas.clientWidth;
			if (!w) return;
			scale = w / W;
			dpr = window.devicePixelRatio || 1;
			canvas.width = Math.round(w * dpr);
			canvas.height = Math.round(canvas.clientHeight * dpr);
			draw();
		};

		function step(dt: number) {
			for (const q of parts) {
				q.t += q.v * dt;
				if (q.t >= 1) {
					scanned++;
					if (Math.random() < 0.15) {
						const end = paths[q.p].pts[3];
						flashes.push({ x: end.x + (Math.random() - 0.5) * 10, y: end.y + (Math.random() - 0.5) * 10, life: 1 });
					}
					Object.assign(q, spawn(false));
				}
			}

			keepClock += dt;
			if (!kept && outT === null && keepClock > 4.2) {
				keepClock = 0;
				const p = pickKept();
				kept = { p, t: 0, rgb: rgbOf(BRAND[G.bubbles[p].key] ?? '#ffffff') };
				lit = p;
			}
			if (kept) {
				kept.t += 0.34 * dt;
				if (kept.t >= 1) {
					outRgb = kept.rgb;
					kept = null;
					pulse = 1;
					outT = 0;
				}
			}
			if (outT !== null) {
				outT += 0.8 * dt;
				if (outT >= 1) {
					outT = null;
					onKeep?.(G.bubbles[lit ?? 0].key);
					lit = null;
				}
			}
			pulse = Math.max(0, pulse - dt * 0.8);
			for (const f of flashes) f.life -= dt * 1.4;
			while (flashes.length && flashes[0].life <= 0) flashes.shift();

			tagClock += dt;
			if (tagClock > 1.7) {
				tagClock = 0;
				const above = Math.random() < 0.5;
				const tag: Tag =
					layout === 'wide'
						? { id: ++tagId, text: REASONS[Math.floor(Math.random() * REASONS.length)], x: core.x - core.r - 14 - Math.random() * 60, y: core.y + (above ? -1 : 1) * (core.r + 16 + Math.random() * 70) }
						: { id: ++tagId, text: REASONS[Math.floor(Math.random() * REASONS.length)], x: core.x + (above ? -1 : 1) * (core.r + 50 + Math.random() * 40), y: core.y - 10 + Math.random() * 30 };
				tags = [...tags.slice(-3), tag];
			}

			scanClock += dt;
			if (scanClock > 0.12 && scanned) {
				onScan?.(scanned);
				scanned = 0;
				scanClock = 0;
			}
		}

		function draw() {
			ctx!.setTransform(scale * dpr, 0, 0, scale * dpr, 0, 0);
			ctx!.clearRect(0, 0, W, H);

			for (const q of parts) {
				if (q.t < 0) continue;
				const pt = bez(paths[q.p].pts, q.t);
				const fade = q.t > 0.9 ? (1 - q.t) * 10 : 1;
				ctx!.fillStyle = `rgba(${ink},${(q.a * fade).toFixed(3)})`;
				ctx!.fillRect(pt.x - q.s / 2, pt.y - q.s / 2, q.s, q.s);
			}

			ctx!.lineWidth = 1;
			for (const f of flashes) {
				ctx!.strokeStyle = `rgba(${ink},${(f.life * 0.8).toFixed(3)})`;
				ctx!.beginPath();
				ctx!.moveTo(f.x - 3, f.y - 3);
				ctx!.lineTo(f.x + 3, f.y + 3);
				ctx!.moveTo(f.x + 3, f.y - 3);
				ctx!.lineTo(f.x - 3, f.y + 3);
				ctx!.stroke();
			}

			if (kept) {
				const pt = bez(paths[kept.p].pts, ease(kept.t));
				ctx!.fillStyle = `rgb(${kept.rgb})`;
				ctx!.fillRect(pt.x - 2.5, pt.y - 2.5, 5, 5);
				ctx!.strokeStyle = `rgba(${kept.rgb},0.5)`;
				ctx!.strokeRect(pt.x - 6, pt.y - 6, 12, 12);
			}

			if (pulse > 0) {
				ctx!.strokeStyle = `rgba(${outRgb},${(pulse * 0.7).toFixed(3)})`;
				ctx!.beginPath();
				ctx!.arc(core.x, core.y, core.r + 6 + 26 * (1 - pulse), 0, Math.PI * 2);
				ctx!.stroke();
			}

			if (outT !== null) {
				const e = ease(outT);
				const x = out[0].x + (out[1].x - out[0].x) * e;
				const y = out[0].y + (out[1].y - out[0].y) * e;
				ctx!.strokeStyle = `rgba(${outRgb},0.9)`;
				ctx!.lineWidth = 1.5;
				ctx!.beginPath();
				ctx!.moveTo(out[0].x, out[0].y);
				ctx!.lineTo(x, y);
				ctx!.stroke();
				ctx!.fillStyle = `rgb(${outRgb})`;
				ctx!.fillRect(x - 3, y - 3, 6, 6);
			}
		}

		let raf = 0;
		let last = 0;
		let visible = false;
		const frame = (ts: number) => {
			const dt = last ? Math.min(0.05, (ts - last) / 1000) : 0;
			last = ts;
			step(dt);
			draw();
			raf = requestAnimationFrame(frame);
		};
		const sync = () => {
			const run = visible && !document.hidden && !reduce;
			if (run && !raf) {
				last = 0;
				raf = requestAnimationFrame(frame);
			} else if (!run && raf) {
				cancelAnimationFrame(raf);
				raf = 0;
			}
		};

		const ro = new ResizeObserver(resize);
		ro.observe(canvas);
		const io = new IntersectionObserver((entries) => {
			visible = entries[0]?.isIntersecting ?? false;
			sync();
		});
		io.observe(root);
		const mo = new MutationObserver(() => {
			setInk();
			draw();
		});
		mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
		document.addEventListener('visibilitychange', sync);
		resize();

		return () => {
			cancelAnimationFrame(raf);
			ro.disconnect();
			io.disconnect();
			mo.disconnect();
			document.removeEventListener('visibilitychange', sync);
		};
	});
</script>

<div bind:this={root} class="stage relative w-full" style={`aspect-ratio: ${G.W} / ${G.H}`} aria-hidden="true">
	<svg class="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 {G.W} {G.H}" fill="none">
		<defs>
			<radialGradient
				id="fade-{uid}"
				gradientUnits="userSpaceOnUse"
				cx={G.core.x}
				cy={G.core.y}
				r={layout === 'wide' ? 620 : 300}
				gradientTransform={`translate(${G.core.x} ${G.core.y}) scale(1 ${layout === 'wide' ? 0.62 : 0.8}) translate(${-G.core.x} ${-G.core.y})`}
			>
				<stop offset="0" stop-color="#fff" />
				<stop offset="0.55" stop-color="#fff" stop-opacity="0.8" />
				<stop offset="1" stop-color="#fff" stop-opacity="0" />
			</radialGradient>
			<mask id="mask-{uid}" maskUnits="userSpaceOnUse" x="-1200" y="-800" width="3200" height="2200">
				<rect x="-1200" y="-800" width="3200" height="2200" fill="url(#fade-{uid})" />
			</mask>
		</defs>
		<g mask="url(#mask-{uid})">
			{#each contours as d, k}
				<path class="contour" class:index={k % 5 === 4} {d} />
			{/each}
		</g>
		{#each wires as w}
			<path class="wire" d={w.d} />
		{/each}
		<line class="wire-out" x1={G.out[0].x} y1={G.out[0].y} x2={G.out[1].x} y2={G.out[1].y} />

		{#each G.bubbles as b, i}
			{@const icon = SOURCE_ICONS[b.key]}
			{@const k = (b.r * 0.95) / 24}
			<g class="bubble" class:lit={lit === i} style={`animation-delay: ${-i * 0.9}s; --brand: ${BRAND[b.key] ?? 'currentColor'}`}>
				<title>{b.name}</title>
				<circle class="bubble-bg" cx={b.x} cy={b.y} r={b.r} />
				{#if icon}
					<path class="logo" d={icon.path} transform={`translate(${b.x - 12 * k} ${b.y - 12 * k}) scale(${k})`} />
				{:else}
					<text class="mono" x={b.x} y={b.y} font-size={b.r * 0.5}>{b.mono}</text>
				{/if}
			</g>
		{/each}

		<circle class="core-ring" cx={G.core.x} cy={G.core.y} r={G.core.r + 12} />
		<circle class="core" cx={G.core.x} cy={G.core.y} r={G.core.r} />
		<g class="core-mark" transform={`translate(${G.core.x - 12 * (G.core.r / 30)} ${G.core.y - 12 * (G.core.r / 30)}) scale(${G.core.r / 30})`}>
			{#each MARK_DOTS as d (`${d.x}-${d.y}`)}
				<circle cx={d.x} cy={d.y} r="1.5" opacity={d.o} />
			{/each}
			<circle cx={MARK_PICK.x} cy={MARK_PICK.y} r={MARK_PICK.r} />
		</g>
	</svg>

	<canvas bind:this={canvas} class="pointer-events-none absolute inset-0 h-full w-full"></canvas>

	{#each tags as tag (tag.id)}
		<span
			class="tag axon-label"
			class:wide={layout === 'wide'}
			style={`left: ${(tag.x / G.W) * 100}%; top: ${(tag.y / G.H) * 100}%`}
		>✕ {tag.text}</span>
	{/each}
</div>

<style>
	.stage {
		color: inherit;
	}

	.contour {
		stroke: currentColor;
		stroke-width: 1;
		opacity: 0.055;
	}

	.contour.index {
		opacity: 0.1;
	}

	.wire {
		stroke: currentColor;
		stroke-width: 1;
		opacity: 0.1;
	}

	.wire-out {
		stroke: currentColor;
		stroke-width: 1;
		stroke-dasharray: 2 4;
		opacity: 0.45;
	}

	.bubble {
		animation: bob 9s ease-in-out infinite;
		transform-box: fill-box;
	}

	.bubble-bg {
		fill: var(--stage-bg, #0a0a0a);
		stroke: currentColor;
		stroke-width: 1;
		stroke-opacity: 0.28;
		transition: stroke 1s, stroke-opacity 1s, stroke-width 1s;
	}

	.logo,
	.mono {
		fill: currentColor;
		opacity: 0.85;
		transition: fill 1s, opacity 1s;
	}

	.bubble {
		cursor: default;
	}

	.lit .bubble-bg,
	.bubble:hover .bubble-bg {
		stroke: var(--brand);
		stroke-opacity: 1;
		stroke-width: 1.5;
		transition-duration: 0.4s;
	}

	.lit .logo,
	.lit .mono,
	.bubble:hover .logo,
	.bubble:hover .mono {
		fill: var(--brand);
		opacity: 1;
		transition-duration: 0.4s;
	}

	.mono {
		font-family: var(--font-mono);
		font-weight: 500;
		letter-spacing: 0.04em;
		text-anchor: middle;
		dominant-baseline: central;
	}

	.core-ring {
		stroke: currentColor;
		stroke-width: 1;
		stroke-dasharray: 2 6;
		opacity: 0.5;
		transform-box: fill-box;
		transform-origin: center;
		animation: spin 40s linear infinite;
	}

	.core {
		fill: currentColor;
	}

	.core-mark circle {
		fill: var(--stage-bg, #0a0a0a);
	}

	.tag {
		position: absolute;
		white-space: nowrap;
		font-size: 9px;
		pointer-events: none;
		transform: translate(-50%, -50%);
		animation: tag 3s ease-out forwards;
	}

	.tag.wide {
		transform: translate(-100%, -50%);
	}

	@keyframes tag {
		0% { opacity: 0; translate: 0 6px; }
		15% { opacity: 0.75; translate: 0 0; }
		70% { opacity: 0.6; }
		100% { opacity: 0; translate: 0 -8px; }
	}

	@keyframes bob {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(-3px); }
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	@media (prefers-reduced-motion: reduce) {
		.bubble,
		.core-ring,
		.tag {
			animation: none;
		}
	}
</style>
