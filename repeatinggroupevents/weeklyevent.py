# # users commands
# .rge set <label> <yes,y|no,n|tentative,t>
# .rge status <label>

# alias
#     .yfri .nfri .tfri
#     .ysat .nsat .tsat 
#     .sat .fri

# title (label)
# duration | time until event
# x of total replied
# list of people with reply
# yes a/t | no b/t | tentative c/t

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





class WeekDay(Enum):
    MONDAY = 0
    pass





class RepeatableEvent:
    label: str
    day: WeekDay
    time: time
    group: str
    channel: str

    replies: list


class RepeatableGroupEvents(bot):

    # barebone implement
    def async setreply(id: str, reply: EventReplyStatus):
        pass

    def async status(id: str):
        pass

    def async reset(id: str):
        pass

    def async time(id: str):
        pass

    # on init reload events

    # tbi functions
    def async get_repeatableevent(label: str) -> WeeklyEvent:
        pass


    def async set_weekyevent(label: str, we: WeeklyEvent):
        pass


    def async set_datetime(label: str, date: datetime):
        we = get_weeklyevent(label)

        if we is None:
            # event doesn't exist 

        # is valid datetime?

        we.date = date
        set_weeklyevent(label, we)

    def async set_interval(label: str, interval: int):
        pass