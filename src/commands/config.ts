import { ApplicationCommandOptionType, CommandInteraction } from 'discord.js'
import { Discord, Guard, Slash, SlashGroup, SlashOption } from 'discordx'
import { getOrCreateGuild } from '../data/guild.js'
import config from '../config.js'
import { IsGuildUser, PermissionGuard } from '@discordx/utilities'

@Discord()
@SlashGroup({ name: 'config', description: 'Configuration settings' })
@SlashGroup('config')
export class ConfigRoot {}

@Discord()
@Guard(PermissionGuard(['Administrator']))
@Guard(IsGuildUser)
@SlashGroup({
  name: 'currency',
  description: 'Currency settings',
  root: 'config',
})
@SlashGroup('currency', 'config')
export class ConfigCurrency {
  @Slash({ description: 'Set currency name (singular & plural)' })
  name(
    @SlashOption({
      name: 'singular',
      description: 'Singular name for the currency (e.g. Coin)',
      type: ApplicationCommandOptionType.String,
      required: true,
    })
    singular: string,

    @SlashOption({
      name: 'plural',
      description: 'Plural name for the currency (e.g. Coins)',
      type: ApplicationCommandOptionType.String,
      required: true,
    })
    plural: string,
    interaction: CommandInteraction,
  ) {
    if (!interaction.guildId)
      return interaction.reply({
        content: config.commandOnlyInGuildWarning,
        flags: ['Ephemeral'],
      })
    getOrCreateGuild({
      id: interaction.guildId,
      currencyName: singular,
      currencyNamePlural: plural,
    })
    return interaction.reply(
      `Currency name set to:\nSingular: **${singular}**\nPlural: **${plural}**`,
    )
  }

  @Slash({ description: 'Set currency emoji' })
  async emoji(
    @SlashOption({
      name: 'value',
      description: 'The currency emoji',
      type: ApplicationCommandOptionType.String,
    })
    value: string,
    interaction: CommandInteraction,
  ) {
    if (!interaction.guildId)
      return interaction.reply({
        content: config.commandOnlyInGuildWarning,
        flags: ['Ephemeral'],
      })
    // TODO: check if value is an emoji <:_:ID>
    getOrCreateGuild({ id: interaction.guildId, currencyEmoji: value })
    return interaction.reply(`Currency emoji set to ${value}`)
  }
}

/* 
@Discord()
@SlashGroup({ name: "channel", description: "Channel settings", root: "config" })
@SlashGroup("channel", "config")
export class ConfigChannel {
    @Slash({ description: "Set shop channel" })
    shop(
        @SlashOption({
            name: "channel",
            description: "Channel to use as shop",
            type: ApplicationCommandOptionType.Channel,
            channelTypes: [ChannelType.GuildText],
        })
        channel: any,
        interaction: CommandInteraction
    ) {
        return interaction.reply(`Shop channel set to <#${channel.id}>`)
    }

    @Slash({ description: "Set logs channel" })
    logs(
        @SlashOption({
            name: "channel",
            description: "Channel to use for logs",
            type: ApplicationCommandOptionType.Channel,
            channelTypes: [ChannelType.GuildText],
        })
        channel: any,
        interaction: CommandInteraction
    ) {
        return interaction.reply(`Logs channel set to <#${channel.id}>`)
    }
} */
