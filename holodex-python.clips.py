#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
"""

import sys, asyncio
from holodex.client import HolodexClient
from rich.console import Console
from time import sleep
from sys import platform
from argparse import ArgumentParser
from collections import defaultdict
from utils import (
    utc_to_loacl,
    check_url_exist,
    parse_list,
    get_archive_date,
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

def args_parser():
    parser = ArgumentParser()
    parser.add_argument("specify_date", nargs='?', type=str,
                        help="Specify date: 211120")
    args = parser.parse_args()
    if args.specify_date:
        if len(args.specify_date) == 6:
            return args.specify_date
        else:
            sys.exit(1)
    else:
        return args.specify_date

async def main(liver_list, start_date, end_date):
    async with HolodexClient() as client:
        for liver in liver_list:
            print(liver)
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

def print_videos_information():
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
    specify_date = args_parser()
    specify_date, start_date, end_date = get_archive_date(specify_date)
    liver_lists = [
        # 'list/liver.Music.list',
        'list/liver.VSPO.list',
        # 'list/liver.FPS.list',
    ]
    for _ in liver_lists:
        liver_list = parse_list(_)
        asyncio.run(main(liver_list, start_date, end_date))
        sleep(5)
    print_videos_information()
