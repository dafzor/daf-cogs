from .currency import Currency

def setup(bot):
    c = Currency(bot)
    bot.add_cog(c)
