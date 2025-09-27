import { Discord, Slash, SlashOption } from 'discordx'
import { EmbedBuilder } from '@discordjs/builders'
import {
  ApplicationCommandOptionType,
  CommandInteraction,
  GuildMember,
  User,
} from 'discord.js'
import emojis from '../emojis.js'
import { getUserCurrenciesSlim } from '../data/guilduserslim.js'

@Discord()
export class Wallet {
  @Slash({ description: 'How the world sees your worth', name: 'wallet' })
  async wallet(
    @SlashOption({
      description: 'user',
      name: 'user',
      required: false,
      type: ApplicationCommandOptionType.User,
    })
    user: User | GuildMember | undefined,
    interaction: CommandInteraction,
  ): Promise<void> {
    const discordUser = user ? user : interaction.user
    const guildUserRecords = await getUserCurrenciesSlim(discordUser.id)
    const sortedRecords = guildUserRecords.sort((a, b) => {
      if (a.guildId === interaction.guildId) return -1
      if (b.guildId === interaction.guildId) return 1
      return 0
    })

    const walletContent =
      sortedRecords
        .map((record) => {
          const emoji = record.guild.currencyEmoji || emojis.gelt
          const coins = record.currency
          const guildName =
            interaction.client.guilds.cache.get(record.guildId)?.name ||
            'Server'

          const coinName =
            coins === 1
              ? record.guild.currencyName
              : record.guild.currencyNamePlural || `${guildName} Coins`

          return `${emoji} \` ${coins} \` ${coinName}`
        })
        .join('\n') || 'This wallet is empty...'
    const embed = new EmbedBuilder()
      .setAuthor({
        name: discordUser.displayName,
        iconURL: discordUser.displayAvatarURL(),
      })
      .setDescription(walletContent)
    await interaction.reply({ embeds: [embed] })
  }
}
