<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		goto('/login', { replaceState: true });
	});
</script>

<svelte:head>
	<title>Sign up — AXON</title>
</svelte:head>

<p class="p-8 text-center text-sm text-zinc-500">Redirecting to sign in…</p>
