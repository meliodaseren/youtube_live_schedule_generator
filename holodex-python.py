#!/usr/bin/env python

"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
Requirement:
    aiohttp==3.7.4.post0
"""

import asyncio
from holodex.client import HolodexClient

liver_list = (
    ## vspo
    "小雀とと",
    "花芽すみれ",
    "花芽なずな",
    "一ノ瀬うるは",
    "橘ひなの",
    "胡桃のあ",
    "如月れん",
    "英リサ",
    "兎咲ミミ",
    "空澄セナ",
    "八雲べに",
    "神成きゅぴ",
    "藍沢エマ",
    "紫宮るな",
    ## 藝人旅團
    "かみと",
    "白雪レイド",
    "小森めと",
    "バーチャルゴリラ")

async def main():
    async with HolodexClient() as client:
        search = await client.autocomplete("雨森小夜")
        for liver in liver_list:
            search = await client.autocomplete(liver)

            channel_id = search.contents[0].value
            channel = await client.channel(channel_id)
            # print(f'{channel.subscriber_count}')

            # videos = await client.videos_from_channel(channel_id, "videos")
            # print(f'{videos.contents[0].title}')

            today_schedule = {
                "channel_id": channel_id,
                "max_upcoming_hours": 24
            }
            live = await client.get_live_streams(today_schedule)
            for stream in live:
                print('')
                print(f"{stream['available_at']}")
#                if 'start_actual' in stream:
#                    print(f"{stream['start_actual']}")
#                else:
#                    print(f"{stream['start_scheduled']}")
                print(f"{channel.name}")
                print(f"{stream['title']}")
                print(f"https://youtu.be/{stream['id']}")

if __name__ == "__main__":
    asyncio.run(main())

