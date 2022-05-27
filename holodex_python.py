#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
"""
import os
import sys
import asyncio
from typing import List
from sys import platform
from datetime import datetime
from collections import defaultdict
from argparse import ArgumentParser
from aiohttp import client_exceptions
from holodex.client import HolodexClient
from rich.console import Console
from utils import (
    time_formatter,
    get_live_date,
    get_archive_date,
    parse_list,
    check_url_exist,
    check_channel_in_list,
    remove_annoying_unicode,
    wrap_title,
)

SLEEP_TIME = 0.3
RERUN_TIME = 0.5
LIMIT_ARCHIVE_VIDEOS = 10
ARCHIVE_DAYS = 14

LIVER_LISTS = [
    'list/liver.VSPO.list',
    'list/liver.FPS.list',
    'list/liver.NeoPorte.list',

    # 'list/liver.RIOT_Music.list',
    # 'list/liver.Kamitsubaki.list',

    # 'list/liver.NIJISANJI_JP_2018.list',
    # 'list/liver.NIJISANJI_JP_SEEDs.list',
    # 'list/liver.NIJISANJI_JP_2019.list',
    # 'list/liver.NIJISANJI_JP_2020.list',
    # 'list/liver.NIJISANJI_KR.list',
    # 'list/liver.NIJISANJI_ID.list',
    # 'list/liver.NIJISANJI_EN.list',
]

console = Console()
SCHEDULE = defaultdict(dict)

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin": # macOS
    pass
elif platform == "win32": # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def args_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "specify_date",
        nargs='?',
        type=str,
        help="Specify date: 211120"
    )
    parser.add_argument(
        "-c", "--collabs", action="store_true",
        help="Get collabs videos"
    )
    parser.add_argument(
        "-a", "--archive", action="store_true",
        help="Get more archive videos"
    )
    args = parser.parse_args()
    if args.specify_date:
        if len(args.specify_date) != 6:
            sys.exit(1)
    return args

async def get_live_stream(liver_list: List, start_date, end_date) -> List:
    async with HolodexClient() as client:
        error_list = []
        for liver in liver_list:
            try:
                search = await client.autocomplete(liver)
                channel_id = search.contents[0].value
                channel = await client.channel(channel_id)
                name = channel.name
                print(f'get live: {liver}, {channel.subscriber_count} subscriber')

                # NOTE: Live/Upcoming Videos (ライブ配信)
                today_schedule = {
                    "channel_id": channel_id,
                    "max_upcoming_hours": 18
                }
                live = await client.get_live_streams(today_schedule)
                for stream in live:
                    # start_scheduled = time_formatter(stream['start_scheduled'])
                    start_scheduled = time_formatter(stream['available_at'])
                    title = stream['title']
                    url = f"https://youtu.be/{stream['id']}"

                    if check_url_exist(liver, url, SCHEDULE):
                        continue

                    if not SCHEDULE[start_scheduled]:
                        SCHEDULE[start_scheduled] = []
                    video_info = {
                        'name': name,
                        'title': title,
                        'url': url,
                        'status': 'Live/Upcoming'
                    }
                    SCHEDULE[start_scheduled].append(video_info)
                await asyncio.sleep(SLEEP_TIME)

                # NOTE: Archive Videos (アーカイブ)
                videos = await client.videos_from_channel(
                    channel_id, "videos", limit=LIMIT_ARCHIVE_VIDEOS
                )
                for idx, _ in enumerate(videos.contents):
                    start_scheduled = time_formatter(videos.contents[idx].available_at)

                    if start_date < start_scheduled.replace(tzinfo=None) < end_date:
                        title = videos.contents[idx].title
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, SCHEDULE):
                            continue

                        if not SCHEDULE[start_scheduled]:
                            SCHEDULE[start_scheduled] = []
                        video_info = {
                            'name': name,
                            'title': title,
                            'url': url,
                            'status': 'Archive'
                        }
                        SCHEDULE[start_scheduled].append(video_info)
                await asyncio.sleep(SLEEP_TIME)
            except IndexError as e:
                console.print(
                    f'[bold red][FAIL ][/bold red] cannot search videos: '
                    f'{liver} (IndexError {e})')
                error_list.append(liver)
                continue
            except KeyError as e:
                console.print(
                    f'[bold red][FAIL ][/bold red] cannot search videos: '
                    f'{liver} (KeyError {e})'
                )
                error_list.append(liver)
                continue
            except client_exceptions.ContentTypeError as e:
                console.print(
                    f'[bold red][FAIL ][/bold red] cannot search videos: '
                    f'{liver} (client_exceptions.ContentTypeError {e})'
                )
                error_list.append(liver)
                continue
        await asyncio.sleep(SLEEP_TIME)
        return error_list

async def get_collabs_stream(liver_list: List, start_date, end_date) -> List:
    async with HolodexClient() as client:
        error_list = []
        for liver in liver_list:
            try:
                search = await client.autocomplete(liver)
                channel_id = search.contents[0].value
                channel = await client.channel(channel_id)
                name = channel.name
                print(f'get collabs: {liver}, {channel.subscriber_count} subscriber')

                # NOTE: Collabs Videos (コラボ)
                videos = await client.videos_from_channel(
                    channel_id, "collabs", limit=LIMIT_ARCHIVE_VIDEOS
                )
                for idx, _ in enumerate(videos.contents):
                    start_scheduled = time_formatter(videos.contents[idx].available_at)

                    if start_date < start_scheduled.replace(tzinfo=None) < end_date:
                        title = videos.contents[idx].title
                        collabs_channel = videos.contents[idx].channel.name
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, SCHEDULE):
                            continue

                        if not SCHEDULE[start_scheduled]:
                            SCHEDULE[start_scheduled] = []
                        video_info = {
                            'name': name,
                            'collabs_channel': collabs_channel,
                            'title': title,
                            'url': url,
                            'status': 'Collabs'
                        }
                        SCHEDULE[start_scheduled].append(video_info)
                await asyncio.sleep(SLEEP_TIME)
            except IndexError as e:
                console.print(
                    f'[bold red][FAIL ][/bold red] cannot search videos: '
                    f'{liver} (IndexError {e})')
                error_list.append(liver)
                continue
            except KeyError as e:
                console.print(
                    f'[bold red][FAIL ][/bold red] cannot search videos: '
                    f'{liver} (KeyError {e})'
                )
                error_list.append(liver)
                continue
            except client_exceptions.ContentTypeError as e:
                console.print(
                    f'[bold red][FAIL ][/bold red] cannot search videos: '
                    f'{liver} (client_exceptions.ContentTypeError {e})'
                )
                error_list.append(liver)
                continue
        await asyncio.sleep(SLEEP_TIME)
        return error_list

def print_schedule(liver_list: List) -> None:
    prev_date, prev_time = "", ""
    total_count, evening_count, night_count = 0, 0, 0
    count = {}
    outfile = f"test/output.{datetime.today().strftime('%Y%m%d')}"
    if os.path.exists(outfile):
        console.print(f'{outfile} already exists')
    with open(outfile, 'w', encoding='utf8') as f:
        for start_scheduled in sorted(SCHEDULE):
            # NOTE: date
            if prev_date != start_scheduled.strftime('%Y/%m/%d'):
                console.print(f"{start_scheduled.strftime('--- %Y/%m/%d ---')}")
                f.write(f"{start_scheduled.strftime('--- %Y/%m/%d ---')}\n")
                prev_date = start_scheduled.strftime('%Y/%m/%d')
                count[prev_date] = 0

            for video in SCHEDULE[start_scheduled]:
                # NOTE: video time (available at)
                if prev_time != start_scheduled.strftime('%H:%M (%Y/%m/%d)'):
                    print(start_scheduled.strftime('%H:%M'))
                    f.write(f"{start_scheduled.strftime('%H:%M')}\n")
                    prev_time = start_scheduled.strftime('%H:%M (%Y/%m/%d)')
                # NOTE: channel name
                if video['status'] == 'Collabs':
                    if check_channel_in_list(video['collabs_channel'], liver_list):
                        print(f"{video['collabs_channel']}")
                        f.write(f"{video['collabs_channel']}\n")
                    else:
                        print(f"{video['collabs_channel']} (合作)")
                        f.write(f"{video['collabs_channel']} (合作)\n")
                else:
                    print(f"{video['name']}")
                    f.write(f"{video['name']}\n")
                # NOTE: video title
                title_format = remove_annoying_unicode(video['title'])
                title_format = wrap_title(title_format)
                print(f"{title_format}")
                f.write(f"{title_format}\n")
                # NOTE: video url
                print(f"{video['url']}\n")
                f.write(f"{video['url']}\n\n")

                count[prev_date] += 1
                if int(start_scheduled.strftime('%H')) < 18:
                    evening_count += 1
                else:
                    night_count += 1
                total_count += 1
        for date, _ in count.items():
            console.print(f"{date} 共計 {_} 枠。")
            f.write(f"{date} 共計 {_} 枠。\n")

        console.print(
            f"           共計 {total_count} 枠 "
            f"({evening_count} 枠 ～18:00 {night_count} 枠)"
        )
        f.write(
            f"           共計 {total_count} 枠 "
            f"({evening_count} 枠 ～18:00 {night_count} 枠)"
        )

def main():
    args_opts = args_parser()
    start_date, end_date = get_live_date(
        args_opts.specify_date
    )
    # NOTE: get archive videos
    if args_opts.archive:
        start_date, end_date = get_archive_date(
            args_opts.specify_date, input_days=ARCHIVE_DAYS
        )

    all_liver_list = []
    for _ in LIVER_LISTS:
        all_liver_list.extend(parse_list(_))

    errors = asyncio.run(get_live_stream(all_liver_list, start_date, end_date))
    i = 0
    while (len(errors) > 0) and (i <= RERUN_TIME):
        i += 1
        print(f'rerun list: {errors}')
        errors = asyncio.run(get_live_stream(errors, start_date, end_date))

    errors = asyncio.run(get_collabs_stream(all_liver_list, start_date, end_date))
    i = 0
    while (len(errors) > 0) and (i <= RERUN_TIME):
        i += 1
        print(f'rerun list: {errors}')
        errors = asyncio.run(get_collabs_stream(errors, start_date, end_date))

    print_schedule(all_liver_list)

if __name__ == "__main__":
    main()
