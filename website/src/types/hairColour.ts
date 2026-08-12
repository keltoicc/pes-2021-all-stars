import type { HairColourPreset } from "../enums/hairColourPreset";

export interface HairColour {
    preset: HairColourPreset;
    red?: number;
    green?: number;
    blue?: number;
}