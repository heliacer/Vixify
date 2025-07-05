import prisma from "./prisma.js"

export async function getUserCurrenciesSlim(userId: string) {
    return prisma.guildUser.findMany({
        where: { userId },
        select: {
            guildId: true,
            currency: true,
            guild: {
                select: {
                    currencyName: true,
                    currencyNamePlural: true,
                    currencyEmoji: true
                }
            }
        }
    })
}

export async function getUserRankSlim(userId: string) {
    return prisma.guildUser.findMany({
        where: { userId },
        select: {
            xp: true,
            rank: true,
        }
    })
}
