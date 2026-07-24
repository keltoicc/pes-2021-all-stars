import { Repository } from "./repository";

import { teams } from "../data/teams";

import type { Team } from "../types/team";

class TeamRepository extends Repository<Team> {

    getAllSorted(): Team[] {

        return [...this.getAll()].sort((a, b) =>
            a.name.localeCompare(b.name)
        );

    }

}

export const teamRepository = new TeamRepository(teams);