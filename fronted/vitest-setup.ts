// Node 22+ exposes an experimental global `localStorage` that is non-functional
// unless the process is started with --localstorage-file, and it shadows the
// jsdom implementation vitest would otherwise provide. Install a real in-memory
// Storage so code under test (feedCache) behaves like it does in a browser.
class MemoryStorage implements Storage {
	private store = new Map<string, string>();

	get length(): number {
		return this.store.size;
	}
	clear(): void {
		this.store.clear();
	}
	getItem(key: string): string | null {
		return this.store.has(key) ? (this.store.get(key) as string) : null;
	}
	key(index: number): string | null {
		return Array.from(this.store.keys())[index] ?? null;
	}
	removeItem(key: string): void {
		this.store.delete(key);
	}
	setItem(key: string, value: string): void {
		this.store.set(key, String(value));
	}
}

Object.defineProperty(globalThis, 'localStorage', {
	value: new MemoryStorage(),
	writable: true,
	configurable: true
});
