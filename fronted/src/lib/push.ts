import { env } from '$env/dynamic/public';

/**
 * Client-side Web Push helpers: feature detection, permission + subscription state,
 * and enable/disable that also sync the subscription to the server. The public VAPID
 * key comes from PUBLIC_VAPID_KEY (exposed at runtime via $env/dynamic/public).
 */

export interface PushStatus {
	supported: boolean;
	permission: NotificationPermission | 'unsupported';
	subscribed: boolean;
}

export function isPushSupported(): boolean {
	return (
		typeof window !== 'undefined' &&
		'serviceWorker' in navigator &&
		'PushManager' in window &&
		'Notification' in window
	);
}

function urlBase64ToUint8Array(base64String: string): BufferSource {
	const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
	const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
	const raw = atob(base64);
	const buffer = new ArrayBuffer(raw.length);
	const output = new Uint8Array(buffer);
	for (let i = 0; i < raw.length; i++) output[i] = raw.charCodeAt(i);
	return output;
}

async function getRegistration(): Promise<ServiceWorkerRegistration> {
	// In production SvelteKit auto-registers the service worker, so this returns the
	// existing one. In dev (or if registration hasn't happened yet) we register it
	// ourselves so `.ready` resolves instead of hanging.
	const existing = await navigator.serviceWorker.getRegistration();
	if (existing) return navigator.serviceWorker.ready;
	await navigator.serviceWorker.register('/service-worker.js', { type: 'module' });
	return navigator.serviceWorker.ready;
}

export async function getStatus(): Promise<PushStatus> {
	if (!isPushSupported()) {
		return { supported: false, permission: 'unsupported', subscribed: false };
	}
	let subscribed = false;
	try {
		const reg = await navigator.serviceWorker.getRegistration();
		subscribed = !!(await reg?.pushManager.getSubscription());
	} catch {
		/* ignore — treat as not subscribed */
	}
	return { supported: true, permission: Notification.permission, subscribed };
}

/**
 * Request permission (must be called from a user gesture), subscribe, and persist the
 * subscription server-side. Returns the resulting status; if permission is denied the
 * status simply reflects that.
 */
export async function enable(): Promise<PushStatus> {
	if (!isPushSupported()) throw new Error('Push is not supported on this device.');

	const key = env.PUBLIC_VAPID_KEY?.trim();
	if (!key) throw new Error('Notifications are not configured (missing PUBLIC_VAPID_KEY).');

	const permission = await Notification.requestPermission();
	if (permission !== 'granted') return getStatus();

	const reg = await getRegistration();
	let sub = await reg.pushManager.getSubscription();
	if (!sub) {
		sub = await reg.pushManager.subscribe({
			userVisibleOnly: true,
			applicationServerKey: urlBase64ToUint8Array(key)
		});
	}

	const res = await fetch('/api/push/subscribe', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(sub.toJSON())
	});
	if (!res.ok) throw new Error('Failed to save subscription.');

	return getStatus();
}

/** iOS only allows Web Push from a Home Screen install, never from a Safari tab. */
export function needsIosInstall(): boolean {
	if (typeof window === 'undefined') return false;
	const ios =
		/iPad|iPhone|iPod/.test(navigator.userAgent) ||
		(navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
	const standalone =
		window.matchMedia('(display-mode: standalone)').matches ||
		(navigator as Navigator & { standalone?: boolean }).standalone === true;
	return ios && !standalone;
}

/** Ask the server to push a test notification to this user's devices. */
export async function sendTest(): Promise<void> {
	await fetch('/api/push/test', { method: 'POST' }).catch(() => {});
}

/** Unsubscribe on this device and remove it server-side. */
export async function disable(): Promise<PushStatus> {
	if (!isPushSupported()) return getStatus();
	const reg = await navigator.serviceWorker.getRegistration();
	const sub = await reg?.pushManager.getSubscription();
	if (sub) {
		await fetch('/api/push/unsubscribe', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ endpoint: sub.endpoint })
		}).catch(() => {});
		await sub.unsubscribe().catch(() => {});
	}
	return getStatus();
}
