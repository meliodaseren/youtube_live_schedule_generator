#!/usr/bin/env python

import asyncio
from holodex.client import HolodexClient

async def main():
    async with HolodexClient() as client:
        search = await client.autocomplete("雨森小夜")
        channel_id = search.contents[0].value
        print(channel_id)

        channel = await client.channel(channel_id)
        print(channel.name)
        print(channel.subscriber_count)

        videos = await client.videos_from_channel(channel_id, "videos")
        print(videos.contents[0].title)

asyncio.run(main())

