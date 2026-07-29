export interface Team {
    id: number;
    name: string;
    shortName?: string;
    slug: string;

    country: string;
    city?: string;
    founded?: number;

    crest: string;

}