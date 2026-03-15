export interface WodMeta {
	index: number;
	name: string;
	rx_count: number;
	scaled_count: number;
	score_types: Record<string, number>;
}

export interface GenderMeta {
	label: string;
	total_athletes: number;
	age_brackets: string[];
	regions: string[];
	wods: WodMeta[];
}

export interface Meta {
	men: GenderMeta;
	women: GenderMeta;
}

export interface PercentileBreakpoints {
	n: number;
	min: number;
	max: number;
	[key: string]: number; // p1, p5, p10, ...
}

export interface PercentileData {
	overall: Record<string, PercentileBreakpoints>;
	wod_1: { rx: Record<string, PercentileBreakpoints>; scaled: Record<string, PercentileBreakpoints> };
	wod_2: { rx: Record<string, PercentileBreakpoints>; scaled: Record<string, PercentileBreakpoints> };
	wod_3: { rx: Record<string, PercentileBreakpoints>; scaled: Record<string, PercentileBreakpoints> };
}

export interface HistogramBin {
	lo: number;
	hi: number;
	count: number;
}

export interface DistributionSet {
	bins: HistogramBin[];
	domain: [number, number];
	n: number;
	score_type?: string;
}

export interface Distributions {
	overall_rank: { all: DistributionSet };
	wod_1: Record<string, DistributionSet>;
	wod_2: Record<string, DistributionSet>;
	wod_3: Record<string, DistributionSet>;
}

export interface AgeDistEntry {
	n: number;
	p5: number;
	p10: number;
	p25: number;
	p50: number;
	p75: number;
	p90: number;
	p95: number;
}

export interface AgeDistributions {
	wod_1: Record<string, AgeDistEntry>;
	wod_2: Record<string, AgeDistEntry>;
	wod_3: Record<string, AgeDistEntry>;
}

export interface ScatterData {
	field: string;
	age_brackets: string[];
	n_sampled: number;
	n_total: number;
	points: [number, number, number][]; // [x, overall_rank, age_bracket_idx]
}

export type Gender = 'men' | 'women';
export type Tier = 'rx' | 'scaled';

export interface UserScoreInput {
	raw: string;
	tier: Tier;
	numeric: number | null;
	scoreType: 'reps' | 'time' | null;
}

export interface AllData {
	meta: Meta;
	percentiles: { men: PercentileData; women: PercentileData };
	distributions: { men: Distributions; women: Distributions };
	ageDistributions: { men: AgeDistributions; women: AgeDistributions };
	scatterHeight: { men: ScatterData; women: ScatterData };
	scatterWeight: { men: ScatterData; women: ScatterData };
}
