import type { AllData, Meta, PercentileData, Distributions, AgeDistributions, ScatterData } from '$lib/data/types';

export const prerender = true;

const YEARS = ['2025', '2026'];

async function loadYear(fetch: typeof globalThis.fetch, y: string): Promise<AllData | null> {
	const base = `/data/${y}`;
	const get = async <T>(path: string): Promise<T | null> => {
		try {
			const res = await fetch(path);
			if (!res.ok) return null;
			return res.json() as Promise<T>;
		} catch {
			return null;
		}
	};

	const [
		meta,
		percMen, percWomen,
		distMen, distWomen,
		ageMen, ageWomen,
		shMen, shWomen,
		swMen, swWomen
	] = await Promise.all([
		get<Meta>(`${base}/meta.json`),
		get<PercentileData>(`${base}/percentiles.men.json`),
		get<PercentileData>(`${base}/percentiles.women.json`),
		get<Distributions>(`${base}/distributions.men.json`),
		get<Distributions>(`${base}/distributions.women.json`),
		get<AgeDistributions>(`${base}/age_distributions.men.json`),
		get<AgeDistributions>(`${base}/age_distributions.women.json`),
		get<ScatterData>(`${base}/scatter_height.men.json`),
		get<ScatterData>(`${base}/scatter_height.women.json`),
		get<ScatterData>(`${base}/scatter_weight.men.json`),
		get<ScatterData>(`${base}/scatter_weight.women.json`),
	]);

	if (!meta || !percMen || !percWomen || !distMen || !distWomen ||
		!ageMen || !ageWomen || !shMen || !shWomen || !swMen || !swWomen) {
		return null;
	}

	return {
		meta,
		percentiles: { men: percMen, women: percWomen },
		distributions: { men: distMen, women: distWomen },
		ageDistributions: { men: ageMen, women: ageWomen },
		scatterHeight: { men: shMen, women: shWomen },
		scatterWeight: { men: swMen, women: swWomen },
	};
}

export async function load({ fetch }): Promise<{ years: Record<string, AllData>; availableYears: string[] }> {
	const results = await Promise.all(YEARS.map(y => loadYear(fetch, y).then(d => [y, d] as const)));
	const years: Record<string, AllData> = {};
	for (const [y, data] of results) {
		if (data) years[y] = data;
	}
	const availableYears = Object.keys(years).sort();
	return { years, availableYears };
}
