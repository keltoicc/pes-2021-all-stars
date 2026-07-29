import type { Team } from "../../types/team";

const modules = import.meta.glob("../../data/teams/*.json", {
    eager: true,
});

const teams: Team[] = Object.values(modules).map((module: any) => module.default);

export default class TeamRepository {
    static getAll(): Team[] {
        return teams;
    }
}