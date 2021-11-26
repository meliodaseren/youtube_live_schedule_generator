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
from sys import platform
from collections import defaultdict
from datetime import datetime, timezone, timedelta, date

console = Console()
result = defaultdict(dict)

specify_date = ""
# specify_date = datetime(2021, 11, 3, 0, 0)
if specify_date:
    today_date = specify_date
    last_week = today_date - datetime.timedelta(days=7)
else:
    today_date = datetime.combine(date.today(), datetime.min.time())
    first_date = today_date - timedelta(days=7)
    # first_date = today_date - timedelta(days=30)
tomorrow_date = today_date + timedelta(days=1)

with open('liver.clips.list', 'r', encoding='utf-8') as f:
    liver_list = [line.strip() for line in f.read().splitlines()]

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin": # macOS
    pass
elif platform == "win32": # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def utc_to_loacl(utc_dt):
    tw = timezone(timedelta(hours=+8))
    schedule_time = datetime.strptime(utc_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
    return schedule_time.replace(tzinfo=timezone.utc).astimezone(tw)

def check_channel_in_list(channel_name: str, liver_list: list):
    for liver in liver_list:
        if liver in channel_name:
            # console.print(f"[bold yellow][WARN][/bold yellow] \"{channel_name}\" in liver list")
            return True

def check_url_exist(name: str, url: str, video_dict: dict):
    # TODO: check the same url with live/upcoming videos
    if url in [v['url'] for t in video_dict for v in video_dict[t]]:
        console.print(f"[bold yellow][WARN][/bold yellow] skip duplicate videos: {url} ({name})")
        return True

async def main():
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
                if first_date < start_scheduled.replace(tzinfo=None) < tomorrow_date:
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

if __name__ == "__main__":
    print(f"Clips start from {first_date}\n")

    asyncio.run(main())

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
