import type { Tier, UserScoreInput } from './types';

export function parseUserScore(input: string, tier: Tier): UserScoreInput {
	const s = input.trim();
	if (!s) return { raw: s, tier, numeric: null, scoreType: null };

	// Time: M:SS or MM:SS
	const timeMatch = s.match(/^(\d{1,2}):(\d{2})$/);
	if (timeMatch) {
		return {
			raw: s,
			tier,
			numeric: parseInt(timeMatch[1]) * 60 + parseInt(timeMatch[2]),
			scoreType: 'time'
		};
	}

	// Reps: plain number or "N reps"
	const repsMatch = s.match(/^(\d+)(\s*reps)?$/i);
	if (repsMatch) {
		return {
			raw: s,
			tier,
			numeric: parseInt(repsMatch[1]),
			scoreType: 'reps'
		};
	}

	return { raw: s, tier, numeric: null, scoreType: null };
}

export function formatScore(value: number, scoreType: 'reps' | 'time'): string {
	if (scoreType === 'time') {
		const mins = Math.floor(value / 60);
		const secs = value % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}
	return `${value} reps`;
}

export function formatPercentile(p: number): string {
	if (p >= 99) return 'Top 1%';
	if (p >= 95) return `Top ${100 - p}%`;
	return `Top ${100 - p}%`;
}
