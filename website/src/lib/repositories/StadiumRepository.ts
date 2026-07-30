import type { Stadium } from "../../types/stadium";

const modules = import.meta.glob("../../data/stadiums/*.json", {
    eager: true,
});

const stadiums: Stadium[] = Object.values(modules)
    .map((module: any) => module.default as Stadium)
    .sort((a, b) => a.name.localeCompare(b.name));

const stadiumsById = new Map<number, Stadium>();
const stadiumsBySlug = new Map<string, Stadium>();

for (const stadium of stadiums) {
    stadiumsById.set(stadium.id, stadium);
    stadiumsBySlug.set(stadium.slug, stadium);
}

export default class StadiumRepository {

    static getAll(): Stadium[] {
        return stadiums;
    }

    static getById(id: number): Stadium | undefined {
        return stadiumsById.get(id);
    }

    static getBySlug(slug: string): Stadium | undefined {
        return stadiumsBySlug.get(slug);
    }

}