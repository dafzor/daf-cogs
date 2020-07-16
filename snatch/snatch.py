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
    # TODO: Remember the last few images shown to avoid repeats?
    self.template_source = {
      "subreddit": "",    # subreddit to get the images from
      "nsfw": True,       # restrict use to nsfw channels
      "frequency": 86400, # time in seconds to refresh data list (default 1 day)
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
      'subreddit': "aww"
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
  async def snatch(self, ctx, opt: str = ""):
    """Returns result from one of the lists."""

    # search for the right list
    async with self.conf.sources() as sources:
      source = sources[opt]

      if not source:
        await ctx.send(f"Unknown id '{opt} given. use [p]snatchcfg list to see available.")
        return

      # is it okay to post here?
      if source['nsfw'] and not ctx.channel.is_nsfw():
        await ctx.send(f"Snatch {id} is marked as NSFW and this is not a NSFW channel.")
        return
        
      # found it but do we have data?
      if len(source['data']) < 1:
        await ctx.send(f"Snatch {id} as no more images, sorry =(")
        return

    # pick a new link at random and removes it from the list
    link = source['data'].pop(random.randrange(len(source['data'])))
    await ctx.send(link)
    # embed only works for images
    #emb = discord.Embed(title=link)
    #emb.set_image(url=link)
    #await ctx.send(embed=emb)
    



  @commands.group(pass_context=True)
  async def snatchcfg(self, ctx):
    pass



  @snatchcfg.command(pass_context=True, name='list')
  async def cfg_list(self, ctx):
    """Lists all the configured sources"""
    guild = ctx.message.guild

    emb = discord.Embed(title="Snatch sources",
      colour=discord.Colour.dark_purple(), timestamp=ctx.message.created_at)
    emb.set_author(name=guild.name, icon_url=guild.icon_url)
    async with self.conf.sources() as sources:
      for id, s in sources:
        emb.add_field(name=id, value=f"r/{s['subreddit']} ({len(s['data'])}), nsfw: {s['nsfw']}")
    await ctx.send(embed=emb)



  @checks.admin_or_permissions(manage_guild=True)
  @snatchcfg.command(pass_context=True, name='add')
  async def cfg_add(self, ctx, id:str, subreddit: str, nsfw: bool = True):
    async with self.conf.sources() as sources:
      if id in sources.keys():
        await ctx.send("A Snatch with that id already exists")
        return

      # add a new one
      entry = self.template_source.copy()
      entry.update({
        'subreddit': "aww",
        'nsfw': nsfw
      })
      sources[id] = entry
      self.go_sniffing()

    await ctx.send(f"added subreddit '{subreddit}' as '{id}'")


  @checks.admin_or_permissions(manage_guild=True)
  @snatchcfg.command(pass_context=True, name='delete')
  async def cfg_delete(self, ctx, id: str):
    async with self.conf.sources() as sources:
      if sources[id]:
        del sources[id]
        ctx.send(f"Removed snatch {id}.")
      else:
        ctx.send(f"Snatch with {id} doesn't exist.")



  @snatchcfg.command(pass_context=True, name='purge')
  async def cfg_purge(self, ctx, id: str):
    async with self.conf.sources() as sources:
      if sources[id]:
        sources[id]['data'] = []
    
    await ctx.send(f"Snatch data for {id} has been purged.")



  @snatchcfg.command(pass_context=True, name='refresh')
  async def cfg_refresh(self, ctx):
    self.go_sniffing()



  async def go_sniffing(self):
    async with self.conf.sources() as sources:
      for id, source in sources.items():
        if time.time() < (source['last'] + source['frequency']):
          continue # not time to update yet

        print(f"trying to update {id}")
        # fetch new images from subreddit
        links = await self.parse_subreddit(source['subreddit'])
        # add images to data trough set to prune repeats
        source['data'] = list(set(links + source['data']))

        print(f"updated {id}, total data is now {len(source['data'])}")

        # we're just updated so
        source['last'] = time.time()
        # except Exception as e:
        #     print("failed to update {}\n{}".format(source['id'], e))

  # TODO: instead of going trough x pages maybe make it get x number of entries?
  async def parse_subreddit(self, sub: str, pages: int = 10) -> list:
    base_address = f"https://reddit.com/r/{sub}/.json"
    address = f"{base_address}?sort=top&t=week"

    request_count = 0
    async with aiohttp.ClientSession() as session:
      links = []

      while request_count < pages: 
        async with session.get(address) as response:
          reply = await response.json()

          # regex to filter only embedable media
          # TODO: review this regex to make it more dynamic and validate if i'm using all possible media
          r = re.compile(r'(.*(?:(?:i\.redd\.it)|(?:imgur)|(?:gfycat)).*|.*(?:(?:jpg)|(?:png)|(?:gif)|(?:mp4)|(?:webm)))')
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
