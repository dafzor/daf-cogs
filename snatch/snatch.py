import discord
from discord.ext import commands
from redbot.core import checks, Config

import asyncio
import aiohttp
import time
import random
import re
#import scipy.stats

# research
# https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
# https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
# https://github.com/IeuanG/mxtm/blob/master/main.py

class Snatch:
    def __init__(self, bot):
        self.bot = bot
        # idea to use config custom to make life easier
        # https://github.com/tekulvw/Squid-Plugins/blob/rewrite_cogs/logger/logger.py
        self.conf = Config.get_conf(self, identifier=208092)

        # template for sources
        self.template_source = {
            "id": "",           # name to be used to identify the source
            "sub": "",          # subreddit to get the images from
            "nsfw": False,      # restrict use to nsfw channels
            "frequency": 3600,  # time in seconds to refresh data list
            "keep": 1000,       # number of records to keep in data
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
            'id': "aww",
            'sub': "aww"
        })

        # registers default config
        default_global = {
            "sources": [
                default_source
            ]
        }
        self.conf.register_global(**default_global)


    async def snatch_help(self, ctx):
        await ctx.send("can't find option.")

    @commands.command(pass_context=True)
    async def snatch(self, ctx, opt: str = ""):
        """Returns result from one of the lists."""

        # search for the right list
        async with self.conf.sources() as sources:
            for source in sources:
                if source['id'] == opt:
                    # found it but do we have data?
                    if len(source['data']) < 1:
                        break

                    # is it okay to post here?
                    if source['nsfw'] and not ctx.channel.is_nsfw():
                        return

                    # pick a new link at random
                    link = source['data'].pop(random.randrange(len(source['data'])))
                    await ctx.send(link)
                    return
        
        # if we got to the end we have no data
        await ctx.send("couldn't find any")

    @checks.admin_or_permissions(manage_server=True)
    @commands.group(pass_context=True)
    async def snatchset(self, ctx):
        pass

    @checks.admin_or_permissions(manage_server=True)
    @snatchset.command(pass_context=True)
    async def add(self, ctx):
        pass

    async def go_sniffing(self):
        async with self.conf.sources() as sources:
            for source in sources:
                if time.time() < (source['last'] + source['frequency']):
                    continue # not time to update yet

                print("trying to update {}".format(source['id']))

                #try:
                # fetch new images from subreddit
                links = await self.parse_subreddit(source['subreddit'])
                # add images to data trough set to prune repeats
                source['data'] = list(set(links + source['data']))

                print("updated {}, total data is now {}".format(source['id'], len(source['data'])))

                # we're just updated so
                source['last'] = time.time()
                # except Exception as e:
                #     print("failed to update {}\n{}".format(source['id'], e))

    async def parse_subreddit(self, name: str, pages: int = 10) -> list:
        base_address = f"https://reddit.com/r/{name}/.json"
        address = base_address

        request_count = 0
        async with aiohttp.ClientSession() as session:
            links = []

            while request_count < pages: 
            async with session.get(address) as response:
                reply = await response.json()

                # regex to filter only embedable media
                r = re.compile(r'(.*(?:(?:imgur)|(?:gfycat)).*|.*(?:(?:jpg)|(?:png)|(?:gif)|(?:mp4)|(?:webm)))')
                for e in reply['data']['children']:
                url = e['data']['url']
                
                # only appends media if embedable
                if r.match(url):
                    links.append(url)

                last = reply['data']['children'][-1]['data']['name']
                address = f"{base_address}?count=25&after={last}"
            request_count += 1

            return list(set(links))

    async def weigh_value(self, meta: dict) -> int:
        """
        Formula

        return (meta.score / scipy.stats.trim_mean(all.qualities) - (meta.views / all.views))
        """
        pass

    # config commands to add
    # .snatchset add|del|list
    # add <name> <subreddit> <nsfw> <freq> <keep>
    # del <name>
