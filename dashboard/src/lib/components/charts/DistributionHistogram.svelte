<script lang="ts">
	import { scaleLinear } from 'd3-scale';
	import { max } from 'd3-array';
	import type { DistributionSet } from '$lib/data/types';

	interface Props {
		distribution: DistributionSet | null;
		userValue: number | null;
		scoreType: 'reps' | 'time' | null;
		title?: string;
		width?: number;
		height?: number;
	}

	let {
		distribution,
		userValue,
		scoreType,
		title = '',
		width = 600,
		height = 340
	}: Props = $props();

	const margin = { top: 24, right: 20, bottom: 40, left: 50 };

	let innerW = $derived(Math.max(100, width - margin.left - margin.right));
	let innerH = $derived(Math.max(50, height - margin.top - margin.bottom));

	let xScale = $derived(
		distribution
			? scaleLinear().domain(distribution.domain).range([0, innerW])
			: scaleLinear().domain([0, 1]).range([0, innerW])
	);

	let maxCount = $derived(distribution ? max(distribution.bins, (b) => b.count) ?? 1 : 1);
	let yScale = $derived(scaleLinear().domain([0, maxCount]).range([innerH, 0]).nice());

	function formatTick(v: number): string {
		if (scoreType === 'time') {
			const mins = Math.floor(v / 60);
			const secs = Math.round(v % 60);
			return `${mins}:${secs.toString().padStart(2, '0')}`;
		}
		return v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(Math.round(v));
	}

	let xTicks = $derived(() => {
		if (!distribution) return [];
		const [lo, hi] = distribution.domain;
		const step = (hi - lo) / 5;
		return Array.from({ length: 6 }, (_, i) => lo + step * i);
	});

	let yTicks = $derived(() => {
		return yScale.ticks(5);
	});

	let userX = $derived(userValue !== null && distribution ? xScale(userValue) : null);
</script>

<div class="histogram-wrapper" style="max-width: {width}px;">
	{#if title}
		<h3 class="hist-title">{title}</h3>
	{/if}

	{#if distribution}
		<svg {width} {height} viewBox="0 0 {width} {height}">
			<g transform="translate({margin.left},{margin.top})">
				<!-- Bars -->
				{#each distribution.bins as bin, i}
					{@const bx = xScale(bin.lo)}
					{@const bw = Math.max(1, xScale(bin.hi) - xScale(bin.lo) - 1)}
					{@const by = yScale(bin.count)}
					{@const bh = innerH - by}
					<rect
						x={bx}
						y={by}
						width={bw}
						height={bh}
						fill={userValue !== null && userValue >= bin.lo && userValue < bin.hi
							? 'var(--highlight)'
							: 'var(--accent)'}
						opacity={userValue !== null && userValue >= bin.lo && userValue < bin.hi ? 1 : 0.7}
						rx="2"
					/>
				{/each}

				<!-- User marker line -->
				{#if userX !== null}
					<line
						x1={userX}
						x2={userX}
						y1={0}
						y2={innerH}
						stroke="var(--highlight)"
						stroke-width="2.5"
						stroke-dasharray="6,3"
					/>
					<text
						x={userX}
						y={-8}
						text-anchor="middle"
						fill="var(--highlight)"
						font-size="12"
						font-weight="600"
					>
						You{scoreType ? ': ' + formatTick(userValue!) : ''}
					</text>
				{/if}

				<!-- X axis -->
				<line x1="0" x2={innerW} y1={innerH} y2={innerH} stroke="var(--bg-tertiary)" />
				{#each xTicks() as tick}
					<text
						x={xScale(tick)}
						y={innerH + 20}
						text-anchor="middle"
						fill="var(--text-muted)"
						font-size="11"
					>
						{formatTick(tick)}
					</text>
				{/each}

				<!-- Y axis -->
				{#each yTicks() as tick}
					<line
						x1="0"
						x2={innerW}
						y1={yScale(tick)}
						y2={yScale(tick)}
						stroke="var(--bg-tertiary)"
						opacity="0.3"
					/>
					<text
						x={-8}
						y={yScale(tick) + 4}
						text-anchor="end"
						fill="var(--text-muted)"
						font-size="11"
					>
						{tick >= 1000 ? `${(tick / 1000).toFixed(1)}k` : tick}
					</text>
				{/each}
			</g>
		</svg>

		<p class="hist-count">{distribution.n.toLocaleString()} athletes</p>
	{:else}
		<div class="no-data">No data available</div>
	{/if}
</div>

<style>
	.histogram-wrapper {
		width: 100%;
		margin: 0 auto;
	}

	svg {
		width: 100%;
		height: auto;
		display: block;
	}

	.hist-title {
		font-size: 1rem;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
		text-align: center;
	}

	.hist-count {
		text-align: center;
		color: var(--text-muted);
		font-size: 0.8rem;
		margin-top: 0.25rem;
	}

	.no-data {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: var(--text-muted);
	}
</style>
