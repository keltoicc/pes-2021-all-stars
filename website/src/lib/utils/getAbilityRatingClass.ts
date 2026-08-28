export function getAbilityRatingClass(value: number): string {
    if (value >= 95) {
        return "excellent";
    }

    if (value >= 85) {
        return "very-good";
    }

    if (value >= 75) {
        return "good";
    }

    return "low";
}