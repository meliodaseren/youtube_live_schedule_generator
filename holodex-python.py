#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
"""
import sys, asyncio, re
from holodex.client import HolodexClient
from time import sleep
from sys import platform
from rich.console import Console
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime, timezone, timedelta, date
from aiohttp import client_exceptions

console = Console()
result = defaultdict(dict)

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin": # macOS
    pass
elif platform == "win32": # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ANNOYING_CHARS = (
    ('\u2000', ''),
    ('\u2001', ''),
    ('\u2002', ''),
    ('\u2003', ''),
    ('\u2004', ''),
    ('\u2005', ''),
    ('\u2006', ''),
    ('\u2007', ''),
    ('\u2008', ''),
    ('\u2009', ''),
    ('\u200a', ''),
    ('\u200b', ''),
    ('\u200c', ''),
    ('\u200d', ''),
    ('\u200e', ''),
    ('\u200f', ''),
    ('\u2010', '-'),
    ('\u2011', '-'),
    ('\u2012', '-'),
    ('\u2013', '-'),
    ('\u2014', '-'),
    ('\u2014', '-'),
    ('\u2018', "'"),
    ('\u201b', "'"),
    ('\u201c', '"'),
    ('\u201c', '"'),
    ('\u201d', '"'),
    ('\u201e', '"'),
    ('\u201f', '"')
)

def remove_annoying_unicode(input_str):
    """
    https://www.utf8-chartable.de/unicode-utf8-table.pl?start=8064&names=-&utf8=string-literal
    """
    for _hex, _char in ANNOYING_CHARS:
        input_str = input_str.replace(_hex, _char)
    return input_str

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

def parse_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.read().splitlines() if not '#' in line]

def date_formatter(specify):
    if specify:
        date_str = [i for i in str(specify)]
        y = int('20' + ''.join(date_str[0:2]))
        m = int(''.join(date_str[2:4]))
        d = int(''.join(date_str[4:6]))
        specify = datetime(y, m, d, 0, 0)
        today = specify
        print(f"Specify Schedule {today}\n")
    else:
        today = datetime.combine(date.today(), datetime.min.time())
        print(f"Today's Schedule {today}\n")

    tomorrow = today + timedelta(days=1)
    return specify, today, tomorrow

def floor_minutes(time_str):
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:)(\d)(\d)(:\d{2}.\d{3}Z)")
    regex = re.match(pattern, time_str)
    return f'{regex.group(1)}{regex.group(2)}0{regex.group(4)}'

def utc_to_loacl(time_str):
    tw = timezone(timedelta(hours=+8))
    time_str = floor_minutes(time_str)
    schedule_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
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

async def get_live_stream(liver_list: list):
    async with HolodexClient() as client:
        for liver in liver_list:
            try:
                search = await client.autocomplete(liver)
                channel_id = search.contents[0].value
                channel = await client.channel(channel_id)
                name = channel.name
                # print(f'{channel.subscriber_count}')

                # NOTE: Live/Upcoming Videos (ライブ配信)
                today_schedule = {
                    "channel_id": channel_id,
                    # HACK: Max upcoming hours: 18
                    "max_upcoming_hours": 18
                }
                live = await client.get_live_streams(today_schedule)
                for stream in live:
                    start_scheduled = utc_to_loacl(stream['start_scheduled'])
                    title = stream['title']
                    url = f"https://youtu.be/{stream['id']}"

                    if check_url_exist(liver, url, result):
                        continue

                    # Create dictionary
                    if not result[start_scheduled]:
                        result[start_scheduled] = []
                    video_info = {
                        'name': name,
                        'title': title,
                        'url': url,
                        'status': 'Live/Upcoming'
                    }
                    result[start_scheduled].append(video_info)

                # NOTE: Archive Videos (アーカイブ)
                # HACK: Limit archive videos: 5
                videos = await client.videos_from_channel(channel_id, "videos", limit=5)
                for idx in range(len(videos.contents)):
                    start_scheduled = utc_to_loacl(videos.contents[idx].available_at)

                    if today_date < start_scheduled.replace(tzinfo=None) < tomorrow_date:
                        # print(f'[PASS] {astart_scheduled} > {today_date}')
                        title = videos.contents[idx].title
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, result):
                            continue

                        # Create dictionary
                        if not result[start_scheduled]:
                            result[start_scheduled] = []
                        video_info = {
                            'name': name,
                            'title': title,
                            'url': url,
                            'status': 'Archive'
                        }
                        result[start_scheduled].append(video_info)
                sleep(0.1)
            except IndexError as e:
                console.print(f"[bold red][FAIL][/bold red] cannot search videos: {liver} ({e})")
                continue
            except client_exceptions.ContentTypeError as e:
                console.print(f"[bold red][FAIL][/bold red] cannot search videos: {liver} ({e})")
                continue

async def get_collabs_stream(liver_list: list):
    async with HolodexClient() as client:
        for liver in liver_list:
            try:
                search = await client.autocomplete(liver)
                channel_id = search.contents[0].value
                channel = await client.channel(channel_id)
                name = channel.name
                # print(f'{channel.subscriber_count}')
                # NOTE: Collabs Videos (コラボ)
                # HACK: Limit archive videos: 3
                videos = await client.videos_from_channel(channel_id, "collabs", limit=3)
                for idx in range(len(videos.contents)):
                    start_scheduled = utc_to_loacl(videos.contents[idx].available_at)

                    if today_date < start_scheduled.replace(tzinfo=None) < tomorrow_date:
                        # print(f'[PASS] {astart_scheduled} > {today_date}')
                        title = videos.contents[idx].title
                        collabs_channel = videos.contents[idx].channel.name
                        url = f"https://youtu.be/{videos.contents[idx].id}"

                        if check_url_exist(liver, url, result):
                            continue

                        # Create dictionary
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
                sleep(0.1)
            except IndexError as e:
                console.print(f"[bold red][FAIL][/bold red] cannot search videos: {liver} ({e})")
                continue
            except client_exceptions.ContentTypeError as e:
                console.print(f"[bold red][FAIL][/bold red] cannot search videos: {liver} ({e})")
                continue

def print_schedule(result_dict):
    prev_date = ""
    prev_time = ""
    count = 0
    with open('test.output', 'w', encoding='utf8') as f:
        for start_scheduled in sorted(result_dict):
            # NOTE: date
            if prev_date != start_scheduled.strftime('%Y/%m/%d'):
                console.print(f"{start_scheduled.strftime('--- %Y/%m/%d ---')}")
                f.write(f"{start_scheduled.strftime('--- %Y/%m/%d ---')}\n")
                prev_date = start_scheduled.strftime('%Y/%m/%d')
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
                        #TODO: only list the first one liver
                        # print(f"{video['collabs_channel']} ({video['name']} 合作)")
                        # f.write(f"{video['collabs_channel']} ({video['name']} 合作)\n")
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
                count += 1
    print(f'Total {count} videos')

def test_floor_minutes_string():
    print(floor_minutes('2023-04-02T03:05:00.000Z'))
    print(floor_minutes('2023-04-02T12:00:00.000Z'))
    print(floor_minutes('2023-04-02T09:31:00.000Z'))
    print(floor_minutes('2023-04-02T04:27:00.000Z'))
    print(floor_minutes('2023-04-02T23:59:00.000Z'))
    sys.exit()

if __name__ == "__main__":
    specify_date = args_parser()
    specify_date, today_date, tomorrow_date = date_formatter(specify_date)
    liver_lists = ['liver.VSPO.list', 'liver.FPS.list']
    for _ in liver_lists:
        liver_list = parse_list(_)
        asyncio.run(get_live_stream(liver_list))
        asyncio.run(get_collabs_stream(liver_list))
    print_schedule(result)
