import type { Player } from "../../types/player";

const players = import.meta.glob("../../data/players/*.json", {
    eager: true,
}) as Record<string, { default: Player }>;

class PlayerRepository {

    private readonly players: Player[];

    constructor() {
        this.players = Object.values(players).map(module => module.default);
    }

    getAll(): Player[] {
        return this.players;
    }

    getById(id: number): Player | undefined {
        return this.players.find(player => player.id === id);
    }

    getBySlug(slug: string): Player | undefined {
        return this.players.find(player => player.slug === slug);
    }

}

export default new PlayerRepository();