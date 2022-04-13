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
from sys import platform
from rich.console import Console
from argparse import ArgumentParser
from collections import defaultdict
from aiohttp import client_exceptions
from utils import (
    utc_to_loacl,
    get_live_date,
    get_archive_date,
    floor_minutes,
    parse_list,
    check_url_exist,
    check_channel_in_list,
    remove_annoying_unicode,
)

SLEEP_TIME = 0.5
RERUN_TIME = 1
LIMIT_ARCHIVE_VIDEOS = 10

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

async def get_live_stream(liver_list: list, start_date, end_date):
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
                    # start_scheduled = utc_to_loacl(stream['start_scheduled'])
                    start_scheduled = utc_to_loacl(stream['available_at'])
                    title = stream['title']
                    url = f"https://youtu.be/{stream['id']}"

                    if check_url_exist(liver, url, result):
                        continue

                    if not result[start_scheduled]:
                        result[start_scheduled] = []
                    video_info = {
                        'name': name,
                        'title': title,
                        'url': url,
                        'status': 'Live/Upcoming'
                    }
                    result[start_scheduled].append(video_info)
                await asyncio.sleep(SLEEP_TIME)

                # NOTE: Archive Videos (アーカイブ)
                videos = await client.videos_from_channel(
                    channel_id, "videos", limit=LIMIT_ARCHIVE_VIDEOS
                )
                for idx in range(len(videos.contents)):
                    start_scheduled = utc_to_loacl(videos.contents[idx].available_at)

                    if start_date < start_scheduled.replace(tzinfo=None) < end_date:
                        title = videos.contents[idx].title
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, result):
                            continue

                        if not result[start_scheduled]:
                            result[start_scheduled] = []
                        video_info = {
                            'name': name,
                            'title': title,
                            'url': url,
                            'status': 'Archive'
                        }
                        result[start_scheduled].append(video_info)
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

async def get_collabs_stream(liver_list: list, start_date, end_date):
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
                for idx in range(len(videos.contents)):
                    start_scheduled = utc_to_loacl(videos.contents[idx].available_at)

                    if start_date < start_scheduled.replace(tzinfo=None) < end_date:
                        title = videos.contents[idx].title
                        collabs_channel = videos.contents[idx].channel.name
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, result):
                            continue

                        if not result[start_scheduled]:
                            result[start_scheduled] = []
                        video_info = {
                            'name': name,
                            'collabs_channel': collabs_channel,
                            'title': title,
                            'url': url,
                            'status': 'Collabs'
                        }
                        result[start_scheduled].append(video_info)
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

def print_schedule(result_dict):
    prev_date = ""
    prev_time = ""
    count = {}
    total_count = 0
    with open('test.output', 'w', encoding='utf8') as f:
        for start_scheduled in sorted(result_dict):
            # NOTE: date
            if prev_date != start_scheduled.strftime('%Y/%m/%d'):
                console.print(f"{start_scheduled.strftime('--- %Y/%m/%d ---')}")
                f.write(f"{start_scheduled.strftime('--- %Y/%m/%d ---')}\n")
                prev_date = start_scheduled.strftime('%Y/%m/%d')
                count[prev_date] = 0

            for video in result_dict[start_scheduled]:
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
                    f.write(f"{video['name']}")
                # NOTE: video title
                title_format = remove_annoying_unicode(video['title'])
                print(f"{title_format}")
                f.write(f"{title_format}\n")
                # NOTE: video url
                print(f"{video['url']}\n")
                f.write(f"{video['url']}\n\n")

                count[prev_date] += 1
                total_count += 1
    for date in count:
        console.print(f"{date} 共計 {count[date]} 枠。")
        f.write(f"{date} 共計 {count[date]} 枠。")
    console.print(f"           共計 {total_count} 枠。")
    f.write(f"           共計 {total_count} 枠。")

def test_floor_minutes_string():
    print(floor_minutes('2023-04-02T03:05:00.000Z'))
    print(floor_minutes('2023-04-02T12:00:00.000Z'))
    print(floor_minutes('2023-04-02T09:31:00.000Z'))
    print(floor_minutes('2023-04-02T04:27:00.000Z'))
    print(floor_minutes('2023-04-02T23:59:00.000Z'))
    sys.exit()

if __name__ == "__main__":
    specify_date = args_parser()

    # NOTE: get liver videso
    specify_date, start_date, end_date = get_live_date(specify_date)    
    liver_lists = [
        # 'list/liver.NIJISANJI_JP_2018.list',
        # 'list/liver.NIJISANJI_JP_SEEDs.list',
        # 'list/liver.NIJISANJI_JP_2019.list',
        # 'list/liver.NIJISANJI_JP_2020.list',
        # 'list/liver.NIJISANJI_KR.list',
        # 'list/liver.NIJISANJI_ID.list',
        # 'list/liver.NIJISANJI_EN.list',
        'list/liver.VSPO.list',
        'list/liver.FPS.list',
    ]
    # NOTE: get archive videos
    # specify_date, start_date, end_date = get_archive_date(specify_date, input_days=14)
    # liver_lists = [
    #     # 'list/liver.RIOT_Music.list',
    #     'list/liver.Kamitsubaki.list',
    # ]

    for _ in liver_lists:
        liver_list = parse_list(_)
        error_list = asyncio.run(get_live_stream(liver_list, start_date, end_date))
        i = 0
        while (len(error_list) > 0) and (i <= RERUN_TIME):
            i += 1
            print(f'rerun list: {error_list}')
            error_list = asyncio.run(get_live_stream(error_list, start_date, end_date))
    for _ in liver_lists:
        liver_list = parse_list(_)
        error_list = asyncio.run(get_collabs_stream(liver_list, start_date, end_date))
        i = 0
        while (len(error_list) > 0) and (i <= RERUN_TIME):
            print(f'rerun list: {error_list}')
            error_list = asyncio.run(get_collabs_stream(error_list, start_date, end_date))
            break
    print_schedule(result)
