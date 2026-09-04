export type SearchResultType =
    | "player"
    | "team"
    | "country";

export interface SearchResult {
    type: SearchResultType;
    id: number;
    name: string;
    slug: string;
}