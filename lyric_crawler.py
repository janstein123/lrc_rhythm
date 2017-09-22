#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading

import requests
import re

import time

from lyric_cache import LyricCache
from singer_cache import SingerCache
from all_singer_cache import AllSingerCache
from bs4 import BeautifulSoup


def download_lrc(id):
    url = 'https://music.163.com/api/song/lyric'
    response = requests.get(url, {'id': id, 'lv': 1, 'kv': 1, 'tv': -1})
    # print response.content
    rep_dict = response.json()
    # try:
    #     # remove foreign songs
    #     if rep_dict['tlyric']['lyric'] is not None:
    #         print "foreign song, ignore!!!"
    #         return None
    # except KeyError as e:
    #     print '1 key error', e
    #     pass

    try:
        return rep_dict["lrc"]["lyric"]
    except KeyError as e:
        print '2 key error', e
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


def is_good_song(song_name):
    p1 = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z0-9\u00a0 \'.,，。！!？?:]')
    p2 = re.compile(u'\([国]\)')
    p3 = re.compile(u'cover|伴奏|remix|mix|instrumental|kala|demo|live|version|d\.?j|伴唱|纯音乐', re.I)
    if (re.search(p1, song_name) and not re.search(p2, song_name)) or re.search(p3, song_name):
        print '[' + song_name+ '] is not a good song'
        return False
    return True


def get_top_songs(artist_id):
    response = requests.get('http://music.163.com/artist?id=' + str(artist_id))
    soup = BeautifulSoup(response.text, 'lxml')
    tag_list = soup.find('ul', attrs={'class': 'f-hide'}).find_all('a')
    song_dict = {}
    for tag in (list(tag_list)):
        # print tag.text
        if not is_good_song(tag.text):
            continue
        sid = str(tag.attrs['href'])[9:]
        song_dict[sid] = tag.text
    return song_dict


def crawl_top_song_lyric(singer_list, start, end):
    t = time.time()
    singer_index = start
    for singer in singer_list:
        artist_id = singer[0]
        artist_name = singer[1]
        top_songs = get_top_songs(artist_id)
        print "[" + threading.currentThread().getName() + '] get_top_songs of ', artist_id, artist_name, len(top_songs)
        lyric_list = []
        i = 1
        for sid in top_songs.keys():
            lyric_text = download_lrc(sid)
            print "[" + threading.currentThread().getName() + "] downloaded.....", artist_id, artist_name, sid, ' ', \
            top_songs[sid], str(i) + '/' + str(
                len(top_songs)), '.............'
            i = i + 1
            if lyric_text is not None:
                lrc_author = find_author(lyric_text)
                lyric_list.append((int(sid), top_songs[sid], artist_id, artist_name, lrc_author, lyric_text))
            else:
                print 'lyric is none'

        print singer_index, 'in [', start, end, ']', artist_name, "all", len(lyric_list), " lyrics downloaded"
        db = LyricCache()
        db.insert_many(lyric_list)
        singer_index = singer_index + 1
    t = time.time() - t
    print "[" + threading.currentThread().getName() + "]", 'time consumed :', t, 'sec'


s_db = AllSingerCache()
all_singers = s_db.query_all()

singer_num = len(all_singers)
print singer_num
part_len = singer_num / 10

for i in range(10):
    start = i * part_len
    if i < 9:
        end = start + part_len
    else:
        end = singer_num
    t = threading.Thread(target=crawl_top_song_lyric,
                         kwargs={'singer_list': all_singers[start:end], 'start': start, 'end': end - 1})
    t.start()

# lyric_text = download_lrc(str(36089838))
# print lyric_text
# lrc_author = find_author(lyric_text)
# print lrc_author, len(lrc_author)
# l_db = LyricCache()
# l_db.insert(song_id=int(408277951), lyric=lyric_text, lyricist=lrc_author)
# print download_lrc(186016)

# get_top_songs(1111005)

# cover_pattern = re.compile(u'cover|伴奏|remix|instrumental|kala|[(（【[].+版[]】）)]|demo|live|version|dj', re.I)
# print re.search(cover_pattern, u'(xianc版b)')
# p = re.compile()
