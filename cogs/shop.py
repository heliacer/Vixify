import discord
import db
import config
from discord import ui
from collections import defaultdict
from discord.ext import commands
from core.plugins import Plugin
from typing import List
from core.items import getItemsByType,getItemByID,getNextItemPrice

EMOJIS = {
  "roles" : "<:features:1178989659976642581>",
  "commands" : "<:dev:1178993359738642512>",
  "utilities" : "<:dimension:1178990567812771890>"
}

CONTENT = {
  "roles": [item for item in getItemsByType(["role"]) if item.buyable], 
  "commands": [item for item in getItemsByType(["command"]) if item.buyable],
  "utilities": [item for item in getItemsByType(["utility"]) if item.buyable],
}
    
async def loadpage(interaction: discord.Interaction,page: int,balance: int,sale_percent: int,section: str,selection: List[int] = None,price: int = None):
  embeds = []
  price = price or 0
  itemDisplay = CONTENT[section][6*(page-1):6*page]
  left = True if page == 1 else False

  # Display the selected items
  selection_counts = defaultdict(int)
  if selection:
      for item_id in selection:
          itemname = getItemByID(item_id, CONTENT[section]).name
          selection_counts[itemname] += 1
      selection_lines = [f'{count}x {name}' for name, count in selection_counts.items()]
      selectionvalue = '\n'.join(selection_lines)
  else:
      selectionvalue = "*No items selected*"

  # Check if there are any items left to display
  try:
    right = not bool(CONTENT[section][page * 6])
  except IndexError:
    right = True

  # Create the embed, add Title
  page_embed = discord.Embed(title=f"{EMOJIS[section]} {section.capitalize()}",description="")
  user_roles = [role.id for role in interaction.user.roles]

  # Add the items of display to the embed
  for item in itemDisplay:
    if item.id in user_roles or db.items.get(interaction.user.id,item.id) > 0 if item.ownstack == 1 else False:
      balance_format = f"<:badge:1178949476308766771> `` Bought ``" 
    elif item.price * sale_percent <= balance:
      balance_format = f"<:coins:1172819933093179443> `` {item.price * sale_percent:,.0f} Coins ``" 
    elif item.price * sale_percent > balance:
      balance_format = f"<:disabledcoins:1178939795288891432> *`` {item.price* sale_percent:,.0f} Coins ``*" 
    page_embed.add_field(name=f"{item.emoji} {item.name}",value=f"*{item.description}*\n{balance_format}",inline=True)
  page_embed.set_footer(text=f"Page {page}/{(len(CONTENT[section])+5)//6}")
  embeds.append(page_embed)
  transaction_embed = discord.Embed(description="")

  # Check if there are any items left to buy / bank is undercapitalized / user has enough coins
  next = getNextItemPrice(interaction.user,sale_percent,CONTENT[section])
  if next == 0:
    transaction_embed.add_field(name="<:finishline:1175568414950031471> You've reached the end!",value="**There is nothing left to buy in this section.\nAsk <@955187087911555152> to add more!** ")
  elif next <= balance:
    transaction_embed.add_field(name="<:selection:1172609449593143316> Selected", value=selectionvalue)
    transaction_embed.add_field(name="<:circular:1172609451023405098> Transaction", value=f"__Current Balance__ : `` {balance:,} Coins ``\n__Total Price__ : `` {price:,} Coins ``\n*You'll be left with `` {balance-price:,} Coins ``*")
    if sale_percent < 1:
      if sale_percent == 0.5:
        sale_embed = discord.Embed(title='<:flashsale:1200119986568581160> BANK 50% SALE',description='**THE BANK IS INSOLVENT. GO BUY NOW.\nALL ITEMS ON 50% SALE!!**')
      else:
        sale_embed = discord.Embed(title='<:flashsale:1200119986568581160> BANK 75% SALE',description='**As the Bank is Undercapitalized, Every item is on 75% Sale!\nGo buy now before the Sale goes away!**')
      sale_embed.set_thumbnail(url='https://i.ibb.co/0KxjgjC/box.png')
      embeds.append(sale_embed)
  else:
    transaction_embed.description = "**Save some more coins up for the next item by chatting a bit!**\nCheck your balance with </coins:1172931104890703984>,\nafter gathering enough come back!"
    transaction_embed.title = "<:fireup:1175569234982604870> Aw, not quite yet!" 
  embeds.append(transaction_embed)

  # Send the embeds
  view= MainMenu(interaction,page,left,right,balance,selection,section,price,sale_percent)
  await interaction.edit_original_response(embeds=embeds,view=view)

