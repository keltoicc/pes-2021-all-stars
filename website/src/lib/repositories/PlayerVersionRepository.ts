import type { PlayerVersion } from "../../types/playerVersion";

const playerVersions = import.meta.glob("../../data/playerVersions/*.json", {
    eager: true,
}) as Record<string, { default: PlayerVersion }>;

class PlayerVersionRepository {

    private readonly playerVersions: PlayerVersion[];

    constructor() {
        this.playerVersions = Object.values(playerVersions).map(module => module.default);
    }

    getAll(): PlayerVersion[] {
        return this.playerVersions;
    }

    getById(id: number): PlayerVersion | undefined {
        return this.playerVersions.find(playerVersion => playerVersion.id === id);
    }

    getBySlug(slug: string): PlayerVersion | undefined {
        return this.playerVersions.find(playerVersion => playerVersion.slug === slug);
    }

    getByPlayer(playerId: number): PlayerVersion[] {
        return this.playerVersions.filter(playerVersion => playerVersion.player === playerId);
    }

}

export default new PlayerVersionRepository();