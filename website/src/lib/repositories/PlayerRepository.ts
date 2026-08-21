import type { Player } from "../../types/player";

const modules = import.meta.glob("../../data/players/*.json", {
    eager: true,
});

const players: Player[] = Object.values(modules)
    .map((module: any) => module.default as Player)
    .sort((a, b) => a.name.localeCompare(b.name));

const playersById = new Map<number, Player>();
const playersBySlug = new Map<string, Player>();

for (const player of players) {
    playersById.set(player.id, player);
    playersBySlug.set(player.slug, player);
}

export default class PlayerRepository {

    static getAll(): Player[] {
        return players;
    }

    static getById(id: number): Player | undefined {
        return playersById.get(id);
    }

    static getBySlug(slug: string): Player | undefined {
        return playersBySlug.get(slug);
    }

    static getByCountry(countryId: number): Player[] {
        return players.filter(player =>
            player.country === countryId ||
            player.secondCountry === countryId
        );
    }

    static getCountryIds(): Set<number> {

        const countryIds = new Set<number>();

        for (const player of players) {

            countryIds.add(player.country);

            if (player.secondCountry !== undefined) {
                countryIds.add(player.secondCountry);
            }

        }

        return countryIds;
    }

}