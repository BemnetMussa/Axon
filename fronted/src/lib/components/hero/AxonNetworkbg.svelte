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
	<svg
		class="absolute inset-0 w-full h-full pointer-events-none"
		xmlns="http://www.w3.org/2000/svg"
		viewBox="0 0 1000 1000"
		preserveAspectRatio="xMidYMin slice"
	>
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
			<!-- Left fan -->
			<path class="base-path" d="M -220 920 C 80 920, 220 430, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-1" d="M -220 920 C 80 920, 220 430, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.8" />

			<path class="base-path" d="M -140 860 C 120 860, 260 410, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-2" d="M -140 860 C 120 860, 260 410, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.6" />

			<path class="base-path" d="M -60 980 C 180 840, 300 470, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-3" d="M -60 980 C 180 840, 300 470, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.5" />

			<path class="base-path" d="M 30 1080 C 220 820, 360 520, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-4" d="M 30 1080 C 220 820, 360 520, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.4" />

			<!-- Center stack -->
			<path class="base-path" d="M 260 1150 C 340 900, 430 560, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-5" d="M 260 1150 C 340 900, 430 560, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.5" />

			<path class="base-path" d="M 380 1200 C 420 930, 470 600, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-6" d="M 380 1200 C 420 930, 470 600, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.7" />

			<path class="base-path" d="M 500 1240 C 500 920, 500 620, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-7" d="M 500 1240 C 500 920, 500 620, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="2" />

			<path class="base-path" d="M 620 1200 C 580 930, 530 600, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-8" d="M 620 1200 C 580 930, 530 600, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.7" />

			<path class="base-path" d="M 740 1150 C 660 900, 570 560, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-9" d="M 740 1150 C 660 900, 570 560, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.5" />

			<!-- Right fan -->
			<path class="base-path" d="M 970 1080 C 780 820, 640 520, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-10" d="M 970 1080 C 780 820, 640 520, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.4" />

			<path class="base-path" d="M 1060 980 C 820 840, 700 470, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-11" d="M 1060 980 C 820 840, 700 470, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.5" />

			<path class="base-path" d="M 1140 860 C 880 860, 740 410, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-12" d="M 1140 860 C 880 860, 740 410, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.6" />

			<path class="base-path" d="M 1220 920 C 920 920, 780 430, 500 200" fill="none" stroke="url(#base-line)" stroke-width="1" />
			<path class="signal-path delay-2" d="M 1220 920 C 920 920, 780 430, 500 200" fill="none" stroke="url(#fade-up)" stroke-width="1.8" />
		</g>
	</svg>
</div>

<style>
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
	.delay-6 { animation-delay: 0.8s; animation-duration: 4.4s; }
	.delay-7 { animation-delay: 1.2s; animation-duration: 5.1s; }
	.delay-8 { animation-delay: 2s; animation-duration: 4.6s; }
	.delay-9 { animation-delay: 2.8s; animation-duration: 4.3s; }
	.delay-10 { animation-delay: 0.3s; animation-duration: 5.3s; }
	.delay-11 { animation-delay: 1.9s; animation-duration: 4.7s; }
	.delay-12 { animation-delay: 3.1s; animation-duration: 4.1s; }

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