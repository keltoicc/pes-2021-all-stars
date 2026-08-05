import type { PreferredFoot } from "../enums/preferredFoot";

export interface Player {
    id: number;

    name: string;
    slug: string;

    country: number;

    birthDate?: string;

    preferredFoot?: PreferredFoot;
}