import { ChannelType, UserMention } from "discord.js"
import { Discord, SimpleCommand, SimpleCommandMessage, SimpleCommandOption, SimpleCommandOptionType } from "discordx"
import prisma from "../data/prisma.js"
import { extractUserId, getOrCreateGuildUser, getOrCreateUser } from "../data/helpers.js"

// Just some testing command, will do coin fetching later
@Discord()
export class GetData {
    @SimpleCommand()
    async getdata(
        @SimpleCommandOption({
            name: "user",
            type: SimpleCommandOptionType.String
        }) userArg: string | undefined,
        command: SimpleCommandMessage
    ) {
        const userId = userArg ? extractUserId(userArg) : command.message.author.id
        if (!userId) return await command.message.reply(`${userId} is not a valid user.`)
        if (!command.message.guildId) return await command.message.reply("this command only works in guilds.")

        await getOrCreateUser(userId)
        await getOrCreateGuildUser(userId, command.message.guildId)

        const channel = command.message.channel
        if (channel.type === ChannelType.GuildText) {
            const allUsers = await prisma.user.findMany()
            const allGuildUsers = await prisma.guildUser.findMany()
            channel.send(`
                allUsers: \`\`\`json\n${JSON.stringify(allUsers, null, 2)}\n\`\`\`\nallGuildUsers: \`\`\`json\n${JSON.stringify(allGuildUsers, null, 2)}\n\`\`\`
            `)
        }
    }
}