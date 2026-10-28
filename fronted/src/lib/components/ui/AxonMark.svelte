<script lang="ts" module>
	// The Axon logo: a 3×3 field of signals rising in strength toward one solid pick.
	// Keep in sync with the static icon SVGs.
	export const MARK_DOTS = [
		{ x: 5, y: 5, o: 0.43 },
		{ x: 12, y: 5, o: 0.55 },
		{ x: 5, y: 12, o: 0.3 },
		{ x: 12, y: 12, o: 0.43 },
		{ x: 19, y: 12, o: 0.55 },
		{ x: 5, y: 19, o: 0.18 },
		{ x: 12, y: 19, o: 0.3 },
		{ x: 19, y: 19, o: 0.43 }
	];
	export const MARK_PICK = { x: 19, y: 5, r: 3.3 };
</script>

<script lang="ts">
	let { class: klass = '' }: { class?: string } = $props();
</script>

<svg class={klass} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
	{#each MARK_DOTS as d (`${d.x}-${d.y}`)}
		<circle cx={d.x} cy={d.y} r="1.5" opacity={d.o} />
	{/each}
	<circle cx={MARK_PICK.x} cy={MARK_PICK.y} r={MARK_PICK.r} />
</svg>
