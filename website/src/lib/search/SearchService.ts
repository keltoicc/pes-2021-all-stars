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

function getMatchScore(
    name: string,
    query: string
): number {

    const words = name.split(/\s+/);

    // 1. Exact name match
    if (name === query) {
        return 600;
    }

    // 2. Exact word match
    if (words.some(word => word === query)) {
        return 500;
    }

    // 3. Name starts with query
    if (name.startsWith(query)) {
        return 400;
    }

    // 4. A word starts with query
    if (words.some(word => word.startsWith(query))) {
        return 300;
    }

    // 5. Name contains query
    if (name.includes(query)) {
        return 200;
    }

    return 0;
}

function getPositionBonus(
    name: string,
    query: string
): number {

    const position = name.indexOf(query);

    if (position === -1) {
        return 0;
    }

    /*
     * The earlier the match appears,
     * the higher the bonus.
     *
     * Maximum: 100
     */
    return Math.max(0, 100 - position);
}

function getStartBonus(
    name: string,
    query: string
): number {

    return name.startsWith(query) ? 50 : 0;
}

function getLengthBonus(
    name: string
): number {

    /*
     * Prefer shorter names when all other
     * relevance criteria are equivalent.
     *
     * Maximum: 20
     */
    return Math.max(0, 20 - name.length);
}

function getScore(
    name: string,
    query: string
): number {

    const matchScore = getMatchScore(name, query);

    if (matchScore === 0) {
        return 0;
    }

    const positionBonus =
        getPositionBonus(name, query);

    const startBonus =
        getStartBonus(name, query);

    const lengthBonus =
        getLengthBonus(name);

    return (
        matchScore +
        positionBonus +
        startBonus +
        lengthBonus
    );
}

export default class SearchService {

    static async search(
        query: string
    ): Promise<SearchResult[]> {

        const normalizedQuery = normalize(query);

        if (!normalizedQuery) {
            return [];
        }

        const results: Array<
            SearchResult & {
                score: number;
            }
        > = [];

        for (const player of PlayerRepository.getAll()) {

            const name = normalize(player.name);
            const score = getScore(name, normalizedQuery);

            if (score > 0) {
                results.push({
                    type: "player",
                    id: player.id,
                    name: player.name,
                    slug: player.slug,
                    score
                });
            }
        }

        for (const team of TeamRepository.getAll()) {

            const name = normalize(team.name);
            const score = getScore(name, normalizedQuery);

            if (score > 0) {
                results.push({
                    type: "team",
                    id: team.id,
                    name: team.name,
                    slug: team.slug,
                    score
                });
            }
        }

        for (const country of CountryRepository.getAll()) {

            const name = normalize(country.name);
            const score = getScore(name, normalizedQuery);

            if (score > 0) {
                results.push({
                    type: "country",
                    id: country.id,
                    name: country.name,
                    slug: country.slug,
                    score
                });
            }
        }

        results.sort((a, b) => {

            // 1. Relevance
            if (b.score !== a.score) {
                return b.score - a.score;
            }

            // 2. Alphabetical order
            return a.name.localeCompare(b.name);
        });

        return results.map(
            ({ score, ...result }) => result
        );
    }
}