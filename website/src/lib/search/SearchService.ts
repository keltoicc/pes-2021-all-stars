import PlayerRepository from "../repositories/PlayerRepository";
import TeamRepository from "../repositories/TeamRepository";
import CountryRepository from "../repositories/CountryRepository";

import type { SearchResult } from "../../types/search";

function normalize(value: string): string {
    return value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

export default class SearchService {

    static async search(query: string): Promise<SearchResult[]> {

        const normalizedQuery = normalize(query);

        if (!normalizedQuery) {
            return [];
        }

        const results: SearchResult[] = [];

        for (const player of PlayerRepository.getAll()) {

            const name = normalize(player.name);

            if (name.includes(normalizedQuery)) {
                results.push({
                    type: "player",
                    id: player.id,
                    name: player.name,
                    slug: player.slug
                });
            }

        }

        for (const team of TeamRepository.getAll()) {

            const name = normalize(team.name);

            if (name.includes(normalizedQuery)) {
                results.push({
                    type: "team",
                    id: team.id,
                    name: team.name,
                    slug: team.slug
                });
            }

        }

        for (const country of CountryRepository.getAll()) {

            const name = normalize(country.name);

            if (name.includes(normalizedQuery)) {
                results.push({
                    type: "country",
                    id: country.id,
                    name: country.name,
                    slug: country.slug
                });
            }

        }

        return results;
    }

}