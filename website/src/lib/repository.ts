export abstract class Repository<
    T extends { id: string; slug: string }
> {

    protected readonly items: T[];

    constructor(items: T[]) {
        this.items = items;
    }

    getAll(): T[] {
        return this.items;
    }

    getById(id: string): T | undefined {
        return this.items.find(item => item.id === id);
    }

    getBySlug(slug: string): T | undefined {
        return this.items.find(item => item.slug === slug);
    }

}