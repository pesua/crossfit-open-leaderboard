import type { PercentileBreakpoints } from './types';

const LEVELS = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 96, 97, 98, 99];

/**
 * Given a user's value and precomputed percentile breakpoints,
 * return the percentile (0-100) the user falls at.
 *
 * For "lower is better" metrics (rank, time), a low value = high percentile.
 * For "higher is better" (reps), a high value = high percentile.
 */
export function computePercentile(
	value: number,
	bp: PercentileBreakpoints,
	lowerIsBetter: boolean
): number {
	const values = LEVELS.map((l) => bp[`p${l}`] as number);

	// Find where value falls in the breakpoints
	if (lowerIsBetter) {
		// Lower value = better = higher percentile
		// p1 = best performers (low rank), p99 = worst (high rank)
		if (value <= values[0]) return 99; // better than p1
		if (value >= values[values.length - 1]) return 1; // worse than p99

		for (let i = 0; i < values.length - 1; i++) {
			if (value <= values[i + 1]) {
				const t = (value - values[i]) / (values[i + 1] - values[i]);
				const pctile = LEVELS[i] + t * (LEVELS[i + 1] - LEVELS[i]);
				return Math.round(100 - pctile); // invert: low rank = high percentile
			}
		}
		return 1;
	} else {
		// Higher value = better = higher percentile
		// p1 = worst performers (low reps), p99 = best (high reps)
		if (value >= values[values.length - 1]) return 99;
		if (value <= values[0]) return 1;

		for (let i = 0; i < values.length - 1; i++) {
			if (value <= values[i + 1]) {
				const t = (value - values[i]) / (values[i + 1] - values[i]);
				const pctile = LEVELS[i] + t * (LEVELS[i + 1] - LEVELS[i]);
				return Math.round(pctile);
			}
		}
		return 99;
	}
}

/**
 * Compute overall percentile from summed WOD ranks.
 * Overall score = sum of ranks → lower is better.
 */
export function computeOverallPercentile(
	overallScore: number,
	bp: PercentileBreakpoints
): number {
	return computePercentile(overallScore, bp, true);
}
