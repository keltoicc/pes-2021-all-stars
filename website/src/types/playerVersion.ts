import type { Position } from "../enums/position";
import type { Positions } from "./positions";
import type { Abilities } from "./abilities";
import type { PlayingSkills } from "../enums/playingSkills";
import type { ComPlayingStyles } from "../enums/comPlayingStyles";
import type { PlayingStyle } from "../enums/playingStyle";

export interface PlayerVersion {
    // Identity
    id: number;
    player: number;
    slug: string;

    // Stage
    version: string;
    fromSeason: number;
    toSeason: number;
    weight?: number;

    // Gameplay
    playingStyle?: PlayingStyle;
    mainPosition: Position;
    positions: Positions;
    abilities: Abilities;
    weakFootUsage: number;
    weakFootAccuracy: number;
    form: number;
    injuryResistance: number;

    playingSkills?: PlayingSkills[];
    comPlayingStyles?: ComPlayingStyles[];

    overall?: number;

    // Visual
    shirtName?: string;
    nationalShirtName?: string;
}