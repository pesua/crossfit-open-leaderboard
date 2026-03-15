import type { AllData, Meta, PercentileData, Distributions, AgeDistributions, ScatterData } from '$lib/data/types';

export const prerender = true;

export async function load({ fetch }): Promise<{ data: AllData }> {
	const json = async <T>(path: string): Promise<T> => {
		const res = await fetch(path);
		return res.json() as Promise<T>;
	};

	const [
		meta,
		percMen, percWomen,
		distMen, distWomen,
		ageMen, ageWomen,
		shMen, shWomen,
		swMen, swWomen
	] = await Promise.all([
		json<Meta>('/data/meta.json'),
		json<PercentileData>('/data/percentiles.men.json'),
		json<PercentileData>('/data/percentiles.women.json'),
		json<Distributions>('/data/distributions.men.json'),
		json<Distributions>('/data/distributions.women.json'),
		json<AgeDistributions>('/data/age_distributions.men.json'),
		json<AgeDistributions>('/data/age_distributions.women.json'),
		json<ScatterData>('/data/scatter_height.men.json'),
		json<ScatterData>('/data/scatter_height.women.json'),
		json<ScatterData>('/data/scatter_weight.men.json'),
		json<ScatterData>('/data/scatter_weight.women.json'),
	]);

	return {
		data: {
			meta,
			percentiles: { men: percMen, women: percWomen },
			distributions: { men: distMen, women: distWomen },
			ageDistributions: { men: ageMen, women: ageWomen },
			scatterHeight: { men: shMen, women: shWomen },
			scatterWeight: { men: swMen, women: swWomen },
		}
	};
}
