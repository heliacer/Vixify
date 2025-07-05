export default function getLevelFromXp(xp: number, a = 100, d = 50): number {
    const A = d / 2
    const B = a - d / 2
    const C = -xp

    const discriminant = B * B - 4 * A * C
    if (discriminant < 0) return 1

    const n = (-B + Math.sqrt(discriminant)) / (2 * A)
    return Math.max(1, Math.floor(n))
}
