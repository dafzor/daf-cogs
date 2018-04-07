import discord
from discord.ext import commands

class Currency:
    """Currency converter"""

    def __init__(self, bot):
        self.bot = bot
        # european bank exchange rate for dkk
        # further documentation in: http://www.ecb.int/stats/exchange/eurofxref/html/index.en.html#dev
        self.exchange: float = 7.4530

    @commands.command(aliases=["c"], pass_context=True)
    async def currency(self, ctx, text: str):
        pass

    @commands.command(pass_context=True)
    async def dkk(self, ctx, amount: float):
        """Converts EUR to DKK"""  
        await ctx.send("**{0:.2f}** EUR is **{1:.2f}** DKK".format(round(amount, 2), round(amount * self.exchange, 2)))

    @commands.command(pass_context=True)
    async def eur(self, ctx, amount: float):
        """Converts DKK to EUR"""  
        await ctx.send("**{0:.2f}** DKK is **{1:.2f}** EUR".format(round(amount, 2), round(amount  / self.exchange, 2)))
