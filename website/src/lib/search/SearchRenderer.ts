import type { SearchResult } from "../../types/search";

export default class SearchRenderer {

    static render(
        results: SearchResult[],
        container: HTMLElement
    ): void {

        container.innerHTML = "";

        for (const result of results) {

            const item = this.createItem(result);

            container.appendChild(item);
        }
    }

    private static createItem(
        result: SearchResult
    ): HTMLLIElement {

        const item = document.createElement("li");
        const link = document.createElement("a");

        link.textContent = result.name;
        link.href = this.getResultUrl(result);

        item.appendChild(link);

        return item;
    }

    private static getResultUrl(
        result: SearchResult
    ): string {

        switch (result.type) {

            case "player":
                return `${import.meta.env.BASE_URL}players/${result.slug}`;

            case "team":
                return `${import.meta.env.BASE_URL}teams/${result.slug}`;

            case "country":
                return `${import.meta.env.BASE_URL}countries/${result.slug}`;

        }
    }
}