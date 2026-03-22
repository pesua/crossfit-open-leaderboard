<script lang="ts">
	import { onMount, tick } from 'svelte';
	import type { AllData, DistributionSet, Gender, Tier } from '$lib/data/types';
	import {
		year,
		gender,
		age,
		wod1Raw,
		wod2Raw,
		wod3Raw,
		wod1Tier,
		wod2Tier,
		wod3Tier,
		ageBracket,
		createDerivedStats
	} from '$lib/stores/userInput';
	import PercentileGauge from '$lib/components/charts/PercentileGauge.svelte';
	import DistributionHistogram from '$lib/components/charts/DistributionHistogram.svelte';
	import BoxPlot from '$lib/components/charts/BoxPlot.svelte';
	import ScatterCanvas from '$lib/components/charts/ScatterCanvas.svelte';

	let { data } = $props<{ data: { years: Record<string, AllData>; availableYears: string[] } }>();
	let allData = $derived(data.years[$year] ?? data.years[data.availableYears[data.availableYears.length - 1]]);

	let stats = $derived(createDerivedStats(allData));

	let activeStep = $state(0);
	let showResults = $state(false);

	$effect(() => {
		$year; // track year changes
		showResults = false;
		activeStep = 0;
	});
	let chartWidth = $state(560);
	let chartContainer: HTMLElement;

	// Responsive chart width
	onMount(() => {
		if (chartContainer) {
			const ro = new ResizeObserver(([entry]) => {
				chartWidth = Math.min(entry.contentRect.width - 32, 700);
			});
			ro.observe(chartContainer);
			return () => ro.disconnect();
		}
	});

	async function initScrollama() {
		await tick();
		const scrollama = (await import('scrollama')).default;
		const scroller = scrollama();
		scroller
			.setup({ step: '.scroll-step', offset: 0.45 })
			.onStepEnter(({ index }: { index: number }) => {
				activeStep = index;
			});
		window.addEventListener('resize', scroller.resize);
	}

	function handleStart() {
		showResults = true;
		initScrollama();
		setTimeout(() => {
			document.querySelector('.scroll-start')?.scrollIntoView({ behavior: 'smooth' });
		}, 100);
	}

	// Helpers to get the right distribution for each WOD
	function getWodDist(wodIdx: number, tier: Tier, scoreType: 'reps' | 'time' | null): DistributionSet | null {
		const key = `wod_${wodIdx}` as 'wod_1' | 'wod_2' | 'wod_3';
		const dists = allData.distributions[$gender][key];
		if (!scoreType) return null;
		const label = `${tier}_${scoreType}`;
		return dists[label] ?? null;
	}

	function getWodAgeDist(wodIdx: number) {
		const key = `wod_${wodIdx}` as 'wod_1' | 'wod_2' | 'wod_3';
		return allData.ageDistributions[$gender][key];
	}

	let genderMeta = $derived(allData.meta[$gender]);
	let scatterColorByAge = $state(false);
</script>

