<script lang="ts">
	import { onMount } from 'svelte';
	import { scaleLinear } from 'd3-scale';
	import { min, max } from 'd3-array';
	import type { ScatterData } from '$lib/data/types';

	interface Props {
		data: ScatterData;
		userX: number | null;
		userY: number | null;
		xLabel: string;
		yLabel?: string;
		colorByAge?: boolean;
		width?: number;
		height?: number;
	}

	let {
		data,
		userX,
		userY,
		xLabel,
		yLabel = 'Overall Rank',
		colorByAge = false,
		width = 600,
		height = 400
	}: Props = $props();

	const AGE_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#0ea5e9'];
	const margin = { top: 16, right: 16, bottom: 44, left: 56 };

	let canvas: HTMLCanvasElement;
	let innerW = $derived(Math.max(100, width - margin.left - margin.right));
	let innerH = $derived(Math.max(50, height - margin.top - margin.bottom));

	let xDomain = $derived((() => {
		const xs = data.points.map((p) => p[0]).sort((a, b) => a - b);
		const lo = xs[Math.floor(xs.length * 0.01)] ?? 0;
		const hi = xs[Math.ceil(xs.length * 0.99) - 1] ?? 1;
		return [lo, hi] as [number, number];
	})());

	let yDomain = $derived([
		min(data.points, (p) => p[1]) ?? 0,
		max(data.points, (p) => p[1]) ?? 1
	] as [number, number]);

	let xScale = $derived(scaleLinear().domain(xDomain).range([0, innerW]).nice());
	let yScale = $derived(scaleLinear().domain(yDomain).range([0, innerH]).nice()); // higher rank = lower on chart

	function draw() {
		if (!canvas) return;
		const dpr = window.devicePixelRatio || 1;
		canvas.width = width * dpr;
		canvas.height = height * dpr;
		canvas.style.width = `${width}px`;
		canvas.style.height = `${height}px`;

		const ctx = canvas.getContext('2d')!;
		ctx.scale(dpr, dpr);
		ctx.clearRect(0, 0, width, height);
		ctx.save();
		ctx.translate(margin.left, margin.top);

		// Population dots
		for (const [x, y, ageIdx] of data.points) {
			ctx.beginPath();
			ctx.arc(xScale(x), yScale(y), 2, 0, Math.PI * 2);
			ctx.fillStyle = colorByAge
				? AGE_COLORS[ageIdx % AGE_COLORS.length] + '80'
				: '#6366f150';
			ctx.fill();
		}

		// User dot
		if (userX !== null && userY !== null) {
			ctx.beginPath();
			ctx.arc(xScale(userX), yScale(userY), 8, 0, Math.PI * 2);
			ctx.fillStyle = '#f59e0b';
			ctx.strokeStyle = '#ffffff';
			ctx.lineWidth = 2.5;
			ctx.fill();
			ctx.stroke();

			// Label
			ctx.fillStyle = '#f59e0b';
			ctx.font = '600 12px Inter, sans-serif';
			ctx.textAlign = 'left';
			ctx.fillText('You', xScale(userX) + 12, yScale(userY) + 4);
		}

		ctx.restore();
	}

	onMount(draw);
	$effect(draw);

	function formatXTick(v: number): string {
		if (xLabel.toLowerCase().includes('height')) return `${Math.round(v)} cm`;
		if (xLabel.toLowerCase().includes('weight')) return `${Math.round(v)} kg`;
		return String(Math.round(v));
	}
</script>

<div class="scatter-wrapper" style="max-width: {width}px;">
	<div class="scatter-container" style="position: relative; width: {width}px; height: {height}px;">
		<canvas bind:this={canvas} style="position: absolute; top: 0; left: 0;" />

		<!-- SVG overlay for axes -->
		<svg
			{width}
			{height}
			viewBox="0 0 {width} {height}"
			style="position: absolute; top: 0; left: 0; pointer-events: none;"
		>
			<g transform="translate({margin.left},{margin.top})">
				<!-- X axis -->
				<line x1="0" x2={innerW} y1={innerH} y2={innerH} stroke="var(--bg-tertiary)" />
				{#each xScale.ticks(5) as tick}
					<text
						x={xScale(tick)}
						y={innerH + 20}
						text-anchor="middle"
						fill="var(--text-muted)"
						font-size="11"
					>
						{formatXTick(tick)}
					</text>
				{/each}
				<text
					x={innerW / 2}
					y={innerH + 38}
					text-anchor="middle"
					fill="var(--text-secondary)"
					font-size="12"
				>
					{xLabel}
				</text>

				<!-- Y axis -->
				{#each yScale.ticks(5) as tick}
					<line
						x1="0" x2={innerW}
						y1={yScale(tick)} y2={yScale(tick)}
						stroke="var(--bg-tertiary)" opacity="0.15"
					/>
					<text
						x={-8}
						y={yScale(tick) + 4}
						text-anchor="end"
						fill="var(--text-muted)"
						font-size="11"
					>
						{tick >= 1000 ? `${(tick / 1000).toFixed(0)}k` : tick}
					</text>
				{/each}
				<text
					x={-40}
					y={innerH / 2}
					text-anchor="middle"
					fill="var(--text-secondary)"
					font-size="12"
					transform="rotate(-90, -40, {innerH / 2})"
				>
					{yLabel}
				</text>
			</g>
		</svg>
	</div>

	{#if colorByAge}
		<div class="legend">
			{#each data.age_brackets as bracket, i}
				<span class="legend-item">
					<span class="dot" style="background: {AGE_COLORS[i]}"></span>
					{bracket}
				</span>
			{/each}
		</div>
	{/if}

	<p class="scatter-count">
		{data.n_sampled.toLocaleString()} of {data.n_total.toLocaleString()} athletes shown
	</p>
</div>

<style>
	.scatter-wrapper {
		width: 100%;
		margin: 0 auto;
	}

	.scatter-container {
		margin: 0 auto;
	}

	canvas {
		border-radius: 4px;
	}

	svg {
		overflow: visible;
	}

	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		justify-content: center;
		margin-top: 0.5rem;
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		display: inline-block;
	}

	.scatter-count {
		text-align: center;
		color: var(--text-muted);
		font-size: 0.75rem;
		margin-top: 0.25rem;
	}
</style>
