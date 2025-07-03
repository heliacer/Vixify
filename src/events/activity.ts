import { EmbedBuilder } from "discord.js"
import type { ArgsOf, Client } from "discordx"
import { Discord, On } from "discordx"

@Discord()
export class ActivityMonitor {
  @On()
  async messageCreate([message]: ArgsOf<"messageCreate">, client: Client): Promise<void> {
    if (message.author.bot) return
    if (!message.guild) return

    console.log(message.content.length)
    /// ...


  }
}
