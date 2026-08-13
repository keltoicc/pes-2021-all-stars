import type { Hairstyle } from "./hairstyle";
import type { Physique } from "./physique";

export interface Appearance {
    id: number;
    hairstyle?: Hairstyle;
    physique?: Physique;
}