<main>
	<!-- Hero / Input Section -->
	<section class="hero">
		<div class="container hero-inner">
			<h1 class="hero-title">Where Do You Rank?</h1>
			<div class="year-selector">
				{#each data.availableYears as y}
					<button
						class="year-pill"
						class:active={$year === y}
						onclick={() => year.set(y)}
					>{y} Open</button>
				{/each}
			</div>
			<p class="hero-desc">
				Enter your scores to see how you compare against
				{allData.meta.men.total_athletes.toLocaleString()} men and
				{allData.meta.women.total_athletes.toLocaleString()} women worldwide.
			</p>

			<div class="input-card">
				<!-- Gender -->
				<div class="input-row">
					<label class="input-label">Division</label>
					<div class="pill-group">
						<button
							class="pill"
							class:active={$gender === 'men'}
							onclick={() => gender.set('men')}
						>
							Men
						</button>
						<button
							class="pill"
							class:active={$gender === 'women'}
							onclick={() => gender.set('women')}
						>
							Women
						</button>
					</div>
				</div>

				<!-- Age -->
				<div class="input-row">
					<label class="input-label" for="age-input">Age</label>
					<input
						id="age-input"
						type="number"
						min="14"
						max="65"
						bind:value={$age}
						class="text-input age-input"
					/>
				</div>

				<!-- WOD 1 -->
								<div class="input-row wod-row">
					<label class="input-label">
						{genderMeta.wods[0].name}
						<span class="input-hint">reps (e.g. 245)</span>
					</label>
					<div class="wod-inputs">
						<input type="text" placeholder="245" bind:value={$wod1Raw} class="text-input score-input" />
						<div class="pill-group pill-small">
							<button class="pill" class:active={$wod1Tier === 'rx'} onclick={() => wod1Tier.set('rx')}>Rx</button>
							<button class="pill" class:active={$wod1Tier === 'scaled'} onclick={() => wod1Tier.set('scaled')}>Scaled</button>
						</div>
					</div>
				</div>

				<!-- WOD 2 -->
								<div class="input-row wod-row">
					<label class="input-label">
						{genderMeta.wods[1].name}
						<span class="input-hint">time (e.g. 9:37) or reps (e.g. 185)</span>
					</label>
					<div class="wod-inputs">
						<input type="text" placeholder="9:37 or 185" bind:value={$wod2Raw} class="text-input score-input" />
						<div class="pill-group pill-small">
							<button class="pill" class:active={$wod2Tier === 'rx'} onclick={() => wod2Tier.set('rx')}>Rx</button>
							<button class="pill" class:active={$wod2Tier === 'scaled'} onclick={() => wod2Tier.set('scaled')}>Scaled</button>
						</div>
					</div>
				</div>

				<!-- WOD 3 -->
								<div class="input-row wod-row">
					<label class="input-label">
						{genderMeta.wods[2].name}
						<span class="input-hint">time (e.g. 9:37) or reps (e.g. 185)</span>
					</label>
					<div class="wod-inputs">
						<input type="text" placeholder="9:37 or 185" bind:value={$wod3Raw} class="text-input score-input" />
						<div class="pill-group pill-small">
							<button class="pill" class:active={$wod3Tier === 'rx'} onclick={() => wod3Tier.set('rx')}>Rx</button>
							<button class="pill" class:active={$wod3Tier === 'scaled'} onclick={() => wod3Tier.set('scaled')}>Scaled</button>
						</div>
					</div>
				</div>

				<button class="cta-button" onclick={handleStart} disabled={!$stats.hasScores}>
					See My Results
				</button>
			</div>
		</div>
	</section>

	<!-- Scrollytelling Section -->
	{#if showResults}
		<div class="scroll-start"></div>
		<section class="container scroll-section">
			<div class="scroll-body">
				<!-- Steps column -->
				<div class="steps-column">
					<!-- Step 0: Overall -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>Your Overall Ranking</h2>
							<p>
								Among {genderMeta.total_athletes.toLocaleString()} {genderMeta.label.toLowerCase()} who competed in
								the {$year} CrossFit Open, here's where you stand.
							</p>
						</div>
					</div>

					<!-- Step 1: Age Group -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>In Your Age Group</h2>
							<p>
								Compared to other athletes aged {$ageBracket}, your results tell a different story.
								Age-group context often reveals strengths the overall ranking hides.
							</p>
						</div>
					</div>

					<!-- Step 2: Age comparison box plot -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>Across All Age Groups</h2>
							<p>
								How does raw performance vary across age groups on {genderMeta.wods[0].name}?
								Each box shows the range from 10th to 90th percentile, with the median marked.
							</p>
						</div>
					</div>

					<!-- Step 3: WOD 1 -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>{genderMeta.wods[0].name} — Deep Dive</h2>
							<p>
								{#if $stats.wodScores[0].numeric !== null}
									You scored <strong>{$stats.wodScores[0].raw}</strong>
									({$stats.wodScores[0].tier.toUpperCase()}).
									Here's the full distribution.
								{:else}
									No score entered for this workout.
								{/if}
							</p>
						</div>
					</div>

					<!-- Step 4: WOD 2 -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>{genderMeta.wods[1].name} — Deep Dive</h2>
							<p>
								{#if $stats.wodScores[1].numeric !== null}
									You scored <strong>{$stats.wodScores[1].raw}</strong>
									({$stats.wodScores[1].tier.toUpperCase()}).
								{:else}
									No score entered for this workout.
								{/if}
							</p>
						</div>
					</div>

					<!-- Step 5: WOD 3 -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>{genderMeta.wods[2].name} — Deep Dive</h2>
							<p>
								{#if $stats.wodScores[2].numeric !== null}
									You scored <strong>{$stats.wodScores[2].raw}</strong>
									({$stats.wodScores[2].tier.toUpperCase()}).
								{:else}
									No score entered for this workout.
								{/if}
							</p>
						</div>
					</div>

					<!-- Step 6: Height scatter -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>Score vs Height</h2>
							<p>
								Does height correlate with performance? Each dot is an athlete.
								Your position is highlighted.
							</p>
							<label class="toggle-label">
								<input type="checkbox" bind:checked={scatterColorByAge} />
								Color by age group
							</label>
						</div>
					</div>

					<!-- Step 7: Weight scatter -->
					<div class="step scroll-step">
						<div class="step-content">
							<h2>Score vs Weight</h2>
							<p>
								How does body weight relate to Open performance? Find yourself among
								{allData.scatterWeight[$gender].n_total.toLocaleString()} athletes with recorded weight.
							</p>
						</div>
					</div>
				</div>

				<!-- Sticky chart column -->
				<div class="chart-column" bind:this={chartContainer}>
					<div class="sticky-chart">
						<div class="chart-panel">
							{#if activeStep === 0}
								<PercentileGauge
									percentile={$stats.overallPercentile}
									label="All {genderMeta.label}"
									total={genderMeta.total_athletes}
								/>
							{:else if activeStep === 1}
								<PercentileGauge
									percentile={$stats.ageGroupPercentile}
									label="Age {$ageBracket}"
									subtitle="{genderMeta.label}, {$ageBracket}"
								/>
							{:else if activeStep === 2}
								<BoxPlot
									data={getWodAgeDist(1)}
									userBracket={$ageBracket}
									userValue={$stats.wodScores[0].numeric}
									scoreType={$stats.wodScores[0].scoreType ?? 'reps'}
									title="{genderMeta.wods[0].name} Score by Age Group (Rx)"
									width={chartWidth}
								/>
							{:else if activeStep === 3}
								<DistributionHistogram
									distribution={getWodDist(1, $stats.wodScores[0].tier, $stats.wodScores[0].scoreType)}
									userValue={$stats.wodScores[0].numeric}
									scoreType={$stats.wodScores[0].scoreType}
									title="{genderMeta.wods[0].name} Score Distribution ({$stats.wodScores[0].tier.toUpperCase()})"
									width={chartWidth}
								/>
							{:else if activeStep === 4}
								<DistributionHistogram
									distribution={getWodDist(2, $stats.wodScores[1].tier, $stats.wodScores[1].scoreType)}
									userValue={$stats.wodScores[1].numeric}
									scoreType={$stats.wodScores[1].scoreType}
									title="{genderMeta.wods[1].name} Score Distribution ({$stats.wodScores[1].tier.toUpperCase()})"
									width={chartWidth}
								/>
							{:else if activeStep === 5}
								<DistributionHistogram
									distribution={getWodDist(3, $stats.wodScores[2].tier, $stats.wodScores[2].scoreType)}
									userValue={$stats.wodScores[2].numeric}
									scoreType={$stats.wodScores[2].scoreType}
									title="{genderMeta.wods[2].name} Score Distribution ({$stats.wodScores[2].tier.toUpperCase()})"
									width={chartWidth}
								/>
							{:else if activeStep === 6}
								<ScatterCanvas
									data={allData.scatterHeight[$gender]}
									userX={null}
									userY={$stats.overallPercentile !== null
										? Math.round(genderMeta.total_athletes * (1 - ($stats.overallPercentile ?? 50) / 100))
										: null}
									xLabel="Height (cm)"
									colorByAge={scatterColorByAge}
									width={chartWidth}
									height={400}
								/>
							{:else if activeStep === 7}
								<ScatterCanvas
									data={allData.scatterWeight[$gender]}
									userX={null}
									userY={$stats.overallPercentile !== null
										? Math.round(genderMeta.total_athletes * (1 - ($stats.overallPercentile ?? 50) / 100))
										: null}
									xLabel="Weight (kg)"
									colorByAge={scatterColorByAge}
									width={chartWidth}
									height={400}
								/>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Footer -->
		<footer class="footer container">
			<p>
				Data from the {$year} CrossFit Open via the public API.
				{(allData.meta.men.total_athletes + allData.meta.women.total_athletes).toLocaleString()} athletes analyzed.
			</p>
		</footer>
	{/if}
</main>

<style>
	main {
		min-height: 100vh;
	}

	/* Hero */
	.hero {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem 0;
		background: linear-gradient(180deg, #0f172a 0%, #1a1a2e 50%, #0f172a 100%);
	}

	.hero-inner {
		text-align: center;
		max-width: 560px;
	}

	.hero-title {
		font-size: clamp(2rem, 6vw, 3.5rem);
		font-weight: 800;
		background: linear-gradient(135deg, #818cf8, #f59e0b);
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		margin-bottom: 0.25rem;
	}

	.year-selector {
		display: flex;
		gap: 0.5rem;
		justify-content: center;
		margin-bottom: 1rem;
	}

	.year-pill {
		padding: 0.4rem 1.1rem;
		border-radius: 999px;
		border: 1px solid var(--bg-tertiary);
		background: transparent;
		color: var(--text-secondary);
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.year-pill:hover {
		border-color: var(--accent);
		color: var(--text-primary);
	}

	.year-pill.active {
		background: var(--accent);
		border-color: var(--accent);
		color: white;
	}

	.hero-desc {
		color: var(--text-muted);
		margin-bottom: 2rem;
		font-size: 0.95rem;
	}

	/* Input card */
	.input-card {
		background: var(--bg-secondary);
		border-radius: var(--radius);
		padding: 1.5rem;
		border: 1px solid var(--bg-tertiary);
		text-align: left;
	}

	.input-row {
		margin-bottom: 1rem;
	}

	.input-label {
		display: block;
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 0.4rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.input-hint {
		font-weight: 400;
		text-transform: none;
		letter-spacing: 0;
		color: var(--text-muted);
		font-size: 0.75rem;
	}

	.pill-group {
		display: flex;
		gap: 0;
		border-radius: var(--radius-sm);
		overflow: hidden;
		border: 1px solid var(--bg-tertiary);
		width: fit-content;
	}

	.pill {
		padding: 0.5rem 1.25rem;
		background: transparent;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 500;
		transition: all 0.15s ease;
	}

	.pill:hover {
		background: var(--bg-tertiary);
	}

	.pill.active {
		background: var(--accent);
		color: white;
	}

	.pill-small .pill {
		padding: 0.35rem 0.75rem;
		font-size: 0.8rem;
	}

	.text-input {
		background: var(--bg-primary);
		border: 1px solid var(--bg-tertiary);
		border-radius: var(--radius-sm);
		padding: 0.6rem 0.9rem;
		color: var(--text-primary);
		font-size: 1rem;
		width: 100%;
		transition: border-color 0.15s ease;
	}

	.text-input:focus {
		outline: none;
		border-color: var(--accent);
	}

	.age-input {
		max-width: 100px;
	}

	.wod-inputs {
		display: flex;
		gap: 0.75rem;
		align-items: center;
	}

	.score-input {
		flex: 1;
		max-width: 200px;
		font-variant-numeric: tabular-nums;
	}

	.cta-button {
		width: 100%;
		padding: 0.85rem;
		margin-top: 0.5rem;
		background: linear-gradient(135deg, var(--accent), #7c3aed);
		color: white;
		border: none;
		border-radius: var(--radius-sm);
		font-size: 1.05rem;
		font-weight: 700;
		cursor: pointer;
		transition: opacity 0.15s ease, transform 0.1s ease;
	}

	.cta-button:hover:not(:disabled) {
		opacity: 0.9;
		transform: translateY(-1px);
	}

	.cta-button:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	/* Scroll section */
	.scroll-section {
		padding: 4rem 0;
	}

	.chart-panel {
		background: var(--bg-secondary);
		border-radius: var(--radius);
		padding: 1.5rem;
		border: 1px solid var(--bg-tertiary);
		width: 100%;
		min-height: 300px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	/* Toggle */
	.toggle-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 1rem;
		color: var(--text-muted);
		font-size: 0.85rem;
		cursor: pointer;
	}

	.toggle-label input {
		accent-color: var(--accent);
		width: 16px;
		height: 16px;
	}

	/* Footer */
	.footer {
		text-align: center;
		padding: 3rem 0;
		color: var(--text-muted);
		font-size: 0.85rem;
		border-top: 1px solid var(--bg-tertiary);
	}

	@media (max-width: 639px) {
		.input-card {
			padding: 1rem;
		}

		.wod-inputs {
			flex-direction: column;
			align-items: stretch;
			gap: 0.5rem;
		}

		.score-input {
			max-width: 100%;
		}

		.pill-small {
			width: 100%;
		}

		.pill-small .pill {
			flex: 1;
			text-align: center;
		}
	}
</style>
