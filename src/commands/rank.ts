import {
  ApplicationCommandOptionType,
  CommandInteraction,
  GuildMember,
  User,
} from 'discord.js'
import { Discord, Slash, SlashOption } from 'discordx'
import { getOrCreateGuildUser } from '../data/guilduser.js'
import config from '../config.js'

@Discord()
export class Rank {
  @Slash({ description: 'Where your class belongs', name: 'rank' })
  async rank(
    @SlashOption({
      description: 'user',
      name: 'user',
      required: false,
      type: ApplicationCommandOptionType.User,
    })
    user: User | GuildMember | undefined,
    interaction: CommandInteraction,
  ) {
    if (!interaction.guildId)
      return interaction.reply({
        content: config.commandOnlyInGuildWarning,
        flags: ['Ephemeral'],
      })
    const discordUser = user ? user : interaction.user
    const guildUser = await getOrCreateGuildUser({
      userId: discordUser.id,
      guildId: interaction.guildId,
    })
    interaction.reply(`rank: ${guildUser.rank}\nxp:${guildUser.xp}`)
  }
}
