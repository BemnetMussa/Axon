<script lang="ts">
	// Brand loader — the Axon mark pulsing on a loop. Inherits currentColor, so it
	// adapts to whatever context it's dropped into. Honours prefers-reduced-motion with a
	// static mark.
	import AxonMark from './AxonMark.svelte';

	let { size = 18, class: klass = '' }: { size?: number; class?: string } = $props();
</script>

<span
	class={`signal-loader inline-flex items-center justify-center ${klass}`}
	role="status"
	aria-label="Loading"
	style={`width: ${size}px; height: ${size}px;`}
>
	<AxonMark class="h-full w-full" />
</span>

<style>
	.signal-loader :global(svg) {
		transform-origin: center;
		animation: signal-fire 1.05s ease-in-out infinite;
	}
	@keyframes signal-fire {
		0% {
			opacity: 0.35;
		}
		20% {
			opacity: 1;
		}
		100% {
			opacity: 0.35;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.signal-loader :global(svg) {
			animation: none;
			opacity: 0.85;
		}
	}
</style>
