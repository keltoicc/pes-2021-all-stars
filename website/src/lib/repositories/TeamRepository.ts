import type { Team } from "../../types/team";

const modules = import.meta.glob("../../data/teams/*.json", {
    eager: true,
});

const teams = Object.values(modules).map(
    (module: any) => module.default as Team
);

const teamsBySlug = new Map(
    teams.map(team => [team.slug, team])
);

export class TeamRepository {

    static getAll(): Team[] {
        return teams;
    }

    static getBySlug(slug: string): Team | undefined {
        return teamsBySlug.get(slug);
    }

}