from redbot.core.bot import Red
from .snatch import Snatch

async def setup(bot: Red) -> None:
  s = Snatch(bot)
  await bot.add_cog(s)
  await bot.loop.create_task(s.go_sniffing())
