import type { SquadMember } from "./squadMember";

export interface Squad {
    id: number;

    team: number;

    name: string;
    slug: string;

    manager?: number;
    stadium?: number;

    members: SquadMember[];
}