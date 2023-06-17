from redbot.core.bot import Red
from .rolemembers import RoleMembers

async def setup(bot: Red) -> None:
    await bot.add_cog(RoleMembers(bot))
