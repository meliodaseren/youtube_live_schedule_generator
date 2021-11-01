#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Holodex API Documentation
    https://holodex.stoplight.io/
Python wrapper
    https://github.com/ombe1229/holodex
Requirement:
    aiohttp==3.7.4.post0
"""

import asyncio
from sys import platform
from holodex.client import HolodexClient
from collections import defaultdict
from datetime import datetime, timezone, timedelta, date

liver_list = (
    # vspo
    "小雀とと", "花芽すみれ", "花芽なずな", "一ノ瀬うるは",
    "橘ひなの", "胡桃のあ", "如月れん", "英リサ",
    "兎咲ミミ", "空澄セナ", "八雲べに", "神成きゅぴ",
    "藍沢エマ", "紫宮るな",
    # 芸人旅団 (VTuber)
    "かみと", "白雪レイド", "小森めと", "バーチャルゴリラ")

result = defaultdict(dict)
today_date = datetime.combine(date.today(), datetime.min.time())
tomorrow_date = today_date + timedelta(days=1)

def utc_to_loacl(utc_dt):
    tw = timezone(timedelta(hours=+8))
    schedule_time = datetime.strptime(utc_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
    return schedule_time.replace(tzinfo=timezone.utc).astimezone(tw)

async def main():
    async with HolodexClient() as client:
        for liver in liver_list:
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
            # HACK: Limit archive videos: 3
            videos = await client.videos_from_channel(channel_id, "videos", limit=3)
            for idx in range(len(videos.contents)):
                start_scheduled = utc_to_loacl(videos.contents[idx].available_at)
                # print(f'       {liver} {idx} {astart_scheduled} vs {today_date}')
                if today_date < start_scheduled.replace(tzinfo=None) < tomorrow_date:
                    # print(f'[PASS] {astart_scheduled} > {today_date}')
                    title = videos.contents[idx].title
                    url = f"https://youtu.be/{videos.contents[idx].id}"

                    # TODO: check the same url with live/upcoming videos
                    if url in [v['url'] for t in result for v in result[t]]:
                        print(f'skip live/upcoming videos: {url}')
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

            # NOTE: Collabs Videos (コラボ)
            # HACK: Limit archive videos: 3
            videos = await client.videos_from_channel(channel_id, "collabs", limit=3)
            for idx in range(len(videos.contents)):
                start_scheduled = utc_to_loacl(videos.contents[idx].available_at)
                # print(f'       {liver} {idx} {astart_scheduled} vs {today_date}')
                if today_date < start_scheduled.replace(tzinfo=None) < tomorrow_date:
                    # print(f'[PASS] {astart_scheduled} > {today_date}')
                    title = videos.contents[idx].title
                    url = f"https://youtu.be/{videos.contents[idx].id}"

                    # TODO: check the same url with live/upcoming videos
                    if url in [v['url'] for t in result for v in result[t]]:
                        print(f'skip live/upcoming videos: {url}')
                        continue

                    # Create dictionary
                    if not result[start_scheduled]:
                        result[start_scheduled] = []
                    video_info = {
                        'name': name,
                        'title': title,
                        'url': url,
                        'status': 'Collabs'
                    }
                    result[start_scheduled].append(video_info)

# Policy for windows: https://docs.python.org/3/library/asyncio-policy.html
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin":
    pass
elif platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

if __name__ == "__main__":
    print(f"Today's Schedule {today_date}\n")
    prev_time = ""
    for start_scheduled in sorted(result):
        for video in result[start_scheduled]:
            # print(start_scheduled.strftime('%H:%M (%m/%d)'))
            if prev_time != start_scheduled.strftime('%H:%M'):
                print(start_scheduled.strftime('%H:%M'))
                prev_time = start_scheduled.strftime('%H:%M')
            if video['status'] == 'Collabs':
                print(f"{video['name']} (コラボ 合作)")
            else:
                print(f"{video['name']}")
            print(f"{video['title']}")
            print(f"{video['url']}\n")
