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
    0, 0, 0, 0, 0, 10, 0, 0, 14, 17, 17, 14, 28,
];

const BALL_CONTROL = [
    0, 0, 14, 14, 20, 22, 15, 15, 22, 19, 19, 16, 20,
];

const DRIBBLING = [
    0, 0, 12, 12, 12, 14, 17, 17, 16, 15, 15, 14, 10,
];

const TIGHT_POSSESSION = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 0, 10,
];

const LOW_PASS = [
    0, 0, 0, 0, 16, 22, 0, 0, 20, 0, 0, 16, 0,
];

const LOFTED_PASS = [
    0, 0, 14, 14, 18, 20, 12, 12, 16, 9, 9, 0, 0,
];

const FINISHING = [
    0, 0, 0, 0, 0, 0, 0, 0, 16, 11, 11, 14, 28,
];

const SET_PIECE_TAKING = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const CURL = [
    0, 0, 0, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0,
];

const HEADING = [
    0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8,
];

const DEFENSIVE_AWARENESS = [
    0, 24, 16, 16, 10, 0, 0, 0, 0, 0, 0, 0, 0,
];

const TACKLING = [
    0, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const AGGRESSION = [
    0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const KICKING_POWER = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const SPEED = [
    0, 0, 16, 16, 0, 0, 24, 24, 0, 15, 15, 14, 0,
];

const ACCELERATION = [
    0, 0, 14, 14, 0, 0, 21, 21, 0, 15, 15, 9, 0,
];

const PHYSICAL_CONTACT = [
    18, 20, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 12,
];

const BALANCE = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const JUMP = [
    18, 20, 14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const STAMINA = [
    0, 14, 16, 16, 16, 18, 13, 13, 0, 6, 6, 0, 0,
];

const GK_AWARENESS = [
    27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CATCHING = [
    22, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REACH = [
    22, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REFLEXES = [
    17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CLEARING = [
    17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const WEAK_FOOT_ACCURACY = [
    50, 50, 50, 50, 50, 50, 56, 56, 50, 47, 47, 50, 50,
];

const POSITION_BONUS = [
    0, 16, 18, 18, 21, 24, 8, 8, 24, 10, 10, 24, 21,
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