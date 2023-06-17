from redbot.core.bot import Red
from .domt import Domt

async def setup(bot: Red) -> None:
  await bot.add_cog(Domt(bot))
