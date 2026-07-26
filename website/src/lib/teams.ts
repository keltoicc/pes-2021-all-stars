import type { Team } from "../types/team";

const teamModules = import.meta.glob("../data/teams/*.json", {
    eager: true,
});

export class TeamRepository {

    static getAll(): Team[] {

        return Object.values(teamModules).map(
            (module: any) => module.default as Team
        );

    }

    static getBySlug(slug: string): Team | undefined {

        return this.getAll().find(team => team.slug === slug);

    }

}