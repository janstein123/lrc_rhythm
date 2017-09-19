#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading

import requests
import re

import time

from lyric_cache import LyricCache
from singer_cache import SingerCache
from bs4 import BeautifulSoup


def download_lrc(id):
    url = 'https://music.163.com/api/song/lyric?id=' + id + '&lv=1&kv=1&tv=-1'
    response = requests.get(url)
    # print response.content
    rep_dict = response.json()
    try:
        # remove foreign songs
        if rep_dict['tlyric']['lyric'] is not None:
            return None
    except KeyError as e:
        print 'key error', e
        pass

    try:
        return rep_dict["lrc"]["lyric"]
    except KeyError as e:
        print 'key error', e
        return None


def find_author(lrc):
    if lrc is None:
        return None

    p = re.compile(u"作词 *[:：].+\n")
    match = re.search(p, lrc)

    if match is not None:
        match_str = match.group()
        if u':' in match_str:
            author = match_str.split(u':')[1].strip()
        elif u'：' in match_str:
            author = match_str.split(u'：')[1]

        if author:
            if len(author) > 128:
                return author[:128]
            return author

    return None


def get_top_songs(artist_id):
    response = requests.get('http://music.163.com/artist?id=' + str(artist_id))
    soup = BeautifulSoup(response.text, 'lxml')
    tag_list = soup.find('ul', attrs={'class': 'f-hide'}).find_all('a')
    print 'get_top_songs ', artist_id, len(tag_list)
    song_dict = {}
    for tag in (list(tag_list)):
        id = str(tag.attrs['href'])[9:]
        song_dict[id] = tag.text
    return song_dict


def crawl_top_song_lyric(singer_list):
    t = time.time()
    for singer in singer_list:
        artist_id = singer[0]
        artist_name = singer[1]
        top_songs = get_top_songs(artist_id)
        lyric_list = []
        i = 1
        for id in top_songs.keys():
            lyric_text = download_lrc(str(id))
            print "downloaded.....", artist_id, artist_name, id, ' ', top_songs[id], str(i) + '/' + str(
                len(top_songs)), '.............'

            if lyric_text is not None:
                lrc_author = find_author(lyric_text)
                lyric_list.append((int(id), top_songs[id], artist_id, artist_name, lrc_author, lyric_text))
            else:
                print 'lyric is none'
            i += 1
        print artist_name, len(lyric_list), "lyrics downloaded"
        db = LyricCache()
        db.insert_many(lyric_list)
    t = time.time() - t
    print 'time consumed :', t, 'sec'

# s_db = SingerCache()
# all_singers = s_db.query_all()
#
#
# singer_num = len(all_singers)
# part_len = singer_num / 10
#
# for i in range(10):
#     start = i * part_len
#     if i < 9:
#         end = start + part_len
#     else:
#         end = singer_num
#     t = threading.Thread(target=crawl_top_song_lyric, kwargs={'singer_list': all_singers[start:end]})
#     t.start()


lyric_text = download_lrc(str(36089838))
print lyric_text
# lrc_author = find_author(lyric_text)
# print lrc_author, len(lrc_author)
# l_db = LyricCache()
# l_db.insert(song_id=int(408277951), lyric=lyric_text, lyricist=lrc_author)