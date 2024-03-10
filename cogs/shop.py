import discord
from dbmanager import *
import json
import config
from discord import ui
from collections import defaultdict
from discord.ext import commands

content = json.load(open("assets/shopindex.json"))

contentlib = {
  "features" : "<:features:1178989659976642581>",
  "commands" : "<:dev:1178993359738642512>",
  "items" : "<:dimension:1178990567812771890>"
}


def getval(id,selector,section: str):
  for key,value in content[section].items():
    if value["id"] == id:
      return value[selector]

def next_item_price(user,section:str,sale:int):
    user_roles = [role.id for role in user.roles]
    sorted_features = sorted(content[section].items(), key=lambda x: x[1]["price"])
    next_item = next((feature for feature in sorted_features if feature[1]["id"] not in user_roles), None)
    return next_item[1]["price"]*sale if next_item else 0
    
async def loadpage(interaction: discord.Interaction,page,balance,sale_percent: int,section: str,selection = None,price = None):
  embeds = []
  price = price or 0
  display = list(content[section].items())[6*(page-1):6*page]
  left = True if page == 1 else False
  selection_counts = defaultdict(int)
  if selection:
      selection_counts = defaultdict(int)
      for item in selection:
          name = getval(item, "name",section)
          selection_counts[name] += 1
      selection_lines = [f'{count}x {name}' for name, count in selection_counts.items()]
      selectionvalue = '\n'.join(selection_lines)
  else:
      selectionvalue = "*No items selected*"
  try:
    right = not bool(list(content[section])[page * 6])
  except IndexError:
    right = True
  page_embed = discord.Embed(title=f"{contentlib[section]} {section.capitalize()}",description="")
  user_roles = [role.id for role in interaction.user.roles]
  for key, feature in display:
    if feature["id"] in user_roles:
      balance_format = f"<:badge:1178949476308766771> `` Owned ``" 
    elif int(feature["price"] * sale_percent) <= balance:
      balance_format = f"<:coins:1172819933093179443> `` {int(feature['price'] * sale_percent)} Coins ``" 
    elif int(feature["price"] *sale_percent) > balance:
      balance_format = f"<:disabledcoins:1178939795288891432> *`` {int(feature['price'] * sale_percent)} Coins ``*" 
    page_embed.add_field(name=feature["name"],value=f"*{feature['description']}*\n{balance_format}",inline=True)
  page_embed.set_footer(text=f"Page {page}/{(len(content[section].items())+5)//6}")
  embeds.append(page_embed)
  transaction_embed = discord.Embed(description="")
  next = next_item_price(interaction.user,section,sale_percent)
  if next == 0:
    transaction_embed.add_field(name="<:finishline:1175568414950031471> You've reached the end!",value="**There is nothing left to buy in this section.\nAsk <@955187087911555152> to add more!** ")
  elif next <= balance:
    transaction_embed.add_field(name="<:selection:1172609449593143316> Selected", value=selectionvalue)
    transaction_embed.add_field(name="<:circular:1172609451023405098> Transaction", value=f"__Current Balance__ : `` {balance} Coins ``\n__Total Price__ : `` {price} Coins ``\n*You'll be left with `` {balance-price} Coins ``*")
    if sale_percent < 1:
      if sale_percent == 0.5:
        sale_embed = discord.Embed(title='<:flashsale:1200119986568581160> BANK 50% SALE',description='**THE BANK IS INSOLVENT. GO BUY NOW, THE BANK IS RUPT. ALL ITEMS 50% SALE!!**')
      else:
        sale_embed = discord.Embed(title='<:flashsale:1200119986568581160> BANK 75% SALE',description='**As the Bank is Undercapitalized, Every item is on 75% Sale!\nGo buy now before the Sale goes away!**')
      sale_embed.set_thumbnail(url='https://i.ibb.co/0KxjgjC/box.png')
      embeds.append(sale_embed)
  else:
    transaction_embed.description = "**Save some more coins up for the next item by chatting a bit!**\nCheck your balance with </coins:1172931104890703984>,\nafter gathering enough come back!"
    transaction_embed.title = "<:fireup:1175569234982604870> Aw, not quite yet!" 
  embeds.append(transaction_embed)
  try:
    await interaction.edit_original_response(embeds=embeds,view=MainMenu(interaction,page,left,right,balance,selection,section,price,sale_percent))
  except Exception as e:
    await interaction.edit_original_response(content=f"There was an error loading the page.\n{e}")
  

