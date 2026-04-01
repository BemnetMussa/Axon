<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';

	let container: HTMLDivElement;
	let animationId: number | null = null;
	let renderer: THREE.WebGLRenderer | null = null;
	let disposed = false;

	onMount(() => {
		if (!container) return;

		const camera = new THREE.Camera();
		camera.position.z = 1;

		const scene = new THREE.Scene();
		const geometry = new THREE.PlaneGeometry(2, 2);
		const uniforms = {
			time: { value: 1.0 },
			resolution: { value: new THREE.Vector2() }
		};

		const material = new THREE.ShaderMaterial({
			uniforms,
			vertexShader: `
				void main() {
					gl_Position = vec4(position, 1.0);
				}
			`,
			fragmentShader: `
				#define TWO_PI 6.2831853072
				precision highp float;
				uniform vec2 resolution;
				uniform float time;

				float random(vec2 st) {
					return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
				}

				void main(void) {
					vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / min(resolution.x, resolution.y);

					vec2 mosaic = vec2(4.0, 2.0);
					vec2 screenSize = vec2(256.0, 256.0);
					uv.x = floor(uv.x * screenSize.x / mosaic.x) / (screenSize.x / mosaic.x);
					uv.y = floor(uv.y * screenSize.y / mosaic.y) / (screenSize.y / mosaic.y);

					float t = time * 0.06 + random(vec2(uv.x, uv.x)) * 0.4;
					float lineWidth = 0.0008;
					vec3 color = vec3(0.0);

					for (int j = 0; j < 3; j++) {
						for (int i = 0; i < 5; i++) {
							color[j] += lineWidth * float(i * i) /
								abs(fract(t - 0.01 * float(j) + float(i) * 0.01) - length(uv));
						}
					}

					gl_FragColor = vec4(color[2], color[1], color[0], 1.0);
				}
			`
		});

		const mesh = new THREE.Mesh(geometry, material);
		scene.add(mesh);

		renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
		container.innerHTML = '';
		container.appendChild(renderer.domElement);

		const resize = () => {
			if (!renderer || disposed) return;
			const rect = container.getBoundingClientRect();
			renderer.setSize(rect.width, rect.height, false);
			uniforms.resolution.value.x = renderer.domElement.width;
			uniforms.resolution.value.y = renderer.domElement.height;
		};

		resize();
		window.addEventListener('resize', resize);

		const animate = () => {
			if (!renderer || disposed) return;
			animationId = requestAnimationFrame(animate);
			uniforms.time.value += 0.05;
			renderer.render(scene, camera);
		};
		animate();

		return () => {
			disposed = true;
			window.removeEventListener('resize', resize);
			if (animationId) cancelAnimationFrame(animationId);
			geometry.dispose();
			material.dispose();
			renderer?.dispose();
			renderer = null;
		};
	});
</script>

<div bind:this={container} class="absolute inset-0 h-full w-full"></div>
