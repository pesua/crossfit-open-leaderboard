<script lang="ts">
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	interface Props {
		percentile: number | null;
		label: string;
		subtitle?: string;
		total?: number;
	}

	let { percentile, label, subtitle = '', total = 0 }: Props = $props();

	const animated = tweened(0, { duration: 1200, easing: cubicOut });
	$effect(() => {
		animated.set(percentile ?? 0);
	});

	const R = 110;
	const cx = 150;
	const cy = 140;
	const strokeW = 18;

	function arcPath(pct: number): string {
		const angle = (Math.max(0, Math.min(100, pct)) / 100) * Math.PI;
		const x = cx - R * Math.cos(angle);
		const y = cy - R * Math.sin(angle);
		const largeArc = pct > 50 ? 1 : 0;
		return `M ${cx - R} ${cy} A ${R} ${R} 0 ${largeArc} 1 ${x} ${y}`;
	}

	function getColor(pct: number): string {
		if (pct >= 90) return '#22c55e';
		if (pct >= 70) return '#84cc16';
		if (pct >= 50) return '#eab308';
		if (pct >= 30) return '#f97316';
		return '#ef4444';
	}
</script>

<div class="gauge-wrapper">
	<svg viewBox="0 0 300 170" class="gauge-svg">
		<defs>
			<linearGradient id="gauge-bg" x1="0" y1="0" x2="1" y2="0">
				<stop offset="0%" stop-color="#334155" />
				<stop offset="100%" stop-color="#334155" />
			</linearGradient>
		</defs>

		<!-- Background arc -->
		<path
			d={arcPath(100)}
			fill="none"
			stroke="#1e293b"
			stroke-width={strokeW}
			stroke-linecap="round"
		/>

		<!-- Filled arc -->
		{#if percentile !== null}
			<path
				d={arcPath($animated)}
				fill="none"
				stroke={getColor($animated)}
				stroke-width={strokeW}
				stroke-linecap="round"
				class="gauge-fill"
			/>
		{/if}

		<!-- Center text -->
		<text x={cx} y={cy - 20} text-anchor="middle" class="gauge-pct">
			{percentile !== null ? `Top ${Math.max(1, 100 - Math.round($animated))}%` : '—'}
		</text>
		<text x={cx} y={cy + 8} text-anchor="middle" class="gauge-label">
			{label}
		</text>
	</svg>

	{#if subtitle}
		<p class="gauge-subtitle">{subtitle}</p>
	{/if}
	{#if total > 0 && percentile !== null}
		<p class="gauge-detail">
			Better than ~{Math.round(total * (percentile / 100)).toLocaleString()} of {total.toLocaleString()} athletes
		</p>
	{/if}
</div>

<style>
	.gauge-wrapper {
		text-align: center;
		width: 100%;
		max-width: 360px;
		margin: 0 auto;
	}

	.gauge-svg {
		width: 100%;
		height: auto;
	}

	.gauge-fill {
		filter: drop-shadow(0 0 8px currentColor);
	}

	.gauge-pct {
		font-size: 2rem;
		font-weight: 800;
		fill: var(--text-primary);
	}

	.gauge-label {
		font-size: 0.85rem;
		font-weight: 500;
		fill: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.gauge-subtitle {
		color: var(--text-secondary);
		font-size: 0.9rem;
		margin-top: 0.25rem;
	}

	.gauge-detail {
		color: var(--text-muted);
		font-size: 0.8rem;
		margin-top: 0.25rem;
	}
</style>
