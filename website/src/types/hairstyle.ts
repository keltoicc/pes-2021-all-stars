import type { HairstyleOverallStyle } from "../enums/hairstyleOverallStyle";
import type { HairstyleOverallLength } from "../enums/hairstyleOverallLength";
import type { HairstyleFrontStyle } from "../enums/hairstyleFrontStyle";
import type { HairstyleFrontParted } from "../enums/hairstyleFrontParted";
import type { HairstyleFrontForeheadWidth } from "../enums/hairstyleFrontForeheadWidth";
import type { HairstyleSideBackStyle } from "../enums/hairstyleSideBackStyle";
import type { HairstyleHairColourAccessoryAccessoryColour } from "../enums/hairstyleHairColourAccessoryAccessoryColour";

import type { HairColour } from "./hairColour"

export interface Hairstyle {
    overall: {
        style?: HairstyleOverallStyle;
        length?: HairstyleOverallLength;
        waveLevel?: number;
        hairVariation?: number;
    };

    front: {
        style?: HairstyleFrontStyle;
        parted?: HairstyleFrontParted;
        hairline?: number;
        foreheadWidth?: HairstyleFrontForeheadWidth;
    };

    sideBack: {
        style?: HairstyleSideBackStyle;
        cropped?: number;
    };

    hairColourAccessory: {
        hairColour: HairColour;
        accessory?: boolean;
        accessoryColour?: HairstyleHairColourAccessoryAccessoryColour;
    };
}