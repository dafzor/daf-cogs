import discord
from redbot.core import commands

from discord.ext.commands import Context

class RoleMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True, aliases=["members"])
    async def rolemembers(self, ctx: Context, role_name: str):
        """Shows all the members with the given role."""

        # if role isn't found this is the default message
        message = "Unknown role '{}'".format(role_name)

        # ignore case
        role_name = role_name.lower()

        # tries to find the role in the guild role list
        for r in ctx.guild.roles:
            if role_name == r.name.lower():
                members = ""
                for m in r.members:
                    members += m.display_name + ", "

                # remove last ', '
                if len(members) > 2:
                    members = members[:-2]
                
                message = "**{}** members: **{}**.".format(role_name, members)
                break

        await ctx.send(message)
