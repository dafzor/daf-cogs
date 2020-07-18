#%% imports
from pprint import pprint as dp
import asyncio
import aiohttp
import time
import random
import re

#%% parse function

async def parse_subreddit(self, sub: str, pages: int = 10) -> list:
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
        r = re.compile(r'(.*(?:(?:i\.redd\.it)|(?:imgur)|(?:gfycat)).*|.*(?:(?:jpg)|(?:png)|(?:gif)|(?:mp4)|(?:webm)))')
        for e in reply['data']['children']:
          url = e['data']['url']
          
          # only appends media if embedable
          #print(f"{url}")
          if r.match(url):
            links.append(url)
          
          last = reply['data']['children'][-1]['data']['name']
          address = f"{base_address}?count=25&after={last}&sort=top&t=week"
        
        request_count += 1
    return list(set(links))

#%% rum test
links = await parse_subreddit('aww')
dp(len(links))
dp(links)
