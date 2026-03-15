<script lang="ts">
	import { scaleLinear, scaleBand } from 'd3-scale';
	import type { AgeDistEntry } from '$lib/data/types';

	interface Props {
		data: Record<string, AgeDistEntry>;
		userBracket: string;
		userValue: number | null;
		scoreType: 'reps' | 'time';
		title?: string;
		width?: number;
		height?: number;
	}

	let {
		data,
		userBracket,
		userValue,
		scoreType,
		title = '',
		width = 600,
		height = 340
	}: Props = $props();

	const margin = { top: 24, right: 20, bottom: 48, left: 50 };
	const AGE_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#0ea5e9'];

	let brackets = $derived(Object.keys(data));
	let innerW = $derived(Math.max(100, width - margin.left - margin.right));
	let innerH = $derived(Math.max(50, height - margin.top - margin.bottom));

	let xScale = $derived(scaleBand<string>().domain(brackets).range([0, innerW]).padding(0.25));
	let yDomain = $derived(() => {
		let lo = Infinity, hi = -Infinity;
		for (const d of Object.values(data)) {
			lo = Math.min(lo, d.p5);
			hi = Math.max(hi, d.p95);
		}
		if (userValue !== null) {
			lo = Math.min(lo, userValue);
			hi = Math.max(hi, userValue);
		}
		return [lo * 0.9, hi * 1.05] as [number, number];
	});
	let yScale = $derived(scaleLinear().domain(yDomain()).range(scoreType === 'time' ? [0, innerH] : [innerH, 0]).nice());

	function formatTick(v: number): string {
		if (scoreType === 'time') {
			const mins = Math.floor(v / 60);
			const secs = Math.round(v % 60);
			return `${mins}:${secs.toString().padStart(2, '0')}`;
		}
		return String(Math.round(v));
	}
</script>

<div class="boxplot-wrapper" style="max-width: {width}px;">
	{#if title}
		<h3 class="bp-title">{title}</h3>
	{/if}

	<svg {width} {height} viewBox="0 0 {width} {height}">
		<g transform="translate({margin.left},{margin.top})">
			<!-- Y grid lines -->
			{#each yScale.ticks(5) as tick}
				<line
					x1="0" x2={innerW}
					y1={yScale(tick)} y2={yScale(tick)}
					stroke="var(--bg-tertiary)" opacity="0.3"
				/>
				<text x={-8} y={yScale(tick) + 4} text-anchor="end" fill="var(--text-muted)" font-size="11">
					{formatTick(tick)}
				</text>
			{/each}

			<!-- Box plots -->
			{#each brackets as bracket, idx}
				{@const d = data[bracket]}
				{@const x = xScale(bracket) ?? 0}
				{@const bw = xScale.bandwidth()}
				{@const isUser = bracket === userBracket}
				{@const color = isUser ? 'var(--highlight)' : AGE_COLORS[idx % AGE_COLORS.length]}

				<!-- Whisker -->
				<line
					x1={x + bw / 2} x2={x + bw / 2}
					y1={yScale(d.p10)} y2={yScale(d.p90)}
					stroke={color} stroke-width="1.5"
				/>
				<!-- Whisker caps -->
				<line x1={x + bw * 0.25} x2={x + bw * 0.75} y1={yScale(d.p10)} y2={yScale(d.p10)} stroke={color} stroke-width="1.5" />
				<line x1={x + bw * 0.25} x2={x + bw * 0.75} y1={yScale(d.p90)} y2={yScale(d.p90)} stroke={color} stroke-width="1.5" />

				<!-- Box (p25 to p75) -->
				<rect
					x={x} y={Math.min(yScale(d.p25), yScale(d.p75))}
					width={bw}
					height={Math.abs(yScale(d.p25) - yScale(d.p75))}
					fill={isUser ? 'rgba(245, 158, 11, 0.2)' : 'rgba(99, 102, 241, 0.15)'}
					stroke={color}
					stroke-width="1.5"
					rx="3"
				/>

				<!-- Median -->
				<line
					x1={x} x2={x + bw}
					y1={yScale(d.p50)} y2={yScale(d.p50)}
					stroke={color} stroke-width="2.5"
				/>

				<!-- User dot on their bracket -->
				{#if isUser && userValue !== null}
					<circle
						cx={x + bw / 2}
						cy={yScale(userValue)}
						r="6"
						fill="var(--highlight)"
						stroke="white"
						stroke-width="2"
					/>
				{/if}

				<!-- Label -->
				<text
					x={x + bw / 2}
					y={innerH + 16}
					text-anchor="middle"
					fill={isUser ? 'var(--highlight)' : 'var(--text-muted)'}
					font-size="10"
					font-weight={isUser ? '700' : '400'}
				>
					{bracket}
				</text>

				<!-- N count -->
				<text
					x={x + bw / 2}
					y={innerH + 30}
					text-anchor="middle"
					fill="var(--text-muted)"
					font-size="9"
					opacity="0.6"
				>
					n={d.n.toLocaleString()}
				</text>
			{/each}
		</g>
	</svg>
</div>

<style>
	.boxplot-wrapper {
		width: 100%;
		margin: 0 auto;
	}

	svg {
		width: 100%;
		height: auto;
		display: block;
	}

	.bp-title {
		font-size: 1rem;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
		text-align: center;
	}
</style>
