import type { Glove } from "../../types/glove";

const modules = import.meta.glob("../../data/gloves/*.json", {
    eager: true,
});

const gloves: Glove[] = Object.values(modules)
    .map((module: any) => module.default as Glove)
    .sort((a, b) => {
        const brandComparison = a.brand.localeCompare(b.brand);

        if (brandComparison !== 0) {
            return brandComparison;
        }

        return a.model.localeCompare(b.model);
    });

const glovesById = new Map<number, Glove>();
const glovesBySlug = new Map<string, Glove>();

for (const glove of gloves) {
    glovesById.set(glove.id, glove);
    glovesBySlug.set(glove.slug, glove);
}

export default class GloveRepository {

    static getAll(): Glove[] {
        return gloves;
    }

    static getById(id: number): Glove | undefined {
        return glovesById.get(id);
    }

    static getBySlug(slug: string): Glove | undefined {
        return glovesBySlug.get(slug);
    }

}