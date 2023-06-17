from redbot.core.bot import Red
from .droll import DRoll

async def setup(bot: Red) -> None:
    await bot.add_cog(DRoll(bot))
