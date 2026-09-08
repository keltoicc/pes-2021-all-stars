import type { SearchResult } from "../../types/search";

export default class SearchSuggestionRenderer {

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

        const name = document.createElement("span");
        name.className = "search-suggestion__name";
        name.textContent = result.name;

        const type = document.createElement("span");
        type.className = "search-suggestion__type";
        type.textContent = this.getResultTypeLabel(result.type);

        link.href = this.getResultUrl(result);

        link.appendChild(name);
        link.appendChild(type);

        item.appendChild(link);

        return item;
    }

    private static getResultTypeLabel(
        type: SearchResult["type"]
    ): string {

        switch (type) {

            case "player":
                return "Player";

            case "team":
                return "Team";

            case "country":
                return "Country";
        }
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