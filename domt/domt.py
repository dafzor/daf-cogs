import discord
from redbot.core import commands, checks, Config
# needed to improve autocomplete
from redbot.core.bot import Red
from discord.ext.commands import Context

import random

class Domt(commands.Cog):
  self.cards = [
    {
      'name': 'Ally'
      'img': 'https://i.imgur.com/SAnA7CD.jpg'
      'desc': "A nonplayer character of the DM's choice becomes enamored with you. The identity of the new friend isn't known until the NPC or someone else reveals it. The NPC will do everything in their power to aid you as though you were a life-long friend."
    },
    {
      'name': 'Arcane'
      'img': 'https://i.imgur.com/aumCU1T.jpg'
      'desc': "You lose all forms of wealth as per the Ruin card, however you are compensated by the gods with a magical item that appears at your feet."
    },
  ]

  

  @commands.command(pass_context=True)
  async def domt(self, ctx):
    p = random.randrange(len(self.cards))
    card = self.cards[p]

    emb = discord.Embed(
      title=card['name'],
      colour=discord.Colour.dark_purple(),
      url=card['img'],
      description=card['description']
    )
    await ctx.send(embed=emb)