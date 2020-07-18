import discord
from redbot.core import commands
from redbot.core import checks, Config

# needed to improve autocomplete
from redbot.core.bot import Red
from discord.ext.commands import Context

import aiohttp
import time
import random
import re
#import scipy.stats

# research
# https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
# https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
# https://github.com/IeuanG/mxtm/blob/master/main.py


class Snatch(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        # idea to use config custom to make life easier
        # https://github.com/tekulvw/Squid-Plugins/blob/rewrite_cogs/logger/logger.py
        self.conf = Config.get_conf(self, identifier=23313)

        # template for sources
        # TODO: Remember the last few images shown to avoid repeats?
        self.template_source = {
            "subreddit": "",    # subreddit to get the images from
            "nsfw": True,       # restrict use to nsfw channels
            # time in seconds to refresh data list (default 1 day)
            "frequency": 86400,
            "keep": 200,        # number of records to keep in data
            "last": 0,          # unixtime of last time data was refreshed
            "data": []          # list of image links retrived with some metadata
        }

        self.template_data = {
            "url": "",
            "meta": {
                "score": 0,
                "views": 0,
                "last": 0
            }
        }

        # copies the source template to make the default source
        default_source = self.template_source.copy()
        default_source.update({
            'subreddit': "aww",
            'nsfw': False
        })

        # registers default config
        default_global = {
            "sources": {
                "aww": default_source
            }
        }
        self.conf.register_global(**default_global)

    async def snatch_help(self, ctx):
        await ctx.send("can't find option.")

    @commands.command(pass_context=True)
    async def snatch(self, ctx, source: str = ""):
        """Shown a random image from the given source."""
        await ctx.trigger_typing()

        # search for the right list
        async with self.conf.sources() as sources:
            if source not in sources.keys():
                await ctx.send(f"Unknown id '{source} given. use `[p]snatchset list` to see available.")
                return

            src = sources[source]
            data_count = len(src['data'])

            # is it okay to post here?
            if src['nsfw'] and not ctx.channel.is_nsfw():
                await ctx.send(f"Snatch {source} is marked as NSFW and this is not a NSFW channel.")
                return

            # found it but do we have data?
            if data_count < 1:
                await ctx.send(f"source '{source}' as no more images, use `[p]snatchset refresh` to get more.")
                return

        # BUG: got a duplicated image? copy post or not removing image?
        # pick a new link at random and removes it from the list
        link = src['data'].pop(random.randrange(data_count))
        await ctx.send(link)

    @commands.group(pass_context=True)
    async def snatchset(self, ctx):
        """Configures the sources for [p]snatch"""
        pass

    @snatchset.command(pass_context=True, name='list')
    async def set_list(self, ctx):
        """Lists all the configured sources."""
        await ctx.trigger_typing()
        guild = ctx.message.guild

        emb = discord.Embed(
            title="Snatch sources",
            colour=discord.Colour.dark_purple()
        )
        emb.set_author(name=guild.name, icon_url=guild.icon_url)
        sources = await self.conf.sources()
        for source, src in sources.items():
            emb.add_field(
                name=source,
                value=f"[r/{src['subreddit']}](https://reddit.com/r/{src['subreddit']}) ({len(src['data'])})\nnsfw: {src['nsfw']}",
                inline=True
            )
        await ctx.send(embed=emb)

    @checks.admin_or_permissions(manage_guild=True)
    @snatchset.command(pass_context=True, name='add')
    async def set_add(self, ctx, source: str, subreddit: str, nsfw: bool = True):
        """Adds a new source"""
        await ctx.trigger_typing()
        async with self.conf.sources() as sources:
            if source in sources.keys():
                await ctx.send("A source with that id already exists")
                return

            # add a new one
            entry = self.template_source.copy()
            entry.update({
                'subreddit': subreddit,
                'nsfw': nsfw
            })
            sources[source] = entry
        await self.go_sniffing()
        await ctx.send(f"added source '{source}' for subreddit '{subreddit}'")

    @checks.admin_or_permissions(manage_guild=True)
    @snatchset.command(pass_context=True, name='delete')
    async def set_delete(self, ctx, source: str):
        """Deletes the source with the given id."""
        await ctx.trigger_typing()
        async with self.conf.sources() as sources:
            if source in sources:
                del sources[source]
                await ctx.send(f"Removed source with id: '{source}'.")
            else:
                await ctx.send(f"Source with id '{source}' doesn't exist.")

    @snatchset.command(pass_context=True, name='purge')
    async def set_purge(self, ctx, source: str):
        """Removes all images for given source"""
        await ctx.trigger_typing()
        async with self.conf.sources() as sources:
            if sources[source]:
                sources[source]['data'] = []
                sources[source]['last'] = 0

        await ctx.send(f"Data for source '{source}' has been purged.")

    @snatchset.command(pass_context=True, name='refresh')
    async def set_refresh(self, ctx, source: str = None):
        """Triggers refresh of data for sources"""
        async with ctx.typing():
            if source is None:
                await self.go_sniffing()
            else:
                await self.sniff_source(source)
        await ctx.send("Refreshed sources.")


    @snatchset.command(pass_context=True, name='forcerefresh')
    async def set_forcerefresh(self, ctx, source: str = None):
        """Forces  refresh data for sources before scheduled"""
        async with ctx.typing():
            if source is None:
                await self.go_sniffing(True)
            else:
                await self.sniff_source(source, True)
        await ctx.send("Refreshed sources.")

    async def go_sniffing(self, force: bool = False):
        # BUG: keep getting errors saying i'm not awaiting for conf?
        sources = await self.conf.sources()
        for source, src in sources.items():
            await self.sniff_source(source, force)

    async def sniff_source(self, source: str, force: bool = False):
        async with self.conf.sources() as sources:
            src = sources[source]

            if time.time() < (src['last'] + src['frequency']) and force == False:
                print(f"Not time to update '{source}', skipping...")
                return

            # fetch new images from subreddit
            print(f"starting to update '{source}'")
            links = await self.parse_subreddit(src['subreddit'], src['nsfw'])
            # add images to data trough set to prune repeats
            src['data'] = list(set(links + src['data']))
            print(
                f"finished updating '{source}', total data is now: {len(src['data'])}")
            # we're just updated so
            src['last'] = time.time()

    # TODO: instead of going trough x pages maybe make it get x number of entries?
    # TODO: make week, month options for quality
    async def parse_subreddit(self, sub: str, nsfw: bool, pages: int = 10) -> list:
        base_address = f"https://reddit.com/r/{sub}/.json"
        address = f"{base_address}?sort=top&t=week"
        request_count = 0
        
        async with aiohttp.ClientSession() as session:
            links = []
            while request_count < pages:
                async with session.get(address) as response:
                    reply = await response.json()
                    # TODO: review this regex to make it more dynamic and validate if i'm using all possible media
                    # regex to filter only embedable media
                    r = re.compile(
                        r'(.*(?:(?:i\.redd\.it)|(?:imgur)|(?:gfycat)).*|.*(?:(?:jpg)|(?:png)|(?:gif)|(?:mp4)|(?:webm)))')
                    for e in reply['data']['children']:
                        url = e['data']['url']
                        is_nsfw = bool(e['data']['over_18'])

                        # only appends media if embedable and respects the nsfw of the sub
                        if r.match(url) and (nsfw or not is_nsfw):
                            links.append(url)

                        last = reply['data']['children'][-1]['data']['name']
                        address = f"{base_address}?count=25&after={last}&sort=top&t=week"
                    request_count += 1
            return list(set(links))

    async def weigh_value(self, meta: dict) -> int:
        """
        Formula

        return (meta.score / scipy.stats.trim_mean(all.qualities) - (meta.views / all.views))
        """
        pass