class MainMenu(ui.View):
  def __init__(self, parent:discord.Interaction, page: int, left_disabled: bool, right_disabled: bool,balance: int,selection: List[int],section: str,price: int,sale_percent: int):
    super().__init__(timeout=None)
    self.parent = parent
    self.page = page
    self.balance = balance
    self.price = price
    self.section = section
    self.sale_percent = sale_percent
    self.selection = selection or []

    buttonrmitem = ui.Button(emoji="<:remove:1175005705422512218>",label="Remove last",custom_id="view.RemoveItem",row=1)
    buttoncheckout = ui.Button(emoji="<:checkout:1175007951669436446> ",label="Checkout",custom_id="view.ButtonCheckout",row=1)
    buttonleft = ui.Button(emoji="<:arrowleft:1173619127106142239> ",custom_id="view.ArrowLeft",disabled=left_disabled,row=1)
    buttonright = ui.Button(emoji="<:arrowright:1173619195624308776> ",custom_id="view.ArrowRight",disabled=right_disabled,row=1)
    items = list(CONTENT[self.section])[6*(page-1):6*page]
    user_item_ids = [role.id for role in parent.user.roles]
    user_item_ids.extend(item[0] for item in db.items.getall(parent.user.id) if getItemByID(item.id).ownstack == 1)
    nonstackable = [id for id in self.selection if getItemByID(id,CONTENT[self.section]).ownstack == 1]
    options = [discord.SelectOption(label=item.name,value=item.id) for item in items if item.price*self.sale_percent <= balance-price and item.id not in nonstackable and item.id not in user_item_ids]
    menuselect = ui.Select(custom_id="view.MenuSelect", placeholder="Select from Page", min_values=1, max_values=1, options=options,row=0)
    
    buttoncheckout.callback = self.checkout
    buttonrmitem.callback = self.removeitem
    buttonleft.callback = self.arrowleft
    buttonright.callback = self.arrowright
    self.add_item(buttonleft)
    if options: 
      menuselect.callback = self.itemselect
      self.add_item(menuselect)
    self.add_item(buttonright)
    if self.selection:
      self.add_item(buttonrmitem)
      self.add_item(buttoncheckout)

  async def arrowleft(self, interaction: discord.Interaction):
    await interaction.response.defer()
    await loadpage(self.parent, self.page - 1,self.balance,self.sale_percent,self.section,self.selection,self.price)

  async def arrowright(self, interaction: discord.Interaction):
    await interaction.response.defer()
    await loadpage(self.parent, self.page + 1,self.balance,self.sale_percent,self.section,self.selection,self.price)

  async def removeitem(self, interaction: discord.Interaction):
    await interaction.response.defer()
    item_id = self.selection[-1]
    for item in CONTENT[self.section]:
      if item.id == item_id:
        price = int(item.price * self.sale_percent)
    self.selection.remove(item_id)
    await loadpage(self.parent, self.page,self.balance,self.sale_percent,self.section,self.selection,self.price-price)
   
  async def checkout(self, interaction: discord.Interaction):
    await interaction.response.defer()
    checkout_embed = discord.Embed(title="Are you sure?",description=f"**This action is irreversible.**")
    selection_counts = defaultdict(int)
    for item_id in self.selection:
        name = getItemByID(item_id,CONTENT[self.section]).name
        selection_counts[name] += 1
    selection_lines = [f'{count}x {name}' for name, count in selection_counts.items()]
    selectionvalue = '\n'.join(selection_lines)
    checkout_embed.add_field(name="<:selection:1172609449593143316> Selected Items", value=selectionvalue)
    checkout_embed.add_field(name="<:circular:1172609451023405098> Transaction", value=f"__Current Balance__ : `` {self.balance} Coins ``\n__Total Price__ : `` {self.price} Coins ``\n*You'll be left with `` {self.balance-self.price} Coins ``*")
    await self.parent.edit_original_response(embed=checkout_embed,view=CheckoutButtons(self.parent,self.page,self.balance,self.sale_percent,self.section,self.selection,self.price))

  async def itemselect(self,interaction: discord.Interaction):
    await interaction.response.defer()
    item_id = int(interaction.data["values"][0])
    self.selection.append(item_id)
    price = getItemByID(item_id,CONTENT[self.section]).price * self.sale_percent
    await loadpage(self.parent, self.page, self.balance,self.sale_percent,self.section,self.selection,self.price+price)

