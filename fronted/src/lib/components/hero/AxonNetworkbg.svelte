<script lang="ts">
	// Faint square grid. A few of its lines peel off and meet at one point
	// in the open top-right, above the first card.
	const step = 80;
	const width = 1440;
	const height = 960;
	// Sits in the open band under the header, above the first card.
	const point = { x: 1190, y: 114 };

	const grid: string[] = [];
	for (let x = 0; x <= width; x += step) grid.push(`M ${x} 0 V ${height}`);
	for (let y = 0; y <= height; y += step) grid.push(`M 0 ${y} H ${width}`);

	const dots: { x: number; y: number }[] = [];
	for (let x = 0; x <= width; x += step) {
		for (let y = 0; y <= height; y += step) dots.push({ x, y });
	}

	// Start on the lattice, run straight, then bend. Uneven on purpose.
	const curves = [
		`M 0 128 H 760 C 940 128, 1080 120, ${point.x} ${point.y}`,
		`M 1380 ${height} C 1380 640, 1420 280, 1310 170 C 1256 128, 1220 118, ${point.x} ${point.y}`,
		`M ${width} 400 C 1380 320, 1290 190, ${point.x} ${point.y}`,
		`M 160 920 C 520 900, 900 840, 1140 600 C 1280 450, 1290 200, ${point.x} ${point.y}`
	];

	// Phone: same idea, framed so the point sits in the band under the header.
	const phoneStep = 40;
	const phonePoint = { x: 300, y: 100 };
	const phoneGrid: string[] = [];
	for (let x = 0; x <= 400; x += phoneStep) phoneGrid.push(`M ${x} 0 V 800`);
	for (let y = 0; y <= 800; y += phoneStep) phoneGrid.push(`M 0 ${y} H 400`);
	const phoneDots: { x: number; y: number }[] = [];
	for (let x = 0; x <= 400; x += phoneStep) {
		for (let y = 0; y <= 800; y += phoneStep) phoneDots.push({ x, y });
	}
	const phoneCurves = [
		`M 0 112 H 190 C 240 112, 276 104, ${phonePoint.x} ${phonePoint.y}`,
		`M 400 148 C 362 128, 328 108, ${phonePoint.x} ${phonePoint.y}`,
		`M 372 800 C 372 480, 360 210, ${phonePoint.x} ${phonePoint.y}`
	];
</script>

<div class="network absolute inset-0 h-full w-full overflow-hidden" aria-hidden="true">
	<svg class="desk h-full w-full" viewBox="0 0 {width} {height}" preserveAspectRatio="xMaxYMin slice" fill="none">
		{#each grid as d}
			<path class="grid-line" {d} />
		{/each}
		{#each dots as dot}
			<circle class="grid-dot" cx={dot.x} cy={dot.y} r="2.2" />
		{/each}
		{#each curves as d, i}
			<path class="curve" {d} />
			<path class="mark" {d} pathLength="1000" style={`animation-delay: ${-i * 1.7}s`} />
		{/each}
		<circle class="point" cx={point.x} cy={point.y} r="5" />
	</svg>

	<svg class="phone absolute top-0 h-screen w-full" viewBox="0 0 400 800" preserveAspectRatio="xMidYMin slice" fill="none">
		{#each phoneGrid as d}
			<path class="grid-line" {d} />
		{/each}
		{#each phoneDots as dot}
			<circle class="grid-dot" cx={dot.x} cy={dot.y} r="1.5" />
		{/each}
		{#each phoneCurves as d, i}
			<path class="curve" {d} />
			<path class="mark" {d} pathLength="1000" style={`animation-delay: ${-i * 1.7}s`} />
		{/each}
		<circle class="point" cx={phonePoint.x} cy={phonePoint.y} r="3.2" />
	</svg>
</div>

<style>
	.phone {
		display: none;
	}

	.network {
		color: #1a1a1a;
		-webkit-mask-image: linear-gradient(to bottom, #000 0%, #000 78%, transparent 100%);
		mask-image: linear-gradient(to bottom, #000 0%, #000 78%, transparent 100%);
	}

	:global(html:not(.light)) .network {
		color: #f3f3f3;
	}

	.grid-line,
	.curve,
	.mark {
		stroke: currentColor;
		fill: none;
	}

	.grid-line {
		stroke-width: 0.8;
		opacity: 0.11;
	}

	.grid-dot {
		fill: currentColor;
		opacity: 0.28;
	}

	.curve {
		stroke-width: 1.15;
		opacity: 0.34;
	}

	.mark {
		stroke-width: 1.35;
		stroke-linecap: round;
		stroke-dasharray: 14 1000;
		opacity: 0.55;
		animation: travel 9s linear infinite;
	}

	.point {
		fill: currentColor;
		opacity: 0.9;
	}

	@keyframes travel {
		from {
			stroke-dashoffset: 1000;
		}
		to {
			stroke-dashoffset: 0;
		}
	}

	@media (max-width: 800px) {
		.desk {
			display: none;
		}

		.phone {
			display: block;
		}

		.network {
			opacity: 0.85;
			-webkit-mask-image: linear-gradient(
				to bottom,
				transparent 0%,
				#000 7%,
				#000 16%,
				rgba(0, 0, 0, 0.4) 26%,
				rgba(0, 0, 0, 0.4) 58%,
				#000 74%,
				transparent 100%
			);
			mask-image: linear-gradient(
				to bottom,
				transparent 0%,
				#000 7%,
				#000 16%,
				rgba(0, 0, 0, 0.4) 26%,
				rgba(0, 0, 0, 0.4) 58%,
				#000 74%,
				transparent 100%
			);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.mark {
			display: none;
		}
	}
</style>
