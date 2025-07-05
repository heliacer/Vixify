import { getOrCreateGuild } from "./guild.js"
import prisma from "./prisma.js"
import { getOrCreateUser } from "./user.js"

export interface GuildUserUpdate {
    userId: string,
    guildId: string,
    currency?: number,
    xp?: number,
    rank?: number
}

export async function getOrCreateGuildUser(data: GuildUserUpdate) {
    const { userId, guildId, ...fields } = data
    await getOrCreateGuild({ id: guildId })
    await getOrCreateUser({ id: userId })

    return prisma.guildUser.upsert({
        where: { userId_guildId: { userId, guildId } },
        update: fields,
        create: {
            userId,
            guildId,
            currency: 0,
            xp: 0,
            rank: 0,
            ...fields
        }
    })
}
