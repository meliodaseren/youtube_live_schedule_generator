#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
"""

import asyncio
from holodex.client import HolodexClient
from rich.console import Console
from time import sleep
from sys import platform
from collections import defaultdict
from datetime import (
    datetime,
    timedelta,
    date
)
from utils import (
    utc_to_loacl,
    check_url_exist,
    parse_list
)

console = Console()
result = defaultdict(dict)

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin": # macOS
    pass
elif platform == "win32": # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def get_date(input_days=7):
    specify_date = ""
    # specify_date = datetime(2021, 11, 3, 0, 0)
    if specify_date:
        today_date = specify_date
        first_date = today_date - datetime.timedelta(days=input_days)
    else:
        today_date = datetime.combine(date.today(), datetime.min.time())
        first_date = today_date - timedelta(days=input_days)
    return first_date, today_date + timedelta(days=1)

async def main(liver_list, start_date, end_date):
    async with HolodexClient() as client:
        for liver in liver_list:
            search = await client.autocomplete(liver)

            channel_id = search.contents[0].value
            channel = await client.channel(channel_id)
            name = channel.name
            # print(f'{channel.subscriber_count}')

            # NOTE: Clips Videos (切り抜き)
            # HACK: Limit archive videos: 5
            videos = await client.videos_from_channel(channel_id, "clips", limit=30)
            for idx in range(len(videos.contents)):
                start_scheduled = utc_to_loacl(videos.contents[idx].available_at)
                # print(f'       {liver} {idx} {astart_scheduled} vs {first_date}')
                if start_date < start_scheduled.replace(tzinfo=None) < end_date:
                    # print(f'[PASS] {astart_scheduled} > {first_date}')
                    title = videos.contents[idx].title
                    clips_channel = videos.contents[idx].channel.name
                    url = f"https://youtu.be/{videos.contents[idx].id}"

                    if check_url_exist(liver, url, result):
                        continue

                    # Create dictionary
                    if not result[start_scheduled]:
                        result[start_scheduled] = []
                    video_info = {
                        'name': name,
                        'clips_channel': clips_channel,
                        'title': title,
                        'url': url,
                        'status': 'Clips'
                    }
                    result[start_scheduled].append(video_info)
            sleep(1)

def print_videos():
    prev_date = ""
    prev_time = ""
    for start_scheduled in sorted(result):
        # NOTE: print date
        if prev_date != start_scheduled.strftime('%Y/%m/%d'):
            print(start_scheduled.strftime('--- %Y/%m/%d ---'))
            prev_date = start_scheduled.strftime('%Y/%m/%d')
        for video in result[start_scheduled]:
            # if prev_time != start_scheduled.strftime('%H:%M (%Y/%m/%d)'):
                # print(start_scheduled.strftime('%H:%M'))
                # prev_time = start_scheduled.strftime('%H:%M (%Y/%m/%d)')
            # if video['status'] == 'Clips':
                # if check_channel_in_list(video['clips_channel'], liver_list):
                    # print(f"{video['clips_channel']}")
                # else:
                    # print(f"{video['clips_channel']} ({video['name']} 剪輯)")
            # else:
                # print(f"{video['name']}")
            # NOTE: print video title
            print(f"{video['title']}")
            # NOTE: print video url
            print(f"{video['url']}\n")

if __name__ == "__main__":
    start_date, end_date = get_date(input_days=3)
    print(f"Clips start from {start_date} to {end_date}\n")
    liver_lists = parse_list('list/liver.VSPO.list')
    asyncio.run(main(liver_lists, start_date, end_date))
    print_videos()
