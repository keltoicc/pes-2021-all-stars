export type PositionCategory =
    | "goalkeeper"
    | "defender"
    | "midfielder"
    | "forward";

export function getPositionCategory(
    position: string
): PositionCategory {

    switch (position) {

        case "GK":
            return "goalkeeper";

        case "SW":
        case "CB":
        case "LB":
        case "RB":
            return "defender";

        case "DMF":
        case "CMF":
        case "RMF":
        case "LMF":
        case "AMF":
            return "midfielder";

        case "LWF":
        case "RWF":
        case "SS":
        case "CF":
            return "forward";

        default:
            throw new Error(
                `Unknown player position: ${position}`
            );
    }
}