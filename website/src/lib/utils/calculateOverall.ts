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
    0, 0, 0, 0, 0, 5, 0, 0, 7, 17, 17, 7, 14,
];

const BALL_CONTROL = [
    0, 0, 7, 7, 10, 11, 15, 15, 11, 19, 19, 8, 10,
];

const DRIBBLING = [
    0, 0, 6, 6, 6, 7, 17, 17, 8, 15, 15, 7, 5,
];

const TIGHT_POSSESSION = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 0, 5,
];

const LOW_PASS = [
    0, 0, 0, 0, 8, 11, 0, 0, 10, 0, 0, 8, 0,
];

const LOFTED_PASS = [
    0, 0, 7, 7, 9, 10, 12, 12, 8, 9, 9, 0, 0,
];

const FINISHING = [
    0, 0, 0, 0, 0, 0, 0, 0, 8, 11, 11, 7, 14,
];

const SET_PIECE_TAKING = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const CURL = [
    0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0,
];

const HEADING = [
    0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,
];

const DEFENSIVE_AWARENESS = [
    0, 12, 8, 8, 5, 0, 0, 0, 0, 0, 0, 0, 0,
];

const TACKLING = [
    0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const AGGRESSION = [
    0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const KICKING_POWER = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const SPEED = [
    0, 0, 8, 8, 0, 0, 24, 24, 0, 15, 15, 7, 0,
];

const ACCELERATION = [
    0, 0, 7, 7, 0, 0, 21, 21, 0, 15, 15, 9, 0,
];

const PHYSICAL_CONTACT = [
    9, 10, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 6,
];

const BALANCE = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const JUMP = [
    9, 10, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const STAMINA = [
    0, 7, 8, 8, 8, 9, 13, 13, 0, 6, 6, 0, 0,
];

const GK_AWARENESS = [
    21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CATCHING = [
    13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REACH = [
    21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REFLEXES = [
    14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CLEARING = [
    13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const WEAK_FOOT_ACCURACY = [
    59, 59, 59, 59, 59, 59, 56, 56, 59, 47, 47, 59, 59,
];

const POSITION_BONUS = [
    0, 32, 36, 36, 41, 47, 8, 8, 48, 10, 10, 47, 42,
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
    player: Player,
): number {
    if (player.height === undefined) {
        throw new Error(
            `Cannot calculate Overall: player ${player.id} (${player.name}) has no height.`,
        );
    }

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

    const weakFootAccuracy = Math.floor(
        (WEAK_FOOT_ACCURACY[position] * playerVersion.weakFootAccuracy) / 3 + 40,
    );

    total = add(
        total,
        weakFootAccuracy,
        4,
    );

    total = Math.floor(total / 100);

    return total + POSITION_BONUS[position];
}