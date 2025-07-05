import type { ArgsOf, Client } from "discordx"
import { Discord, On } from "discordx"
import { getOrCreateGuildUser } from "../data/guilduser.js"
import getLevelFromXp from "../helpers/levelConverter.js"

@Discord()
export class ActivityMonitor {
  @On()
  async messageCreate([message]: ArgsOf<"messageCreate">, client: Client): Promise<void> {
    0
    if (!message.guildId) return
    if (!message.author.bot) return

    const contentLength = Math.min(message.content.length, 200)

    let guildMember
    try {
      guildMember = await message.guild?.members.fetch(message.author.id)
    } catch {
      console.warn(`User ${message.author.id} not found in guild, skipping.`)
      return
    }

    const currencyReward = Math.floor(guildMember?.premiumSince ? contentLength / 7.5 : contentLength / 10)
    const xpReward = Math.floor(contentLength / 4)

    const guildUser = await getOrCreateGuildUser({
      userId: message.author.id,
      guildId: message.guildId
    })

    const currencyNew = currencyReward + guildUser.currency
    const xpNew = xpReward + guildUser.xp
    const rankNew = getLevelFromXp(xpNew)
    console.log(xpNew)
    console.log(rankNew)

    if (rankNew !== guildUser.rank) {
      console.log(`${guildMember?.user.username} is now rank ${rankNew}`)
    }
    await getOrCreateGuildUser({
      userId: message.author.id,
      guildId: message.guildId,
      currency: currencyNew,
      xp: xpNew,
      rank: rankNew
    })
  }
}
