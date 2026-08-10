import type { Squad } from "../../types/squad";

const modules = import.meta.glob("../../data/squads/*.json", {
    eager: true,
});

const squads: Squad[] = Object.values(modules)
    .map((module: any) => module.default as Squad)
    .sort((a, b) => {
        if (a.team !== b.team) {
            return a.team - b.team;
        }

        return a.name.localeCompare(b.name);
    });

const squadsById = new Map<number, Squad>();
const squadsBySlug = new Map<string, Squad>();
const squadsByTeam = new Map<number, Squad[]>();

for (const squad of squads) {
    squadsById.set(squad.id, squad);
    squadsBySlug.set(squad.slug, squad);

    const teamSquads = squadsByTeam.get(squad.team) ?? [];

    teamSquads.push(squad);

    squadsByTeam.set(squad.team, teamSquads);
}

export default class SquadRepository {

    static getAll(): Squad[] {
        return squads;
    }

    static getById(id: number): Squad | undefined {
        return squadsById.get(id);
    }

    static getBySlug(slug: string): Squad | undefined {
        return squadsBySlug.get(slug);
    }

    static getByTeam(teamId: number): Squad[] {
        return squadsByTeam.get(teamId) ?? [];
    }

}