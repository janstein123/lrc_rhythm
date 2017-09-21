#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from all_singer_cache import AllSingerCache

SINGER_TYPE_MALE = 1001
SINGER_TYPE_FEMALE = 1002


def get_all_singers(singer_type, initial=-1):
    # response = requests.get('http://music.baidu.com/artist/cn/male')
    response = requests.get('https://music.163.com/discover/artist/cat', {'id': singer_type, 'initial': initial})
    soup = BeautifulSoup(response.text, 'lxml')
    # < ul class ="m-cvrlst m-cvrlst-5 f-cb" id="m-artist-box" >
    singer_tags = soup.find('ul', attrs={'class': 'm-cvrlst m-cvrlst-5 f-cb'}).find_all('a', attrs={
        'class': 'nm nm-icn f-thide s-fc0'})
    singers = []
    for singer in singer_tags:
        name = singer.text
        id = int(singer.attrs['href'].strip(' ')[11:])
        print id, name
        singers.append((id, name, singer_type, initial))
    print '--------------------------------------'
    return singers


db = AllSingerCache()
for i in range(ord('A'), ord('Z') + 1):
    singers = []
    singers.extend(get_all_singers(SINGER_TYPE_MALE, i))
    singers.extend(get_all_singers(SINGER_TYPE_FEMALE, i))
    db.insert_many(singers)


