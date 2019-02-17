from .repeatinggroupevents import RepeatingGroupEvents

def setup(bot):
    bot.add_cog(RepeatingGroupEvents(bot))
