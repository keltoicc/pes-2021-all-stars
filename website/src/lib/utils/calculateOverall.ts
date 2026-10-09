import type { Player } from "../../types/player";
import type { PlayerVersion } from "../../types/playerVersion";
import { Position } from "../../enums/position";

const POSITION_INDEX: Record<Position, number> = {
    [Position.GK]: 0,

    [Position.SW]: 1,
    [Position.CB]: 1,
    [Position.RB]: 2,
    [Position.LB]: 3,

    [Position.DMF]: 4,
    [Position.CMF]: 5,
    [Position.RMF]: 6,
    [Position.LMF]: 7,
    [Position.AMF]: 8,

    [Position.RWF]: 9,
    [Position.LWF]: 10,
    [Position.SS]: 11,
    [Position.CF]: 12,
};

const HEIGHT = [
    19, 14, 5, 5, 6, 4, 1, 1, 4, 5, 5, 6, 10,
];

const OFFENSIVE_AWARENESS = [
    0, 4, 8, 9, 10, 9, 11, 7, 13, 16, 14, 11, 24,
];

const BALL_CONTROL = [
    0, 7, 12, 9, 17, 19, 13, 15, 19, 14, 15, 14, 17,
];

const DRIBBLING = [
    0, 4, 8, 9, 11, 13, 14, 14, 14, 14, 14, 12, 9,
];

const TIGHT_POSSESSION = [
    0, 4, 8, 8, 6, 8, 10, 10, 9, 9, 10, 9, 9,
];

const LOW_PASS = [
    0, 4, 3, 5, 14, 18, 10, 8, 16, 6, 7, 14, 4,
];

const LOFTED_PASS = [
    0, 4, 13, 13, 16, 17, 11, 13, 14, 11, 12, 10, 6,
];

const FINISHING = [
    0, 5, 6, 5, 5, 6, 6, 6, 14, 11, 12, 13, 25,
];

const HEADING = [
    0, 17, 5, 4, 3, 3, 4, 3, 5, 5, 4, 7, 7,
];

const SET_PIECE_TAKING = [
    0, 4, 5, 5, 5, 4, 4, 4, 4, 5, 3, 7, 4,
];

const CURL = [
    0, 5, 5, 5, 12, 5, 7, 5, 4, 5, 6, 3, 5,
];

const SPEED = [
    0, 9, 14, 13, 5, 7, 19, 16, 8, 14, 14, 11, 7,
];

const ACCELERATION = [
    0, 5, 12, 13, 7, 8, 17, 17, 8, 13, 13, 16, 8,
];

const KICKING_POWER = [
    0, 4, 4, 4, 4, 4, 4, 5, 5, 6, 6, 7, 6,
];

const JUMP = [
    10, 17, 10, 11, 9, 5, 4, 4, 5, 4, 4, 4, 6,
];

const PHYSICAL_CONTACT = [
    10, 17, 10, 11, 11, 6, 4, 7, 6, 7, 7, 6, 10,
];

const BALANCE = [
    0, 5, 8, 7, 6, 6, 6, 5, 8, 9, 7, 7, 6,
];

const STAMINA = [
    0, 12, 14, 14, 14, 16, 12, 13, 7, 10, 9, 10, 6,
];

const DEFENSIVE_AWARENESS = [
    0, 20, 13, 15, 9, 8, 5, 4, 4, 4, 6, 4, 5,
];

const TACKLING = [
    0, 15, 10, 9, 7, 5, 5, 4, 5, 6, 5, 4, 6,
];

const AGGRESSION = [
    0, 9, 7, 7, 5, 4, 4, 5, 4, 4, 4, 5, 4,
];

const GK_AWARENESS = [
    24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CATCHING = [
    16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CLEARING = [
    16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REFLEXES = [
    17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REACH = [
    25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const WEAK_FOOT_ACCURACY = [
    0, 9, 32, 30, 7, 8, 25, 32, 21, 26, 26, 14, 20,
];

const POSITION_BONUS = [
    8, -9, -9, -8, -8, -9, -9, -8, -9, -8, -8, -9, -10,
];

function add(
    total: number,
    value: number,
    weight: number,
): number {
    return total + (value - 25) * weight;
}

export function calculateOverall(
    playerVersion: PlayerVersion,
    //player: Player,
): number {
    //if (player.height === undefined) {
    //    throw new Error(
    //        `Cannot calculate Overall: player ${player.id} (${player.name}) has no height.`,
    //    );
    //}

    const position = POSITION_INDEX[playerVersion.mainPosition];

    let total = 0;

    //total += (player.height - 111 - 25) * HEIGHT[position];

    total = add(
        total,
        playerVersion.abilities.offensiveAwareness,
        OFFENSIVE_AWARENESS[position],
    );

    total = add(
        total,
        playerVersion.abilities.ballControl,
        BALL_CONTROL[position],
    );

    total = add(
        total,
        playerVersion.abilities.dribbling,
        DRIBBLING[position],
    );

    total = add(
        total,
        playerVersion.abilities.tightPossession,
        TIGHT_POSSESSION[position],
    );

    total = add(
        total,
        playerVersion.abilities.lowPass,
        LOW_PASS[position],
    );

    total = add(
        total,
        playerVersion.abilities.loftedPass,
        LOFTED_PASS[position],
    );

    total = add(
        total,
        playerVersion.abilities.finishing,
        FINISHING[position],
    );

    total = add(
        total,
        playerVersion.abilities.placeKicking,
        SET_PIECE_TAKING[position],
    );

    total = add(
        total,
        playerVersion.abilities.curl,
        CURL[position],
    );

    total = add(
        total,
        playerVersion.abilities.heading,
        HEADING[position],
    );

    total = add(
        total,
        playerVersion.abilities.defensiveAwareness,
        DEFENSIVE_AWARENESS[position],
    );

    total = add(
        total,
        playerVersion.abilities.ballWinning,
        TACKLING[position],
    );

    total = add(
        total,
        playerVersion.abilities.aggression,
        AGGRESSION[position],
    );

    total = add(
        total,
        playerVersion.abilities.kickingPower,
        KICKING_POWER[position],
    );

    total = add(
        total,
        playerVersion.abilities.speed,
        SPEED[position],
    );

    total = add(
        total,
        playerVersion.abilities.acceleration,
        ACCELERATION[position],
    );

    total = add(
        total,
        playerVersion.abilities.physicalContact,
        PHYSICAL_CONTACT[position],
    );

    total = add(
        total,
        playerVersion.abilities.balance,
        BALANCE[position],
    );

    total = add(
        total,
        playerVersion.abilities.jump,
        JUMP[position],
    );

    total = add(
        total,
        playerVersion.abilities.stamina,
        STAMINA[position],
    );

    total = add(
        total,
        playerVersion.abilities.gkAwareness,
        GK_AWARENESS[position],
    );

    total = add(
        total,
        playerVersion.abilities.gkCatching,
        GK_CATCHING[position],
    );

    total = add(
        total,
        playerVersion.abilities.gkReach,
        GK_REACH[position],
    );

    total = add(
        total,
        playerVersion.abilities.gkReflexes,
        GK_REFLEXES[position],
    );

    total = add(
        total,
        playerVersion.abilities.gkClearing,
        GK_CLEARING[position],
    );

    //const weakFootAccuracy = Math.floor(
    //    (WEAK_FOOT_ACCURACY[position] * playerVersion.weakFootAccuracy) / 3 + 40,
    //);

    total = add(
        total,
        WEAK_FOOT_ACCURACY[position],
        playerVersion.weakFootAccuracy,
    );

    total = Math.floor(total / 100);

    return total + POSITION_BONUS[position];
}