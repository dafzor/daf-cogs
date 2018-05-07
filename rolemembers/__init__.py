from .rolemembers import RoleMembers

def setup(bot):
    bot.add_cog(RoleMembers(bot))
