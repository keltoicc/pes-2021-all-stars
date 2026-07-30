import type { Manager } from "../../types/manager";

const modules = import.meta.glob("../../data/managers/*.json", {
    eager: true,
});

const managers: Manager[] = Object.values(modules)
    .map((module: any) => module.default as Manager)
    .sort((a, b) => a.name.localeCompare(b.name));

const managersById = new Map<number, Manager>();
const managersBySlug = new Map<string, Manager>();

for (const manager of managers) {
    managersById.set(manager.id, manager);
    managersBySlug.set(manager.slug, manager);
}

export default class ManagerRepository {

    static getAll(): Manager[] {
        return managers;
    }

    static getById(id: number): Manager | undefined {
        return managersById.get(id);
    }

    static getBySlug(slug: string): Manager | undefined {
        return managersBySlug.get(slug);
    }

}