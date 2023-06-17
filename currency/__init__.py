from redbot.core.bot import Red
from .currency import Currency

async def setup(bot: Red) -> None:
    await bot.add_cog(Currency(bot))
