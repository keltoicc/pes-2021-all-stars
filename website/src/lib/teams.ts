import { teams } from "../data/teams";
import type { Team } from "../types/team";

export function getTeams(): Team[] {
    return teams;
}