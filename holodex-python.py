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
from collections import defaultdict
from datetime import datetime, timezone, timedelta

liver_list = (
    ## vspo
    "小雀とと", "花芽すみれ", "花芽なずな", "一ノ瀬うるは",
    "橘ひなの", "胡桃のあ", "如月れん", "英リサ",
    "兎咲ミミ", "空澄セナ", "八雲べに", "神成きゅぴ",
    "藍沢エマ", "紫宮るな",
    ## 藝人旅團 (VTuber)
    "かみと", "白雪レイド", "小森めと", "バーチャルゴリラ")

result = defaultdict(dict)

def utc_to_loacl(utc_dt):
    tw = timezone(timedelta(hours=+8))
    schedule_time = datetime.strptime(utc_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
    return schedule_time.replace(tzinfo=timezone.utc).astimezone(tw)

async def main():
    async with HolodexClient() as client:
        # search = await client.autocomplete("雨森小夜")
        for liver in liver_list:
            search = await client.autocomplete(liver)

            channel_id = search.contents[0].value
            channel = await client.channel(channel_id)
            # print(f'{channel.subscriber_count}')
            # videos = await client.videos_from_channel(channel_id, "videos")
            # print(f'{videos.contents[0].title}')
            today_schedule = {
                "channel_id": channel_id,
                "max_upcoming_hours": 18
            }

            live = await client.get_live_streams(today_schedule)
            idx = 0
            
            for stream in live:
                # print(stream)
                # if 'start_actual' in stream:
                #     print(f"{stream['start_actual']}")
                # else:
                #     print(f"{stream['start_scheduled']}")
                # publish = utc_to_loacl(stream['published_at'])
                # avaiable = utc_to_loacl(stream['available_at'])
                start_scheduled = utc_to_loacl(stream['start_scheduled'])
                name = channel.name
                title = stream['title']
                url = f"https://youtu.be/{stream['id']}"

                # Create dictionary
                result[start_scheduled][idx] = {}
                result[start_scheduled][idx]['name'] = ""
                result[start_scheduled][idx]['title'] = ""
                result[start_scheduled][idx]['url'] = ""
                if result[start_scheduled][idx]['name'] != "":
                    idx += 1
                result[start_scheduled][idx]['name'] = name
                result[start_scheduled][idx]['title'] = title
                result[start_scheduled][idx]['url'] = url

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

for start_scheduled in sorted(result):
    for idx in result[start_scheduled]:
        print(start_scheduled.strftime('%H:%M (%m/%d)'))
        print(result[start_scheduled][idx]['name'])
        print(result[start_scheduled][idx]['title'])
        print(result[start_scheduled][idx]['url'])
        print('')
