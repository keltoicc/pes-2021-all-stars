export interface Team {
    id: number;
    name: string;
    shortName?: string;
    slug: string;

    country: number;
    city?: string;
    founded?: number;

    crest: string;

}