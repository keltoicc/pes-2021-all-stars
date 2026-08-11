export function calculatePlayerVersionAge(
    birthDate: string,
    fromSeason: number,
    toSeason: number
): { min: number; max: number } {
    const birth = new Date(`${birthDate}T00:00:00`);

    const start = new Date(fromSeason, 6, 1);
    const end = new Date(toSeason + 1, 5, 30);

    let minAge = start.getFullYear() - birth.getFullYear();

    if (
        start.getMonth() < birth.getMonth() ||
        (
            start.getMonth() === birth.getMonth() &&
            start.getDate() < birth.getDate()
        )
    ) {
        minAge--;
    }

    let maxAge = end.getFullYear() - birth.getFullYear();

    if (
        end.getMonth() < birth.getMonth() ||
        (
            end.getMonth() === birth.getMonth() &&
            end.getDate() < birth.getDate()
        )
    ) {
        maxAge--;
    }

    return {
        min: minAge,
        max: maxAge
    };
}