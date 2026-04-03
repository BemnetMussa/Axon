<!-- $lib/components/hero/AxonNetworkBg.svelte -->
<script lang="ts">
	// No external libraries needed! Pure SVG and CSS magic.
</script>

<div class="absolute inset-0 w-full h-full overflow-hidden flex items-center justify-center">
	
	<!-- 1. The Matrix Grid (Subtle technical foundation) -->
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_0%,#000_20%,transparent_100%)]"></div>

	<!-- 2. The Core Glow (Where signals converge) -->
	<div class="absolute top-[10%] left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px] rounded-full pointer-events-none"></div>

	<!-- 3. The Signal Network (SVG) -->
	<svg class="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
		<defs>
			<!-- Signal Colors -->
			<linearGradient id="fade-up" x1="0%" y1="100%" x2="0%" y2="0%">
				<stop offset="0%" stop-color="rgba(16, 185, 129, 0)" />
				<stop offset="50%" stop-color="rgba(16, 185, 129, 0.8)" />
				<stop offset="100%" stop-color="rgba(16, 185, 129, 0)" />
			</linearGradient>

			<!-- Faded Base Lines -->
			<linearGradient id="base-line" x1="0%" y1="100%" x2="0%" y2="0%">
				<stop offset="0%" stop-color="currentColor" stop-opacity="0" />
				<stop offset="100%" stop-color="currentColor" stop-opacity="0.1" />
			</linearGradient>
		</defs>

		<!-- 
			The paths converge roughly at X: 50%, Y: 25% (Behind the text).
			We use a relative coordinate system (viewBox="0 0 1000 1000" but scaled).
			For this, absolute viewport units work best for responsive curves.
		-->
		<g class="text-zinc-400 dark:text-zinc-600">
			<!-- Far Left Signal -->
			<path class="base-path" d="M -100 800 C 200 800, 300 300, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-1" d="M -100 800 C 200 800, 300 300, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="2" />

			<!-- Mid Left Signal -->
			<path class="base-path" d="M 100 1000 C 250 700, 400 400, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-2" d="M 100 1000 C 250 700, 400 400, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.5" />

			<!-- Bottom Center Signal -->
			<path class="base-path" d="M 500 1200 C 500 800, 500 500, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-3" d="M 500 1200 C 500 800, 500 500, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="2" />

			<!-- Mid Right Signal -->
			<path class="base-path" d="M 900 1000 C 750 700, 600 400, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-4" d="M 900 1000 C 750 700, 600 400, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.5" />

			<!-- Far Right Signal -->
			<path class="base-path" d="M 1100 800 C 800 800, 700 300, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-5" d="M 1100 800 C 800 800, 700 300, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="2" />
		</g>
	</svg>
</div>

<style>
	/* Make SVG responsive but maintain coordinate system */
	svg {
		viewBox: 0 0 1000 1000;
		preserveAspectRatio: xMidYMin slice;
	}

	.signal-path {
		/* This creates the "Dash" of light */
		stroke-dasharray: 150 2000;
		stroke-linecap: round;
		animation: flow 4s linear infinite;
		opacity: 0;
	}

	/* Timing variations so they don't all fire at once */
	.delay-1 { animation-delay: 0s; animation-duration: 4s; }
	.delay-2 { animation-delay: 1.5s; animation-duration: 3.5s; }
	.delay-3 { animation-delay: 0.5s; animation-duration: 5s; }
	.delay-4 { animation-delay: 2.5s; animation-duration: 4.2s; }
	.delay-5 { animation-delay: 1s; animation-duration: 4.8s; }

	@keyframes flow {
		0% {
			stroke-dashoffset: 2000;
			opacity: 0;
		}
		10% {
			opacity: 1;
		}
		80% {
			opacity: 1;
		}
		100% {
			stroke-dashoffset: 0; /* Flows toward the end of the path */
			opacity: 0;
		}
	}
</style>