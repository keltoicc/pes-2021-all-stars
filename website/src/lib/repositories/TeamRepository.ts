import type { Team } from "../../types/team";

const modules = import.meta.glob("../../data/teams/*.json", {
    eager: true,
});

const teams: Team[] = Object.values(modules)
    .map((module: any) => module.default as Team)
    .sort((a, b) => a.name.localeCompare(b.name));

const teamsById = new Map<number, Team>();
const teamsBySlug = new Map<string, Team>();

for (const team of teams) {
    teamsById.set(team.id, team);
    teamsBySlug.set(team.slug, team);
}

export default class TeamRepository {
    static getAll(): Team[] {
        return teams;
    }

    static getByCountry(countryId: number): Team[] {

        const result: Team[] = [];

        for (const team of teams) {

            if (team.country === countryId) {
                result.push(team);
            }

        }

        return result;

    }

    static getById(id: number): Team | undefined {
        return teamsById.get(id);
    }

    static getBySlug(slug: string): Team | undefined {
        return teamsBySlug.get(slug);
    }
}