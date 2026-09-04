import fs from "node:fs";
import path from "node:path";

interface SearchIndexEntry {
    type: "player" | "team" | "country";
    id: number;
    name: string;
    slug: string;
}

interface SourceData {
    id: number;
    name: string;
    slug: string;
}

const sources = [
    {
        type: "player" as const,
        directory: "src/data/players"
    },
    {
        type: "team" as const,
        directory: "src/data/teams"
    },
    {
        type: "country" as const,
        directory: "src/data/countries"
    }
];

const outputDirectory = "public/data";
const outputFile = path.join(outputDirectory, "search-index.json");

const index: SearchIndexEntry[] = [];

let hasErrors = false;

for (const source of sources) {

    const directory = path.resolve(source.directory);

    const files = fs
        .readdirSync(directory)
        .filter(file => file.endsWith(".json"));

    const ids = new Map<number, string>();
    const slugs = new Map<string, string>();

    for (const file of files) {

        const filePath = path.join(directory, file);
        const data = JSON.parse(fs.readFileSync(filePath, "utf-8")) as SourceData;

        /*
         * Validate required fields
         */

        if (
            typeof data.id !== "number" ||
            typeof data.name !== "string" ||
            typeof data.slug !== "string"
        ) {
            console.error(
                `[ERROR] Invalid search data in ${filePath}`
            );

            hasErrors = true;
            continue;
        }

        /*
         * Check duplicate ID
         */

        const previousIdFile = ids.get(data.id);

        if (previousIdFile) {

            console.error(
                `[ERROR] Duplicate ${source.type} ID ${data.id}:\n` +
                `  - ${previousIdFile}\n` +
                `  - ${filePath}`
            );

            hasErrors = true;

        } else {

            ids.set(data.id, filePath);

        }

        /*
         * Check duplicate slug
         */

        const previousSlugFile = slugs.get(data.slug);

        if (previousSlugFile) {

            console.error(
                `[ERROR] Duplicate ${source.type} slug "${data.slug}":\n` +
                `  - ${previousSlugFile}\n` +
                `  - ${filePath}`
            );

            hasErrors = true;

        } else {

            slugs.set(data.slug, filePath);

        }

        index.push({
            type: source.type,
            id: data.id,
            name: data.name,
            slug: data.slug
        });
    }
}

/*
 * Stop the build if invalid data was found.
 */

if (hasErrors) {
    throw new Error(
        "Search index generation failed because invalid data was found."
    );
}

/*
 * Generate search index
 */

fs.mkdirSync(outputDirectory, {
    recursive: true
});

fs.writeFileSync(
    outputFile,
    JSON.stringify(index, null, 4) + "\n",
    "utf-8"
);

console.log(
    `Search index generated: ${index.length} entries.`
);