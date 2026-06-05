// Scroll-reveal action: fades + lifts an element into view the first time it
// enters the viewport. GPU-only (opacity + transform), fires once, then
// disconnects. A no-op for users who prefer reduced motion, so it can never
// reintroduce scroll jank.
type RevealParams = { delay?: number; y?: number; duration?: number };

export function reveal(node: HTMLElement, params: RevealParams = {}) {
	const prefersReduced =
		typeof window !== 'undefined' &&
		window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	// Reduced motion (or no IO support): leave the element in its natural, visible state.
	if (prefersReduced || typeof IntersectionObserver === 'undefined') return;

	const { delay = 0, y = 18, duration = 600 } = params;
	const ease = 'cubic-bezier(0.16, 1, 0.3, 1)';

	// Hidden start state — set synchronously on mount, before first paint.
	node.style.opacity = '0';
	node.style.transform = `translate3d(0, ${y}px, 0)`;
	node.style.willChange = 'opacity, transform';

	const show = () => {
		node.style.transition = `opacity ${duration}ms ${ease} ${delay}ms, transform ${duration}ms ${ease} ${delay}ms`;
		node.style.opacity = '1';
		node.style.transform = 'translate3d(0, 0, 0)';
		const cleanup = () => {
			node.style.willChange = '';
			node.removeEventListener('transitionend', cleanup);
		};
		node.addEventListener('transitionend', cleanup);
	};

	const io = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					show();
					io.disconnect();
				}
			}
		},
		{ threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
	);

	io.observe(node);

	return {
		destroy() {
			io.disconnect();
		}
	};
}
