import type { Position } from "../enums/position";
import type { Positions } from "./positions";

export interface PlayerVersion {
    // Identity
    id: number;
    player: number;
    slug: string;

    // Stage
    version: string;
    fromSeason: number;
    toSeason: number;

    // Gameplay
    mainPosition: Position;
    positions: Positions;

    overall?: number;

    // Visual
    shirtName?: string;
    nationalShirtName?: string;
}