import discord
from discord.ext import commands
import xdice

# needed to improve autocomplete
from redbot.core.bot import Red
from discord.ext.commands import Context

class DRoll:
    """Evaluates a dice expression"""

    def __init__(self, bot: Red):
        self.bot = bot


    @commands.command(pass_context=True, aliases=["r"])
    async def droll(self, ctx: Context, exp: str):
        """Rolls a set of dices and/or evaluates a mathematical expression."""

        try:
            ps = xdice.roll(exp)
            await ctx.send("{} `{}` = ({}) = **{}**".format(ctx.author.mention, exp, ps.format(True), ps))
        except:
            await ctx.send("Error evaluating the given expression.")
