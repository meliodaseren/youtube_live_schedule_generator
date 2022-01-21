import re
from rich.console import Console
from datetime import (
    datetime,
    timezone,
    timedelta,
    date
)

console = Console()

def utc_to_loacl(time_str):
    tw = timezone(timedelta(hours=+8))
    time_str = floor_minutes(time_str)
    schedule_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return schedule_time.replace(tzinfo=timezone.utc).astimezone(tw)

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

def parse_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.read().splitlines() if not '#' in line]

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