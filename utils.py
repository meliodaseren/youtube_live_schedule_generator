import re
from rich.console import Console
from typing import Tuple
from datetime import (
    datetime,
    timezone,
    timedelta,
    date
)

console = Console()

def time_formatter(time_str):
    time_str = utc_to_local(time_str)
    return time_str

def utc_to_local(time_str):
    tw = timezone(timedelta(hours=+8))
    time_str, hour_carry = round_off_time(time_str)
    schedule_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    if hour_carry:
        schedule_time = schedule_time + timedelta(hours=1)
        console.print(f"carry hour to {schedule_time}")
    return schedule_time.replace(tzinfo=timezone.utc).astimezone(tw)

def get_live_date(specify, input_days=1):
    if specify:
        date_str = [i for i in str(specify)]
        y = int('20' + ''.join(date_str[0:2]))
        m = int(''.join(date_str[2:4]))
        d = int(''.join(date_str[4:6]))
        specify = datetime(y, m, d, 0, 0)
        first_day = specify
        print(f"Specify Schedule {first_day}")
    else:
        first_day = datetime.combine(date.today(), datetime.min.time())
        print(f"Today's Schedule {first_day}")

    end_date = first_day + timedelta(days=input_days)
    print(f"Schedule from {first_day} to {end_date}\n")
    return specify, first_day, end_date

def get_archive_date(specify, input_days=7):
    if specify:
        date_str = [i for i in str(specify)]
        y = int('20' + ''.join(date_str[0:2]))
        m = int(''.join(date_str[2:4]))
        d = int(''.join(date_str[4:6]))
        specify = datetime(y, m, d, 0, 0)
        first_day = specify
        print(f"Specify Schedule {first_day}")
    else:
        first_day = datetime.combine(date.today(), datetime.min.time())
        print(f"Today's Schedule {first_day}")

    first_day = first_day + timedelta(days=1)
    prev_day = first_day - timedelta(days=input_days)
    print(f"Videos from {prev_day} to {first_day}\n")
    return specify, prev_day, first_day

def round_off_time(time_str) -> Tuple[str, bool]:
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d)(\d):(\d{2}).(\d{3}Z)")
    regex = re.match(pattern, time_str)
    str_date = regex.group(1)
    str_hours = regex.group(2)
    str_minutes = f'{regex.group(3)}{regex.group(4)}'
    # str_seconds = regex.group(5)
    str_seconds = '00'
    str_zone = regex.group(6)
    if (regex.group(3) == '0') or (str_minutes == '10'):
        # 01 ~ 10 -> floor to 00
        str_minutes = '00'
    elif str_minutes == '50':
        # 50 -> carry to next hour
        str_minutes = '00'
        console.print(f"[bold orange][DEBUG][/bold orange] {time_str} ", end='')
        return (
            f'{str_date}T{str_hours}:{str_minutes}:{str_seconds}.{str_zone}',
            True
        )
    elif regex.group(4) in ('0', '1', '2', '3', '4'):
        str_minutes = f'{regex.group(3)}0'
        if str_minutes == '10':
            str_minutes = '00'
    elif regex.group(4) in ('5', '6', '7', '8', '9'):
        str_minutes = f'{int(regex.group(3))+1}0'
        if str_minutes == '60':
            # carry to next hour
            str_minutes = '00'
            console.print(f"[bold orange][DEBUG][/bold orange] {time_str} ", end='')
            return (
                f'{str_date}T{str_hours}:{str_minutes}:{str_seconds}.{str_zone}',
                True
            )
    return (
        f'{str_date}T{str_hours}:{str_minutes}:{str_seconds}.{str_zone}',
        False
    )

def parse_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        print(f'parse {filepath}')
        return [line.strip() for line in f.read().splitlines() if not '#' in line]

def check_channel_in_list(channel_name: str, liver_list: list):
    for liver in liver_list:
        if liver in channel_name:
            # console.print(f"[bold yellow][WARN ][/bold yellow] \"{channel_name}\" in liver list")
            return True

def check_url_exist(name: str, url: str, video_dict: dict):
    # TODO: check the same url with live/upcoming videos
    if url in [v['url'] for t in video_dict for v in video_dict[t]]:
        # console.print(f"[bold yellow][WARN ][/bold yellow] skip duplicate videos: {url} ({name})")
        return True

def wrap_title(title: str):
    # if len(title) > 30:
    #     pattern = re.search(r'^(.*)【(.*)】(.*)【(.*)】(.*)$', title)
    #     if pattern:
    #         title = (
    #             f'{pattern.group(1).strip()}'
    #             f'【{pattern.group(2).strip()}】{pattern.group(3).strip()}\n'
    #             f'【{pattern.group(4).strip()}】{pattern.group(5).strip()}'
    #         )
    return title

def remove_annoying_unicode(input_str):
    """
    https://www.utf8-chartable.de/unicode-utf8-table.pl?start=8064&names=-&utf8=string-literal
    """
    for _hex, _char in ANNOYING_CHARS:
        input_str = input_str.replace(_hex, _char)
    return input_str

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
    ('\u2028', ''),
    ('\u2029', ''),
    ('\u202a', ''),
    ('\u202b', ''),
    ('\u202c', ''),
    ('\u202d', ''),
    ('\u202e', ''),
    ('\u202f', ''),
    ('\u205f', ''),
    ('\u2060', ''),
    ('\u2061', ''),
    ('\u2062', ''),
    ('\u2063', ''),
    ('\u2064', ''),
    ('\u2065', ''),
    ('\u2066', ''),
    ('\u2067', ''),
    ('\u2068', ''),
    ('\u2069', ''),
    ('\u206a', ''),
    ('\u206b', ''),
    ('\u206c', ''),
    ('\u206d', ''),
    ('\u206e', ''),
    ('\u206f', ''),
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

if __name__ == '__main__':
    # import sys
    # from argparse import ArgumentParser

    # def args_parser():
    #     specify_date = '220228'
    #     if specify_date:
    #         if len(specify_date) == 6:
    #             return specify_date
    #         else:
    #             sys.exit(1)
    #     else:
    #         return specify_date
    
    # input_date = args_parser()
    # specify_date, start_date, end_date = get_live_date(input_date)
    # specify_date, start_date, end_date = get_archive_date(input_date, input_days=3)

    test_list = [
        '2022-03-09T11:02:02.000Z',
        '2022-03-09T11:09:02.000Z',
        '2022-03-09T11:10:02.000Z',

        '2022-02-25T11:20:14.000Z',
        '2022-02-25T11:22:14.000Z',

        '2022-02-25T11:27:14.000Z',
        '2022-02-18T11:30:44.000Z',
        '2022-02-18T11:34:44.000Z',

        '2022-02-18T11:45:03.000Z',
        '2022-02-18T11:48:03.000Z',

        '2022-02-08T11:50:03.000Z',
        '2022-02-08T11:58:03.000Z'
    ]
    for test_str in test_list:
        print(f'{test_str} -> {time_formatter(test_str)}')
