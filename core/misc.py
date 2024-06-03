import json
import datetime
import discord
import random
from PIL import ImageDraw, Image, ImageFont
from core.emojis import *
import io
import db
import json

THRESHOLD = 30

ranks = json.load(open("assets/ranks.json")).items() # TODO make a ranks class to handle this
messages = {}
warnings = {}
has_penalty = {}

def calc_message(user_messages):
    heat = 0
    time_diff = None
    if user_messages:
        length, timestamp = user_messages[-1]
        heat += length
        if len(user_messages) > 1:
            prev_length, prev_timestamp = user_messages[-2]
            heat += prev_length
            time_diff = (timestamp - prev_timestamp).total_seconds()
            heat = heat * max(int(THRESHOLD - time_diff),1)
    return heat,time_diff 

def calc_cooldown(message):
    timediff = datetime.timedelta(seconds=0)
    current_time = datetime.datetime.now(datetime.UTC) 
    while calc_message([message, (1, current_time + timediff)])[0] > 20000:
        timediff += datetime.timedelta(seconds=1)
    return int(timediff.total_seconds())

async def broadcast(message: discord.Message,content,title=None,view=None,thumb_url=None):
  embed = discord.Embed(description=content,title=title)
  embed.set_thumbnail(url=thumb_url)
  try:
    dm = await message.author.create_dm()
    await dm.send(embed=embed,view=view)
  except Exception as e:
    print(e)
    await message.channel.send(embed=embed,view=view)

def loadbarimage(percentage: int) -> io.BytesIO:
    width, height = 400, 400
    image = Image.new("RGBA", (width, height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(image) 
    size = [(width / 2) - 190, (height / 2) - 190, (width / 2) + 190, (height / 2) + 190]
    draw.arc(size, -90, (percentage / 100) * 360 - 90, fill="#AF01E7", width=35)
    font = ImageFont.truetype('assets/Beyonders.ttf', 70)
    draw.text([115,70], "XP", font=font, fill="white")
    draw.text([80,180], f"{round(percentage)}%", font=font, fill="white")
    io_bytes = io.BytesIO()
    image.save(io_bytes, format="PNG")
    io_bytes.seek(0)
    return io_bytes

def winchance(percentage) -> bool:
    return random.random() < percentage / 100

def stripCodeBlocks(content: str) -> str:
  while "```" in content:
    start = content.find("```")
    end = content.find("```", start + 3)
    content = content[:start] + content[end + 3:]
  return content

def isauthor(message: discord.Message, member: discord.Member) -> bool:
    return message.author == member

def isprivileged(member: discord.Member) -> bool:
  '''
  Check if a member is privileged (is a booster, is an admin, or is the owner of the guild)
  '''
  return member.premium_since or member.guild_permissions.administrator or member.guild.owner == member

def hascoins(amount: int, message: str) -> bool:
    async def predicate(interaction: discord.Interaction):
        balance = db.users.get('coins',interaction.user.id)
        if balance < amount:
            await interaction.response.send_message(f"You need at least {COINS_EMOJI} ` {amount} Coins ` to {message}.",ephemeral=True)
            return False
        return True
    return discord.app_commands.check(predicate)

def calculate_boosts(slots):
    boosts = {
        COINS_EMOJI: ["coin boost", 4002],
        LEVEL_EMOJI: ["XP boost", 4001],
        SANDCLOCK_EMOJI: ["Shop discount", 4003]
    }
    boost_durations = {1: 5*60, 2: 10*60}

    matched = [slot for slot in slots if slot in boosts]
    unique_matches = set(matched)
    return matched, unique_matches, boosts, boost_durations