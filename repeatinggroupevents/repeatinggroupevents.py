import discord
from redbot.core import commands, Config

from discord.ext.commands import Context

from datetime import datetime, timedelta

from .eventreply import EventReply
from .eventreply import EventReplyStatus

# # users commands
# .rge set <label> <yes,y|no,n|tentative,t>
# .rge status <label>

# alias
#     .yfri .nfri .tfri
#     .ysat .nsat .tsat 
#     .sat .fri

# # admin commands
# .rge datetime <label> <datetime>
# .rge interval <label> <interval (hours)>
# .rge group <label> <role>
# .rge reset <label>
# .rge channel <label> <channel>
# .rge title <label> <title>
# .rge duration <label> <duration (minutes)>


# # config
# .rge add <label> <datetime> <interval (hours)> <group> <channel> <title (opt)> <duration (opt)>
# .rge del <label>
# .rge info <label>
# .rge list



# auto steps
# - past the event time reset it or duration if set
# - (interval/2) before event whisper members of group that haven't confirmed
#     - repeat every 24h
# - 1h before event announce in channel
#     - repeat 30m and 5m

# minimal barebone implementation
class RepeatingGroupEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.conf = Config.get_conf(self, identifier=7497573) # 'rge' in decimal

        # template for sources
        self.template_event = {
            "id": "",               # name to be used to identify the event
            "title": "D&D Session", # title of the event
            "time": 0,              # datetime at which the event should happen
            "interval": 86400,      # number of seconds before the event repeats (minimal 3600)
            "duration": 18000,      # how long the event lasts, must be lower then interval
            "role": "DnD",          # role with all the members for the event  
            "channel": "dnd5e",     # channel on which to show alerts for the event
            "replies": []           # list of replies (signup) to the event
        }

        self.template_reply = {
            "user": "",
            "reply": EventReplyStatus.NONE
        }

        # copies the source template to make the default events
        default_event_friday = self.template_event.copy()
        default_event_friday.update({
            'id': "friday",
            'time': 1550871000 # friday 21:30 gmt
        })
        default_event_saturday = self.template_event.copy()
        default_event_saturday.update({
            'id': "saturday",
            'time': 1550957400 # saturday 21:30 gmt
        })
        

        # registers default config
        default_global = {
            "events": [
                default_event_friday,
                default_event_saturday
            ]
        }
        self.conf.register_global(**default_global)

    @commands.command(pass_context=True)
    async def status(self, ctx: Context, id: str):
        """Shows the status of the given event."""

        event = await self.get_event(id)

        if event is None:
            await ctx.send(f"Unknown event '{id}'")
            return

        # <display template>
        message = ""

        # title (label)
        message += f"**{event['title']}** ({event['id']})\n"
        
        # time until event
        time_left = datetime.now - datetime.fromtimestamp(event['time'])
        message += f"starting in: {time_left.day} days,  {time_left.hour} hours, {time_left.minute} minutes.\n"
    

        role = None
        for r in ctx.guild.roles:
            if event['role'] == r.name.lower():
                role = r
    
        # x of total replied
        message += f"{len(event['replies'])}/{len(role['members'])} replied:\n"

        count_yes = 0
        count_no = 0
        count_tentative = 0
        count_noreply = 0

        for m in role['members']:
            message += f"\t{m['name']} - reply\n"


        # list of people with reply
        # yes a/t | no b/t | tentative c/t
        message += f"yes = {count_yes}; no = {count_no}; tentative = {count_tentative}; no reply = {count_noreply}\n"

        await ctx.send(message)

    @commands.command(pass_context=True)
    async def setreply(self, ctx: Context, id: str, reply: EventReplyStatus):
        pass

    @commands.command(pass_context=True)
    async def reset(self, ctx: Context, id: str):
        # clear replies
        # if time < current_time
        #   add interval until time > current_time
        pass

    @commands.command(pass_context=True)
    async def time(self, ctx: Context, id: str, time: str):
        """allows changing the time of the event. format hh:mm"""
        pass

    async def get_event(self, id: str):
        id = id.lower()

        with await self.conf.events() as events:
            for event in events:
                if event['id'] == id:
                    return event
        return None