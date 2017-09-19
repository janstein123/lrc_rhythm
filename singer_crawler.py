#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from singer_cache import SingerCache

SINGER_TYPE_MALE = 1001
SINGER_TYPE_FEMALE = 1002
SINGER_TYPE_BAND = 1003

singers_to_del = [u'回音哥',
                  u'石进',
                  u'Pianoboy',
                  u'eliaqsopa',
                  u'有声小说',
                  u'中国人民解放军军乐团',
                  u'中国国家交响乐团',
                  u'小紫荆儿童合唱团',
                  u'网易游戏',
                  u'英雄联盟',
                  u'风潮唱片',
                  u'Robynn & Kendy',
                  u'Six City',
                  u'poppin 国王',
                  u'打扰一下乐团']


def get_top_100_singers(singer_type):
    # response = requests.get('http://music.baidu.com/artist/cn/male')
    response = requests.get('https://music.163.com/discover/artist/cat', {'id': singer_type})
    soup = BeautifulSoup(response.text, 'lxml')
    # < ul class ="m-cvrlst m-cvrlst-5 f-cb" id="m-artist-box" >
    singer_tags = soup.find('ul', attrs={'class':'m-cvrlst m-cvrlst-5 f-cb'}).find_all('a', attrs={'class':'nm nm-icn f-thide s-fc0'})
    singers = []
    for singer in singer_tags:
        name = singer.text
        if name in singers_to_del:
            continue
        id = int(singer.attrs['href'].strip(' ')[11:])
        singers.append((id, singer.text, singer_type))
    return singers


all_singers = []
m_singers = get_top_100_singers(SINGER_TYPE_MALE)
f_singers = get_top_100_singers(SINGER_TYPE_FEMALE)
b_singers = get_top_100_singers(SINGER_TYPE_BAND)

all_singers.extend(m_singers)
all_singers.extend(f_singers)
all_singers.extend(b_singers)

print len(all_singers)

cache = SingerCache()
cache.insert_many(all_singers)