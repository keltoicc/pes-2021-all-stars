import type { Position } from "../enums/position";
import type { Positions } from "./positions";
import type { Abilities } from "./abilities";
import type { PlayingSkills } from "../enums/playingSkill";

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
    abilities: Abilities;
    weakFootUsage: number;
    weakFootAccuracy: number;
    form: number;
    injuryResistance: number;

    playingSkills?: PlayingSkills[];

    overall?: number;

    // Visual
    shirtName?: string;
    nationalShirtName?: string;
}