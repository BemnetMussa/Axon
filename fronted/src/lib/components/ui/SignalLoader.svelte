<script lang="ts">
	// Brand "signal" loader — the Axon lightning bolt (Lucide Zap, the app's logo)
	// charging and striking on a loop. Inherits currentColor, so it adapts to whatever
	// context it's dropped into; the glow uses currentColor too (drop-shadow with no
	// colour defaults to it). A drop-in replacement for generic spinners. Echoes the
	// theme-toggle lightning so loading reads as "the signal firing". Honours
	// prefers-reduced-motion with a static mark.
	let { size = 18, class: klass = '' }: { size?: number; class?: string } = $props();
</script>

<span
	class={`signal-loader inline-flex items-center justify-center ${klass}`}
	role="status"
	aria-label="Loading"
>
	<svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
		<path
			d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"
		/>
	</svg>
</span>

<style>
	.signal-loader svg {
		transform-origin: center;
		animation: signal-strike 1.05s ease-in-out infinite;
		will-change: opacity, transform, filter;
	}
	/* Charge → strike → settle, on a loop: a quick bright flash with a glow, then it
	   dims back down so it reads as the bolt repeatedly firing, not just breathing. */
	@keyframes signal-strike {
		0% {
			opacity: 0.35;
			transform: scale(0.9);
		}
		14% {
			opacity: 1;
			transform: scale(1.06);
			filter: drop-shadow(0 0 5px);
		}
		30% {
			opacity: 0.9;
			transform: scale(1);
			filter: drop-shadow(0 0 1px);
		}
		70% {
			opacity: 0.5;
			transform: scale(0.95);
		}
		100% {
			opacity: 0.35;
			transform: scale(0.9);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.signal-loader svg {
			animation: none;
			opacity: 0.85;
		}
	}
</style>
