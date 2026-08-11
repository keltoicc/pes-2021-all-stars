import type { Boot } from "../../types/boot";

const modules = import.meta.glob("../../data/boots/*.json", {
    eager: true,
});

const boots: Boot[] = Object.values(modules)
    .map((module: any) => module.default as Boot)
    .sort((a, b) => {
        const brandComparison = a.brand.localeCompare(b.brand);

        if (brandComparison !== 0) {
            return brandComparison;
        }

        return a.model.localeCompare(b.model);
    });

const bootsById = new Map<number, Boot>();
const bootsBySlug = new Map<string, Boot>();

for (const boot of boots) {
    bootsById.set(boot.id, boot);
    bootsBySlug.set(boot.slug, boot);
}

export default class BootRepository {

    static getAll(): Boot[] {
        return boots;
    }

    static getById(id: number): Boot | undefined {
        return bootsById.get(id);
    }

    static getBySlug(slug: string): Boot | undefined {
        return bootsBySlug.get(slug);
    }

}