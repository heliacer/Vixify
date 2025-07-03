import prisma from "./prisma.js"

function extractUserId(input: string): string | null {
    return input.match(/^<@!?(\d+)>$/)?.[1] || input.match(/^\d{17,20}$/)?.[0] || null
}

async function getOrCreateGuild(guildId: string) {
    return prisma.guild.upsert({
        where: { id: guildId },
        update: {},
        create: {
            id: guildId
        }
    })
}

async function getOrCreateUser(userId: string) {
    return prisma.user.upsert({
        where: { id: userId },
        update: {},
        create: {
            id: userId,
            coins: 0
        }
    })
}

async function getOrCreateGuildUser(userId: string, guildId: string) {
    await getOrCreateGuild(guildId)
    await getOrCreateUser(userId)

    return prisma.guildUser.upsert({
        where: {
            userId_guildId: {
                userId: userId,
                guildId: guildId
            }
        },
        update: {},
        create: {
            userId: userId,
            guildId: guildId,
            xp: 0,
            rank: 0
        }
    })
}

export { getOrCreateGuild, getOrCreateUser, getOrCreateGuildUser, extractUserId }