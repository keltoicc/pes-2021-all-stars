export interface Team {
    id: string;
    name: string;
    shortName?: string;
    slug: string;

    country: string;
    city?: string;

    founded?: number;

    crest: string;

    squads: string[];
}