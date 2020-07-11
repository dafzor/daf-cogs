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
    self.conf = Config.get_conf(self, identifier=208092)

    # template for sources
    self.template_source = {
      "id": "",           # name to be used to identify the source
      "sub": "",          # subreddit to get the images from
      "nsfw": False,      # restrict use to nsfw channels
      "frequency": 86400, # time in seconds to refresh data list (default 1 days)
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
            await ctx.send("Can't use NSFW source in non NSFW channel")
            return

          # pick a new link at random
          link = source['data'].pop(random.randrange(len(source['data'])))
          await ctx.send(link)
          # embed only works for images
          #emb = discord.Embed(title=link)
          #emb.set_image(url=link)
          #await ctx.send(embed=emb)
          return
    
    # if we got to the end we have no data
    await ctx.send("couldn't find any")

  @commands.group(pass_context=True)
  async def snatchcfg(self, ctx):
    pass

  @snatchcfg.command(pass_context=True, name='list')
  async def snatchcfg_list(self, ctx):
    """Lists all the configured sources"""
    guild = ctx.message.guild

    emb = discord.Embed(title="Snatch sources",
      colour=discord.Colour.dark_purple(), timestamp=ctx.message.created_at)
    emb.set_author(name=guild.name, icon_url=guild.icon_url)
    async with self.conf.sources() as sources:
      for s in sources:
        emb.add_field(name=s['id'], value=f"r/{s['subreddit']}")
    await ctx.send(embed=emb)

  @checks.admin_or_permissions(manage_guild=True)
  @snatchcfg.command(pass_context=True, name='add')
  async def snatchcfg_add(self, ctx):
    """Adds a new source"""
    await ctx.send("nyi")

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
    address = f"{base_address}?sort=top&t=week"

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
            address = f"{base_address}?count=25&after={last}&sort=top&t=week"
          
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
