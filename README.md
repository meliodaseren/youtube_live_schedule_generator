## Schedule Generator

Generate today schedule by liver list

1. Modfiy the liver name in liver.list

2. `./holodex-python.py`

Output:

```sh
{Time}
{Channel Name} ({Collabs Liver} 合作)
{Video Title}
{Video URL}
...
```

Requirement:

```sh
holodex==0.8.7
aiohttp==3.7.4.post0
rich==10.12.0
```

---

Last week clips

1. Modfiy the liver name in liver.clips.list

2. `./holodex-python.clips.py`

```sh
{Time}
{Clips Channel Name} ({Collabs Liver} 剪輯)
{Video Title}
{Video URL}
...
```
