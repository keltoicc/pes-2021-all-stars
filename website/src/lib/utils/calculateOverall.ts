
import type { PlayerVersion } from "../../types/playerVersion";
import { Position } from "../../enums/position";

type AbilityKey = keyof PlayerVersion["abilities"];

// GK, CB, LB/RB, DMF, CMF, LMF/RMF, AMF, LWF/RWF, SS, CF
type PositionGroup = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;

const POSITION_GROUP: Record<Position, PositionGroup> = {
    [Position.GK]: 0,
    [Position.SW]: 1, // Aproximación: tratar SW como CB
    [Position.CB]: 1,
    [Position.LB]: 2,
    [Position.RB]: 2,
    [Position.DMF]: 3,
    [Position.CMF]: 4,
    [Position.LMF]: 5,
    [Position.RMF]: 5,
    [Position.AMF]: 6,
    [Position.LWF]: 7,
    [Position.RWF]: 7,
    [Position.SS]: 8,
    [Position.CF]: 9,
};

const POSITION_BONUS: Record<Position, number> = {
    [Position.GK]: 8,
    [Position.SW]: 8,
    [Position.CB]: 8,
    [Position.LB]: 9,
    [Position.RB]: 9,
    [Position.DMF]: 9,
    [Position.CMF]: 8,
    [Position.LMF]: 8,
    [Position.RMF]: 8,
    [Position.AMF]: 8,
    [Position.LWF]: 10,
    [Position.RWF]: 10,
    [Position.SS]: 9,
    [Position.CF]: 8,
};

// Cada fila contiene los pesos en el orden de POSITION_GROUP.
const ABILITY_WEIGHTS: {
    key: AbilityKey;
    weights: number[];
}[] = [
    { key: "offensiveAwareness", weights: [0, 0, 6, 7, 5, 7, 14, 17, 15, 31] },
    { key: "ballControl", weights: [0, 0, 9, 18, 23, 15, 23, 19, 19, 23] },
    { key: "dribbling", weights: [0, 0, 9, 10, 16, 17, 17, 15, 13, 9] },
    { key: "tightPossession", weights: [0, 0, 5, 5, 8, 8, 7, 7, 6, 5] },
    { key: "lowPass", weights: [0, 0, 0, 18, 23, 7, 21, 5, 9, 0] },
    { key: "loftedPass", weights: [0, 0, 14, 19, 21, 12, 14, 9, 9, 0] },
    { key: "finishing", weights: [0, 0, 0, 0, 0, 0, 17, 11, 14, 36] },
    { key: "heading", weights: [0, 22, 0, 0, 0, 0, 0, 0, 0, 3] },
    { key: "placeKicking", weights: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] },
    { key: "curl", weights: [0, 0, 0, 12, 0, 4, 0, 0, 0, 0] },
    { key: "speed", weights: [0, 10, 16, 3, 4, 24, 5, 15, 9, 5] },
    { key: "acceleration", weights: [0, 0, 14, 3, 6, 21, 7, 15, 21, 5] },
    { key: "kickingPower", weights: [0, 0, 0, 0, 0, 0, 0, 5, 6, 3] },
    { key: "jump", weights: [11, 19, 11, 5, 0, 0, 0, 0, 0, 3] },
    { key: "physicalContact", weights: [11, 19, 8, 9, 3, 0, 2, 2, 2, 8] },
    { key: "balance", weights: [0, 0, 4, 4, 2, 0, 3, 4, 5, 2] },
    { key: "stamina", weights: [0, 9, 14, 14, 17, 13, 3, 6, 4, 0] },
    { key: "defensiveAwareness", weights: [0, 25, 14, 7, 3, 0, 0, 0, 0, 0] },
    { key: "ballWinning", weights: [0, 17, 8, 3, 0, 0, 0, 0, 0, 0] },
    { key: "aggression", weights: [0, 8, 5, 1, 0, 0, 0, 0, 0, 0] },
];

