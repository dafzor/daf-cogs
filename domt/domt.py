import discord
from redbot.core import commands, checks, Config
# needed to improve autocomplete
from redbot.core.bot import Red
from discord.ext.commands import Context

import random

class Domt(commands.Cog):
  def __init__(self, bot: Red):
    self.cards = [
      {
        'name': 'Rogue',
        'img': 'https://i.imgur.com/voPBc64.png',
        'desc': "A nonplayer character of the DM's choice becomes Hostile toward you. The identity of your new enemy isn't known until the NPC or someone else reveals it. Nothing less than a wish spell or Divine Intervention can end the NPC's hostility toward you."
      },
      {
        'name': 'Balance',
        'img': 'https://i.imgur.com/dlHlMSJ.png',
        'desc': "Your mind suffers a wrenching alteration, causing your Alignment to change. Lawful becomes chaotic, good becomes evil, and vice versa. If you are true neutral or unaligned, this card has no effect on you."
      },
    ]

  

  @commands.command(pass_context=True)
  async def domt(self, ctx):
    p = random.randrange(len(self.cards))
    card = self.cards[p]

    emb = discord.Embed(
      title=card['name'],
      colour=discord.Colour.dark_purple(),
      url='https://roll20.net/compendium/dnd5e/Deck%20of%20Many%20Things#content',
      description=card['desc']
    )
    emb.add_image(card['img'])
    await ctx.send(embed=emb)