class CheckoutButtons(ui.View):
  def __init__(self,parent,page,balance,sale_percent,section,selection,price):
    super().__init__(timeout=None)
    self.parent = parent
    self.balance = balance
    self.selection = selection
    self.price = price
    self.page = page
    self.section = section
    self.sale_percent = sale_percent

  @ui.button(label="Confirm",custom_id="View.ConfirmCheckout",emoji="<:confirm:1175396326272409670>")
  async def confirmcheckout(self,interaction: discord.Interaction,button: ui.Button):
    await interaction.response.defer()
    embed= discord.Embed(description=f"**<:partyhorn:1175408062782263397> {self.section.capitalize()} added successfully!**")
    db.exchange(interaction.client.user.id,interaction.user.id,self.price)
    for item_id in self.selection:
      role = interaction.guild.get_role(item_id)
      if role:
        await interaction.user.add_roles(role)
      else:
        db.items.increase(interaction.user.id,item_id,1)
    await self.parent.edit_original_response(embed=embed,view=None)

  @ui.button(label="Go back",custom_id="View.CancelCheckout",emoji="<:undo:1175396297583366155>")
  async def cancelcheckout(self,interaction: discord.Interaction,button: ui.Button):
    await interaction.response.defer()
    await loadpage(self.parent,self.page,self.balance,self.sale_percent,self.section,self.selection,self.price)

class SectionSelect(ui.View):
  def __init__(self,parent: discord.Interaction):
    super().__init__(timeout=None)
    self.parent = parent
    self.balance = db.fetch("economy","coins",parent.user.id)

  options = [discord.SelectOption(label=key.capitalize(),value=key,emoji=value) for key, value in EMOJIS.items()]
  @ui.select(custom_id="View.SectionSelect",placeholder="Select a option",min_values=1,max_values=1,options=options,row=0)
  async def selection(self,interaction:discord.Interaction,select: ui.Select):
    await interaction.response.defer()
    bank_balance = db.fetch('economy','coins',interaction.client.user.id)
    sale_percent = 1
    if bank_balance < interaction.guild.member_count * 100:
      sale_percent = 0.75
      if bank_balance == 0:
        sale_percent = 0.5
    await loadpage(self.parent,1,self.balance,sale_percent,interaction.data["values"][0])

class ShopButtons(ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @ui.button(label="Open Shop", custom_id="View.viewAllFeaturesButton", emoji="<:cart:1172610055749783672>")
  async def viewAllFeaturesButton(self, interaction: discord.Interaction, button: ui.Button):
    embed = discord.Embed(description="**<:searching:1172609453686800464> What would you like to buy?**")
    await interaction.response.send_message(embed=embed,ephemeral=True,delete_after=120,view=SectionSelect(interaction))

  @ui.button(label="Rewards",custom_id="View.RewardsButton",emoji="<:passion:1179088197842649180>",disabled=True)
  async def RewardsButton(self,interaction: discord.Interaction,button: ui.Button):
    await interaction.response.send_message("work in progress!",ephemeral=True,delete_after=120)

  @ui.button(label="Quests",custom_id="View.QuestsButton",emoji="<:progresschart:1178590023759695952>",disabled=True)
  async def QuestsButton(self,interaction: discord.Interaction,button: ui.Button):
    await interaction.response.send_message("work in progress!",ephemeral=True,delete_after=120)

class ShopReady(Plugin):
  def __init__(self, bot):
    self.bot = bot
    self.bot.add_view(ShopButtons())
    super().__init__(bot=bot)


  @commands.Cog.listener()
  async def on_ready(self):
    channel = self.bot.get_channel(config.SHOP_CHANNEL)
    if channel:
      embed = discord.Embed(
        title="<:level:1172820830812643389> Level Shop",
        description="**Exchange your coins for exclusive server features!**\nType </coins:1172931104890703984> to view your coin balance",
        color=0x2b2d31)
      embed.set_thumbnail(url="https://i.ibb.co/4Zr15Gv/invest.png")
      messages = []
      async for msg in channel.history(limit=50):
          if msg.author == self.bot.user:
              messages.append(msg)
      message = messages[0] if messages else None
      if message:
        await message.edit(embed=embed,view=ShopButtons())
      else:
        file = discord.File("assets/shop.png", filename="shop.png")
        await channel.send(embed = embed,file=file,view=ShopButtons())



async def setup(bot):
  await bot.add_cog(ShopReady(bot))

