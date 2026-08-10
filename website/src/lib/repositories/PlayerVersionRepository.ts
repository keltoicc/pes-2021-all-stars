import type { PlayerVersion } from "../../types/playerVersion";

const modules = import.meta.glob("../../data/playerVersions/*.json", {
    eager: true,
});

const playerVersions: PlayerVersion[] = Object.values(modules)
    .map((module: any) => module.default as PlayerVersion)
    .sort((a, b) => a.player - b.player);

const playerVersionsById = new Map<number, PlayerVersion>();
const playerVersionsBySlug = new Map<string, PlayerVersion>();
const playerVersionsByPlayer = new Map<number, PlayerVersion[]>();

for (const playerVersion of playerVersions) {

    playerVersionsById.set(playerVersion.id, playerVersion);
    playerVersionsBySlug.set(playerVersion.slug, playerVersion);

    const playerVersionsForPlayer =
        playerVersionsByPlayer.get(playerVersion.player) ?? [];

    playerVersionsForPlayer.push(playerVersion);

    playerVersionsByPlayer.set(
        playerVersion.player,
        playerVersionsForPlayer
    );
}

export default class PlayerVersionRepository {

    static getAll(): PlayerVersion[] {
        return playerVersions;
    }

    static getById(id: number): PlayerVersion | undefined {
        return playerVersionsById.get(id);
    }

    static getBySlug(slug: string): PlayerVersion | undefined {
        return playerVersionsBySlug.get(slug);
    }

    static getByPlayer(playerId: number): PlayerVersion[] {
        return playerVersionsByPlayer.get(playerId) ?? [];
    }

}