class MainMenu(ui.View):
  def __init__(self, parent, page, left_disabled, right_disabled,balance,selection,section,price,sale_percent):
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
    items = list(content[self.section].items())[6*(page-1):6*page]
    user_ids = [role.id for role in parent.user.roles]
    roleselect = [id for id in self.selection if len(str(id)) > 4]
    options = [discord.SelectOption(label=feature["name"],value=feature["id"]) for key,feature in items if int(feature["price"]*self.sale_percent) <= balance-price and feature["id"] not in roleselect and feature["id"] not in user_ids]
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
    role_id = self.selection[-1]
    for key,value in content[self.section].items():
      if value["id"] == role_id:
        price = int(value["price"] * self.sale_percent)
    self.selection.remove(role_id)
    await loadpage(self.parent, self.page,self.balance,self.sale_percent,self.section,self.selection,self.price-price)
   
  async def checkout(self, interaction: discord.Interaction):
    await interaction.response.defer()
    checkout_embed = discord.Embed(title="Are you sure?",description=f"**This action is irreversible.**")
    selection_counts = defaultdict(int)
    for item in self.selection:
        name = getval(item, "name",self.section)
        selection_counts[name] += 1
    selection_lines = [f'{count}x {name}' for name, count in selection_counts.items()]
    selectionvalue = '\n'.join(selection_lines)
    checkout_embed.add_field(name="<:selection:1172609449593143316> Selected Items", value=selectionvalue)
    checkout_embed.add_field(name="<:circular:1172609451023405098> Transaction", value=f"__Current Balance__ : `` {self.balance} Coins ``\n__Total Price__ : `` {self.price} Coins ``\n*You'll be left with `` {self.balance-self.price} Coins ``*")
    await self.parent.edit_original_response(embed=checkout_embed,view=CheckoutButtons(self.parent,self.page,self.balance,self.sale_percent,self.section,self.selection,self.price))

  async def itemselect(self,interaction: discord.Interaction):
    await interaction.response.defer()
    role_id = int(interaction.data["values"][0])
    package = content[self.section].items()
    for key, value in package:
      if value["id"] == role_id:
        price = int(value["price"] * self.sale_percent)
    self.selection.append(role_id)
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
    exchange(config.bot_id,interaction.user.id,self.price)
    for id in self.selection:
      role = interaction.guild.get_role(id)
      if role:
        await interaction.user.add_roles(role)
      else:
        json_data = get("items","json_data",interaction.user.id)
        if json_data != 0:
          json_data = json.loads(json_data)
          print(f"old data: {json_data}")
          if json_data.get(str(id)):
            json_data[str(id)] += 1
          else:
            json_data[str(id)] = 1
        else:
          print("null data.")
          json_data = {str(id):1}
        print("adding item.")
        print(f"new: {json_data}")
        set("items","json_data",interaction.user.id,json.dumps(json_data))

    await self.parent.edit_original_response(embed=embed,view=None)

  @ui.button(label="Go back",custom_id="View.CancelCheckout",emoji="<:undo:1175396297583366155>")
  async def cancelcheckout(self,interaction: discord.Interaction,button: ui.Button):
    await interaction.response.defer()
    await loadpage(self.parent,self.page,self.balance,self.sale_percent,self.section,self.selection,self.price)

class SectionSelect(ui.View):
  def __init__(self,parent):
    super().__init__(timeout=None)
    self.parent = parent
    self.balance = get("economy","coins",parent.user.id)

  options = [discord.SelectOption(label=key.capitalize(),value=key,emoji=value) for key, value in contentlib.items()]
  @ui.select(custom_id="View.SectionSelect",placeholder="Select a option",min_values=1,max_values=1,options=options,row=0)
  async def selection(self,interaction:discord.Interaction,select: ui.Select):
    await interaction.response.defer()
    bank_balance = get('economy','coins',config.bot_id)
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

class ShopReady(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.add_view(ShopButtons())

  @commands.Cog.listener()
  async def on_ready(self):
    channel = self.bot.get_channel(config.shop_channel)
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
