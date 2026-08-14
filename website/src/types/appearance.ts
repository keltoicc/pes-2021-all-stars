import type { Hairstyle } from "./hairstyle";
import type { Face } from "./face";
import type { Physique } from "./physique";

export interface Appearance {
    id: number;
    hairstyle?: Hairstyle;
    face?: Face;
    physique?: Physique;
}