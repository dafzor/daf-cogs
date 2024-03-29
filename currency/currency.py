import discord
from redbot.core import commands
from redbot.core import checks, Config

# needed to improve autocomplete
from redbot.core.bot import Red
from discord.ext.commands import Context

import re

# Future ideas
# european bank api returning xml with how much 1€ is in each currency, can use to update dkk
# further documentation in: http://www.ecb.int/stats/exchange/eurofxref/html/index.en.html#dev

class Currency(commands.Cog):
    """Currency converter"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.cfg = Config.get_conf(self, identifier=23313)

        # exchange rate uses EUR as base, so how much you need to get 1 euro
        # examples:
        #   USD: 1.08 USD to have 1 EUR
        #   GBP: 0.44 GBP to have 1 EUR
        global_settings = {
            "exchange": {
                'eur': {
                    "name": "Euro",
                    "rate": 1,
                    "symbols": ["€", "EUR"]
                },
                'usd': {
                    "name": "US dollar",
                    "rate": 1.10,
                    "symbols": ["$", "USD", "bucks"]
                },
                'dkk': {
                    "name": "Danish Krone",
                    "rate": 7.44,
                    "symbols": ["kr", ",-", "DKK"]
                },
                'gbp': {
                    "name": "British Pound",
                    "rate": 0.86,
                    "symbols": ["£", "GBP"]
                },
                'won': {
                    "name": "Korean Won",
                    "rate": 1400.62,
                    "symbols": ["₩", "WON"]
                }
            },
            "base": "eur",
            "targets": ["eur", "dkk"]
        }
        
        guild_settings = {
            "auto": True
        }

        self.cfg.register_global(**global_settings)
        self.cfg.register_guild(**guild_settings)

    @commands.group(pass_context=True)
    async def currencyset(self, ctx):
        """Allows to configure the settings for currency"""
        pass

    @currencyset.command(pass_context=True, name='auto')
    async def currencyset_auto(self, ctx, on: bool = None):
        """Toggle the automatic currency conversion of messages on and off"""
        cur_on = await self.cfg.guild(ctx.guild).auto()
        if on == None:
            await ctx.send(f"Auto is currently: {cur_on}")
        else:
            await self.cfg.guild(ctx.guild).auto.set(on)
            await ctx.send(f"Set auto currency convert messages to: {on}")



    @commands.command(pass_context=True, aliases=['c'])
    async def currency(self, ctx: Context, *, msg: str):
        await self.parse_message(ctx, msg)


    async def parse_message(self, ctx: Context, msg: str):
        """ Parses a line for known currency values. """
        if not await self.cfg.guild(ctx.guild).auto():
            return
        
        # TODO: Possible optimization using pypi regex and reset, see link bellow
        # https://stackoverflow.com/questions/44460642/python-regex-duplicate-names-in-named-groups
        # base regex to find get the value with the currency symbols filled in
        base_regex = r'(^|\s)(?P<valuef>[+-]?(?:\d*(?:\.|,))?\d+)\s?(?:(?:{0}))(\s|$)|(^|\s)(?:(?:{0}))\s?(?P<valueb>[+-]?(?:\d*(?:\.|,))?\d+)(\s|$)'

        # we go trough all the currencies we know and try to find them on the message one by one
        reply: str = ""

        exchange = await self.cfg.exchange()
        for currency, data in exchange.items():
            # appends the currency affix to the base regex
            affix = '|'.join([str.format("(?:{})", re.escape(s)) for s in data['symbols']])

            currency_regex = str.format(base_regex, affix)
            #debug:print('\nregex({})={}'.format(currency['id'], currency_regex))

            # compiles regex and interates trough results
            rx = re.compile(currency_regex, re.IGNORECASE)
            for r in rx.finditer(msg): # cant use msg because it only sends first word
                try:
                    #debug:print('\n\n\nmatch={}\nvalues={}'.format(r.group(0), r.expand(r"\g<valuef>\g<valueb>")))
                    # there should ever only be one match so putting both groups shouldn't matter
                    # we also make sure to replace , with . so conversion doesn't fail
                    value = float(r.expand(r"\g<valuef>\g<valueb>").replace(',', '.'))
                    #debug:print('value={}'.format(value))

                    # we have a matched currency value so we convert and add it to the reply
                    reply += await self.convert_to_targets(currency, value)
                except ValueError:
                    reply += "Error parsing the value \'{}\'.\n".format(
                        r.group("value"))
                    continue

        # don't bother sending empty message (no currency found)
        if reply == "":
            return

        # outputs the converted values minus the last character
        await ctx.send(reply)



    async def convert_to_targets(self, base: str, value: float) -> str:
        # <original value> <original currency id> =
        line: str = "{:.2f} {} = ".format(value, base.capitalize())

        exchange = await self.cfg.exchange()

        # converts the value into the target currencies
        for target in await self.cfg.targets():
            if target == base:
                continue  # don't convert into itself

            # get the currency data
            if target not in exchange:
                continue  # returned empty

            # converts to euros, then to target
            converted = round(value / exchange[base]['rate'] * exchange[target]['rate'], 2)

            # <converted value> <target currency id>,
            line += "**{:.2f}** *{}*, ".format(converted, target.capitalize())

        if line != "":
            line = line[:-2] + "\n"  # removes last space and coma and ends the line

        return line
        
    @commands.Cog.listener()
    async def on_message(self, message):
        # messages to ignore
        if message.author == self.bot.user or await self.is_command(message):
            return
        
        await self.parse_message(message.channel, message.content)
    
    async def is_command(self, message) -> bool:
        if callable(self.bot.command_prefix):
            prefixes = await self.bot.command_prefix(self.bot, message)
        else:
            prefixes = self.bot.command_prefix
        for p in prefixes:
            if message.content.startswith(p):
                return True
        return False
