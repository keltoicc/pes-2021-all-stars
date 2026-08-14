import type { Continent } from "../../types/continent";

const modules = import.meta.glob("../../data/continents/*.json", {
    eager: true,
});

const continents: Continent[] = Object.values(modules)
    .map((module: any) => module.default as Continent)
    .sort((a, b) => a.name.localeCompare(b.name));

const continentsById = new Map<number, Continent>();
const continentsBySlug = new Map<string, Continent>();

for (const continent of continents) {
    continentsById.set(continent.id, continent);
    continentsBySlug.set(continent.slug, continent);
}

export default class ContinentRepository {

    static getAll(): Continent[] {
        return continents;
    }

    static getById(id: number): Continent | undefined {
        return continentsById.get(id);
    }

    static getBySlug(slug: string): Continent | undefined {
        return continentsBySlug.get(slug);
    }

}