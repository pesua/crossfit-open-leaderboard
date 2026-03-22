import { writable, derived } from 'svelte/store';
import type { Gender, Tier, UserScoreInput, AllData } from '$lib/data/types';
import { parseUserScore } from '$lib/data/scores';
import { computePercentile, computeOverallPercentile } from '$lib/data/percentile';

export const gender = writable<Gender>('men');
export const age = writable<number>(30);
export const region = writable<string>('');

// Raw score strings for each WOD
export const wod1Raw = writable('');
export const wod2Raw = writable('');
export const wod3Raw = writable('');

// Tier for each WOD
export const wod1Tier = writable<Tier>('rx');
export const wod2Tier = writable<Tier>('rx');
export const wod3Tier = writable<Tier>('rx');

// Parsed scores (derived)
export const wod1Score = derived([wod1Raw, wod1Tier], ([$raw, $tier]) => parseUserScore($raw, $tier));
export const wod2Score = derived([wod2Raw, wod2Tier], ([$raw, $tier]) => parseUserScore($raw, $tier));
export const wod3Score = derived([wod3Raw, wod3Tier], ([$raw, $tier]) => parseUserScore($raw, $tier));

function getAgeBracket(age: number): string {
	if (age <= 17) return '16-17';
	if (age <= 24) return '18-24';
	if (age <= 29) return '25-29';
	if (age <= 34) return '30-34';
	if (age <= 39) return '35-39';
	if (age <= 44) return '40-44';
	if (age <= 49) return '45-49';
	return '50+';
}

export const ageBracket = derived(age, ($age) => getAgeBracket($age));

export interface UserStats {
	overallPercentile: number | null;
	ageGroupPercentile: number | null;
	wodPercentiles: (number | null)[];
	wodScores: UserScoreInput[];
	ageBracket: string;
	hasScores: boolean;
}

export function createDerivedStats(data: AllData) {
	return derived(
		[gender, age, ageBracket, wod1Score, wod2Score, wod3Score],
		([$gender, $age, $bracket, $w1, $w2, $w3]) => {
			const perc = data.percentiles[$gender];
			const scores = [$w1, $w2, $w3];
			const hasScores = scores.some((s) => s.numeric !== null);

			// Per-WOD percentiles
			const wodPercentiles = scores.map((s, i) => {
				if (s.numeric === null || s.scoreType === null) return null;
				const wodKey = `wod_${i + 1}` as keyof typeof perc;
				const wodPerc = perc[wodKey] as { rx: Record<string, any>; scaled: Record<string, any> };
				const bp = wodPerc[s.tier]?.[s.scoreType]?.all;
				if (!bp) return null;

				// For reps, higher is better. For time, lower is better.
				const lowerIsBetter = s.scoreType === 'time';
				return computePercentile(s.numeric, bp, lowerIsBetter);
			});

			// Overall percentile: approximate by averaging WOD percentiles if we have all 3
			let overallPercentile: number | null = null;
			const validPercentiles = wodPercentiles.filter((p) => p !== null);
			if (validPercentiles.length > 0) {
				overallPercentile = Math.round(
					validPercentiles.reduce((a, b) => a + b, 0) / validPercentiles.length
				);
			}

			// Age group percentile
			let ageGroupPercentile: number | null = null;
			if (validPercentiles.length > 0) {
				const agePercentiles = scores.map((s, i) => {
					if (s.numeric === null || s.scoreType === null) return null;
					const wodKey = `wod_${i + 1}` as keyof typeof perc;
					const wodPerc = perc[wodKey] as { rx: Record<string, any>; scaled: Record<string, any> };
					const bp = wodPerc[s.tier]?.[s.scoreType]?.[$bracket];
					if (!bp) return null;
					const lowerIsBetter = s.scoreType === 'time';
					return computePercentile(s.numeric, bp, lowerIsBetter);
				});
				const validAge = agePercentiles.filter((p) => p !== null);
				if (validAge.length > 0) {
					ageGroupPercentile = Math.round(
						validAge.reduce((a, b) => a + b, 0) / validAge.length
					);
				}
			}

			return {
				overallPercentile,
				ageGroupPercentile,
				wodPercentiles,
				wodScores: scores,
				ageBracket: $bracket,
				hasScores
			} satisfies UserStats;
		}
	);
}
