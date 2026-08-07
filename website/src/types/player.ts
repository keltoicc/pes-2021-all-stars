import type { PreferredFoot } from "../enums/preferredFoot";
import type { CareerEntry } from "./careerEntry";

export interface Player {
    id: number;

    name: string;
    slug: string;

    birthDate?: string;
    birthPlace?: string;

    country: number;
    secondCountry?: number;

    height?: number;

    preferredFoot?: PreferredFoot;

    career?: CareerEntry[];

    //statistics?: CareerStatistics;

    //honours?: Honour[];
}