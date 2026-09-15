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
    186, 136, 49, 49, 61, 37, 12, 12, 37, 49, 49, 62, 99,
];

const OFFENSIVE_AWARENESS = [
    0, 14, 61, 61, 61, 98, 98, 98, 171, 159, 159, 173, 210,
];

const BALL_CONTROL = [
    13, 27, 86, 86, 122, 171, 171, 171, 196, 159, 159, 210, 123,
];

const DRIBBLING = [
    0, 14, 61, 61, 37, 98, 110, 122, 122, 159, 159, 123, 62,
];

const TIGHT_POSSESSION = [
    0, 0, 37, 37, 24, 49, 73, 61, 73, 86, 86, 86, 37,
];

const LOW_PASS = [
    27, 41, 61, 61, 122, 208, 135, 135, 196, 73, 73, 99, 37,
];

const LOFTED_PASS = [
    40, 68, 147, 147, 122, 159, 196, 196, 159, 98, 98, 74, 12,
];

const FINISHING = [
    0, 27, 24, 24, 37, 73, 86, 86, 184, 159, 159, 284, 358,
];

const SET_PIECE_TAKING = [
    0, 14, 24, 24, 12, 12, 24, 24, 12, 12, 12, 12, 12,
];

const CURL = [
    0, 14, 24, 24, 12, 12, 24, 24, 12, 12, 12, 12, 12,
];

const HEADING = [
    0, 55, 24, 24, 61, 24, 12, 12, 24, 24, 24, 25, 62,
];

const DEFENSIVE_AWARENESS = [
    13, 286, 147, 147, 220, 86, 49, 49, 24, 12, 12, 0, 0,
];

const TACKLING = [
    0, 191, 86, 86, 122, 86, 24, 24, 24, 12, 12, 12, 12,
];

const AGGRESSION = [
    0, 82, 37, 37, 98, 37, 12, 12, 12, 12, 12, 12, 12,
];

const KICKING_POWER = [
    53, 27, 24, 24, 49, 73, 24, 24, 73, 61, 61, 99, 123,
];

const SPEED = [
    13, 136, 220, 220, 61, 61, 196, 196, 98, 220, 220, 86, 99,
];

const ACCELERATION = [
    40, 150, 184, 184, 61, 86, 159, 159, 86, 159, 159, 99, 123,
];

const PHYSICAL_CONTACT = [
    80, 204, 98, 98, 122, 49, 24, 24, 24, 37, 37, 37, 86,
];

const BALANCE = [
    0, 0, 24, 24, 12, 24, 61, 61, 24, 73, 73, 74, 86,
];

const JUMP = [
    133, 109, 37, 37, 37, 12, 12, 12, 12, 24, 24, 37, 62,
];

const STAMINA = [
    0, 68, 196, 196, 196, 196, 147, 147, 86, 49, 49, 49, 37,
];

const GK_AWARENESS = [
    279, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CATCHING = [
    226, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REACH = [
    226, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_REFLEXES = [
    173, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const GK_CLEARING = [
    173, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

const WEAK_FOOT_ACCURACY = [
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
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

    total += (player.height - 111 - 25) * HEIGHT[position];

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
        (59 * playerVersion.weakFootAccuracy) / 3 + 40,
    );

    total = add(
        total,
        weakFootAccuracy,
        WEAK_FOOT_ACCURACY[position],
    );

    return Math.floor((total + 500) / 1000);
}