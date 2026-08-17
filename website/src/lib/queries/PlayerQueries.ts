import PlayerRepository from "../repositories/PlayerRepository";
import PlayerVersionRepository from "../repositories/PlayerVersionRepository";

import type { Player } from "../../types/player";
import type { Position } from "../../enums/position";

export default class PlayerQueries {

    static getByPosition(position: Position): Player[] {

        const playerIds = new Set<number>();

        const versions = PlayerVersionRepository.getAll();

        for (const version of versions) {

            if (position in version.positions) {
                playerIds.add(version.player);
            }

        }

        return PlayerRepository
            .getAll()
            .filter(player => playerIds.has(player.id));

    }

}