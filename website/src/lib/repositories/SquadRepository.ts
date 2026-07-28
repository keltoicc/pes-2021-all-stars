import type { Squad } from "../../types/squad";

const modules = import.meta.glob("../../data/squads/*.json", {
    eager: true,
});

const squads = Object.values(modules).map(
    (module: any) => module.default as Squad
);

export class SquadRepository {

    static getAll(): Squad[] {
        return squads;
    }

    static getBySlug(slug: string) {

        return squads.find(
            squad => squad.slug === slug
        );

    }

    static getByTeam(teamId: string) {

        return squads.filter(
            squad => squad.teamId === teamId
        );

    }

}