const WEAK_FOOT_ACCURACY_WEIGHTS = [
    0, 23, 56, 23, 23, 56, 37, 47, 37, 38,
];

const OUTFIELD_ABILITIES: AbilityKey[] = [
    "offensiveAwareness",
    "ballControl",
    "dribbling",
    "tightPossession",
    "lowPass",
    "loftedPass",
    "finishing",
    "heading",
    "placeKicking",
    "curl",
    "speed",
    "acceleration",
    "kickingPower",
    "jump",
    "physicalContact",
    "balance",
    "stamina",
    "defensiveAwareness",
    "ballWinning",
    "aggression",
];

function getGkAwarenessComposite(player: PlayerVersion): number {
    return Math.floor(
        (player.abilities.gkAwareness + player.abilities.gkReach) / 2,
    );
}

function getGkReflexesComposite(player: PlayerVersion): number {
    return Math.floor(
        (
            player.abilities.gkCatching
            + player.abilities.gkClearing
            + player.abilities.gkReflexes
        ) / 3,
    );
}

function calculateWeightedAverage(
    player: PlayerVersion,
    group: PositionGroup,
): number {
    let weightedSum = 0;

    for (const { key, weights } of ABILITY_WEIGHTS) {
        const value = player.abilities[key] as number;
        weightedSum += (value - 25) * weights[group];
    }

    // Los atributos compuestos de portero sustituyen a Awareness y Reflexes.
    weightedSum += (getGkAwarenessComposite(player) - 25)
        * (group === 0 ? 50 : 0);

    weightedSum += (getGkReflexesComposite(player) - 25)
        * (group === 0 ? 48 : 0);

    // Weak Foot Accuracy utiliza 1 como valor base, no 25.
    weightedSum += (
        player.weakFootAccuracy - 1
    ) * WEAK_FOOT_ACCURACY_WEIGHTS[group];

    return Math.floor((weightedSum + 50) / 100);
}

function calculateSumAverage(player: PlayerVersion): number {
    let contributorSum = 0;

    for (const key of OUTFIELD_ABILITIES) {
        contributorSum += player.abilities[key] as number;
    }

    contributorSum += getGkAwarenessComposite(player);
    contributorSum += getGkReflexesComposite(player);

    const scaledAverage = Math.floor((contributorSum * 100) / 22);

    return Math.floor((scaledAverage + 50) / 100);
}

function mapRating(sumAverage: number): number {
    if (sumAverage <= 61) return sumAverage - 9;
    if (sumAverage === 62) return sumAverage - 6;
    if (sumAverage === 63) return sumAverage - 4;
    if (sumAverage === 64) return sumAverage - 2;
    if (sumAverage === 65) return sumAverage;
    if (sumAverage === 66) return sumAverage + 1;
    if (sumAverage === 67) return sumAverage + 3;
    if (sumAverage === 68) return sumAverage + 5;
    if (sumAverage === 69) return sumAverage + 6;
    if (sumAverage === 70) return sumAverage + 7;
    if (sumAverage === 71) return sumAverage + 8;
    if (sumAverage <= 73) return sumAverage + 10;
    if (sumAverage <= 75) return sumAverage + 12;
    if (sumAverage <= 77) return sumAverage + 13;

    return sumAverage + 14;
}

export function calculateOverall(
    playerVersion: PlayerVersion,
): number {
    const position = playerVersion.mainPosition;
    const group = POSITION_GROUP[position];

    if (group === undefined) {
        throw new Error(
            `Unsupported position for Overall calculation: ${position}`,
        );
    }

    const base = calculateWeightedAverage(playerVersion, group)
        + POSITION_BONUS[position];

    // Konami no combina la curva con el cálculo de porteros.
    if (position === Position.GK) {
        return Math.max(40, base);
    }

    const curved = mapRating(calculateSumAverage(playerVersion));

    const finalRating = Math.floor(
        (base * 60 + curved * 40 + 50) / 100,
    );

    return Math.max(40, finalRating);
}
