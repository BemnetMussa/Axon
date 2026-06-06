<script lang="ts" generics="T extends { id: number }">
	import type { Snippet } from 'svelte';

	type Props = {
		/** The list to render. Items are matched by `id`, so reorder/prepend is safe. */
		items: T[];
		/** The scroll container these items live inside (bound from the parent). */
		scrollEl: HTMLElement | undefined;
		/** Height guess for not-yet-measured rows. Keep close to the real card height. */
		estimateHeight?: number;
		/** Extra rows rendered above/below the viewport to avoid blank edges on fast scroll. */
		overscan?: number;
		/** Vertical padding baked into the virtual height so the list isn't flush to the edges. */
		padTop?: number;
		padBottom?: number;
		/** Vertical gap between rows (matches the old `gap-0.5`). */
		gap?: number;
		item: Snippet<[T]>;
	};

	let {
		items,
		scrollEl,
		estimateHeight = 185,
		overscan = 6,
		padTop = 8,
		padBottom = 8,
		gap = 2,
		item
	}: Props = $props();

	let scrollTop = $state(0);
	let viewportH = $state(0);

	// Measured heights keyed by item id so they survive prepend/reorder. Not reactive
	// itself — reads are gated through `measureVersion` to trigger recompute on change.
	const heightMap = new Map<number, number>();
	let measureVersion = $state(0);

	function heightOf(it: T): number {
		return heightMap.get(it.id) ?? estimateHeight;
	}

	// offsets[i] = top of row i (relative to the content box, after padTop).
	// offsets[items.length] = total scrollable height.
	let offsets = $derived.by(() => {
		measureVersion; // dependency: recompute when any row is (re)measured
		const arr = new Array<number>(items.length + 1);
		let acc = padTop;
		for (let i = 0; i < items.length; i++) {
			arr[i] = acc;
			acc += heightOf(items[i]) + gap;
		}
		arr[items.length] = (items.length > 0 ? acc - gap : padTop) + padBottom;
		return arr;
	});

	let totalHeight = $derived(offsets[items.length] ?? padTop + padBottom);

	// Largest i with offsets[i] <= top.
	function findStart(top: number): number {
		let lo = 0;
		let hi = items.length - 1;
		let ans = 0;
		while (lo <= hi) {
			const mid = (lo + hi) >> 1;
			if (offsets[mid] <= top) {
				ans = mid;
				lo = mid + 1;
			} else {
				hi = mid - 1;
			}
		}
		return ans;
	}

	let range = $derived.by(() => {
		if (items.length === 0) return { start: 0, end: 0 };
		const start = Math.max(0, findStart(scrollTop) - overscan);
		const limit = scrollTop + viewportH;
		let end = start;
		while (end < items.length && offsets[end] < limit) end++;
		end = Math.min(items.length, end + overscan);
		return { start, end };
	});

	let visible = $derived.by(() => {
		const out: { item: T; top: number }[] = [];
		for (let i = range.start; i < range.end; i++) {
			out.push({ item: items[i], top: offsets[i] });
		}
		return out;
	});

	function setHeight(id: number, h: number) {
		const prev = heightMap.get(id);
		if (prev === undefined || Math.abs(prev - h) > 0.5) {
			heightMap.set(id, h);
			measureVersion++;
		}
	}

	function measure(node: HTMLElement, id: number) {
		let currentId = id;
		const ro = new ResizeObserver(() => setHeight(currentId, node.offsetHeight));
		ro.observe(node);
		setHeight(currentId, node.offsetHeight);
		return {
			update(newId: number) {
				currentId = newId;
				setHeight(currentId, node.offsetHeight);
			},
			destroy() {
				ro.disconnect();
			}
		};
	}

	// Keep scrollTop/viewportH in sync with the container we don't own.
	$effect(() => {
		const el = scrollEl;
		if (!el) return;
		const onScroll = () => (scrollTop = el.scrollTop);
		const ro = new ResizeObserver(() => (viewportH = el.clientHeight));
		el.addEventListener('scroll', onScroll, { passive: true });
		ro.observe(el);
		scrollTop = el.scrollTop;
		viewportH = el.clientHeight;
		return () => {
			el.removeEventListener('scroll', onScroll);
			ro.disconnect();
		};
	});

	// Prepend compensation: when new rows are inserted at the front while the user is
	// scrolled down, every offset shifts. Nudge scrollTop by the inserted height so the
	// content under the viewport stays put (matches the old natural-flow behaviour).
	let prevFirstId: number | null = null;
	$effect(() => {
		const el = scrollEl;
		const first = items[0]?.id ?? null;
		if (el && prevFirstId !== null && first !== prevFirstId && el.scrollTop > 0) {
			const idx = items.findIndex((it) => it.id === prevFirstId);
			if (idx > 0) {
				let added = 0;
				for (let i = 0; i < idx; i++) added += heightOf(items[i]) + gap;
				el.scrollTop += added;
				scrollTop = el.scrollTop;
			}
		}
		prevFirstId = first;
	});
</script>

<div style="position: relative; height: {totalHeight}px;">
	{#each visible as v (v.item.id)}
		<div style="position: absolute; left: 0; right: 0; top: {v.top}px;" use:measure={v.item.id}>
			{@render item(v.item)}
		</div>
	{/each}
</div>
