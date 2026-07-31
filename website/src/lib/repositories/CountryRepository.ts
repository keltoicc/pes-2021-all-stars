import type { Country } from "../../types/country";

const modules = import.meta.glob("../../data/countries/*.json", {
    eager: true,
});

const countries: Country[] = Object.values(modules)
    .map((module: any) => module.default as Country)
    .sort((a, b) => a.name.localeCompare(b.name));

const countriesById = new Map<number, Country>();
const countriesBySlug = new Map<string, Country>();

for (const country of countries) {
    countriesById.set(country.id, country);
    countriesBySlug.set(country.slug, country);
}

export default class CountryRepository {

    static getAll(): Country[] {
        return countries;
    }

    static getById(id: number): Country | undefined {
        return countriesById.get(id);
    }

    static getBySlug(slug: string): Country | undefined {
        return countriesBySlug.get(slug);
    }

}