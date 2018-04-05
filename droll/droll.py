import discord
from discord.ext import commands
import xdice

class DRoll:
    """Rolls a dice expression"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True, aliases=["r"])
    async def droll(self, ctx, exp: str):
        """Rolls a set of dices."""

        try:
            ps = xdice.roll(exp)
            await ctx.send("{} `{}` = ({}) = **{}**".format(ctx.author.mention, exp, ps.format(True), ps))
        except:
            await ctx.send("Couldn't parse roll.")
