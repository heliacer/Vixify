import prisma from "./prisma.js"

export interface GuildUpdate {
    id: string,
    currencyName?: string,
    currencyNamePlural?: string,
    currencyEmoji?: string
}

export async function getOrCreateGuild(data: GuildUpdate) {
    const { id, ...fields } = data

    return prisma.guild.upsert({
        where: { id },
        update: { ...fields },
        create: { id }
    })
}