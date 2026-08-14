export type HairRelatedColour =
    | {
        type: "Hair";
    }
    | {
        type: "Custom";
        red: number;
        green: number;
        blue: number;
    };