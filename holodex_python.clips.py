#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
"""
import asyncio
from sys import platform
from collections import defaultdict
from aiohttp import client_exceptions
from holodex.client import HolodexClient
from rich.console import Console
from utils import (
    time_formatter,
    check_url_exist,
    parse_list,
    get_archive_date,
)
from holodex_python import (
    args_parser,
)

SLEEP_TIME = 0.5
RERUN_TIME = 1
LIMIT_ARCHIVE_VIDEOS = 30

console = Console()
SCHEDULE = defaultdict(dict)

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin": # macOS
    pass
elif platform == "win32": # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main(liver_list: list, start_date, end_date):
    async with HolodexClient() as client:
        error_list = []
        for liver in liver_list:
            try:
                search = await client.autocomplete(liver)
                channel_id = search.contents[0].value
                channel = await client.channel(channel_id)
                name = channel.name
                print(f'get live: {liver}, {channel.subscriber_count} subscriber')

                # NOTE: Clips Videos (切り抜き)
                videos = await client.videos_from_channel(
                    channel_id,
                    "clips",
                    limit=LIMIT_ARCHIVE_VIDEOS
                )
                for idx, _ in enumerate(videos.contents):
                    start_scheduled = time_formatter(videos.contents[idx].available_at)
                    # print(f'       {liver} {idx} {astart_scheduled} vs {first_date}')
                    if start_date < start_scheduled.replace(tzinfo=None) < end_date:
                        # print(f'[PASS] {astart_scheduled} > {first_date}')
                        title = videos.contents[idx].title
                        clips_channel = videos.contents[idx].channel.name
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, SCHEDULE):
                            continue

                        # Create dictionary
                        if not SCHEDULE[start_scheduled]:
                            SCHEDULE[start_scheduled] = []
                        video_info = {
                            'name': name,
                            'clips_channel': clips_channel,
                            'title': title,
                            'url': url,
                            'status': 'Clips'
                        }
                        SCHEDULE[start_scheduled].append(video_info)
                await asyncio.sleep(SLEEP_TIME)
            except IndexError as e:
                console.print(f"[bold red][FAIL ][/bold red] cannot search videos: {liver} (IndexError {e})")
                error_list.append(liver)
                continue
            except KeyError as e:
                console.print(f"[bold red][FAIL ][/bold red] cannot search videos: {liver} (KeyError {e})")
                error_list.append(liver)
                continue
            except client_exceptions.ContentTypeError as e:
                console.print(f"[bold red][FAIL ][/bold red] cannot search videos: {liver} (client_exceptions.ContentTypeError {e})")
                error_list.append(liver)
                continue
        await asyncio.sleep(SLEEP_TIME)
        return error_list

def print_videos_information():
    prev_date = ""
    for start_scheduled in sorted(SCHEDULE):
        # NOTE: print date
        if prev_date != start_scheduled.strftime('%Y/%m/%d'):
            print(start_scheduled.strftime('--- %Y/%m/%d ---'))
            prev_date = start_scheduled.strftime('%Y/%m/%d')
        for video in SCHEDULE[start_scheduled]:
            # NOTE: print video title
            print(f"{video['title']}")
            # NOTE: print video url
            print(f"{video['url']}\n")

def main():
    specify_date = args_parser()
    specify_date, start_date, end_date = get_archive_date(specify_date)
    liver_lists = [
        # 'list/liver.Music.list',
        # 'list/liver.VSPO.list',
        'list/liver.FPS.list',
    ]
    for _ in liver_lists:
        liver_list = parse_list(_)
        error_list = asyncio.run(main(liver_list, start_date, end_date))
        i = 0
        while (len(error_list) > 0) and (i <= RERUN_TIME):
            print(f'rerun list: {error_list}')
            error_list = asyncio.run(main(error_list, start_date, end_date))
            break
    print_videos_information()

if __name__ == "__main__":
    main()
