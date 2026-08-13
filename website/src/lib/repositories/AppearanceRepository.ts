import type { Appearance } from "../../types/appearance";

const modules = import.meta.glob("../../data/appearances/*.json", {
    eager: true,
});

const appearances: Appearance[] = Object.values(modules)
    .map((module: any) => module.default as Appearance);

const appearancesById = new Map<number, Appearance>();

for (const appearance of appearances) {
    appearancesById.set(appearance.id, appearance);
}

export default class AppearanceRepository {

    static getAll(): Appearance[] {
        return appearances;
    }

    static getById(id: number): Appearance | undefined {
        return appearancesById.get(id);
    }

}