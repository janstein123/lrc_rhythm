#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
import time
from one_singer_lyric_cache import OneSingerCache
from bs4 import BeautifulSoup
from all_singer_cache import AllSingerCache
import lyric_crawler
import logging
import threading

my_logger = logging.getLogger("one_singer_crawler")


def get_all_albums(artist_id):
    albums = []

    def download_one_page(offset=0):
        response = requests.get('http://music.163.com/artist/album', {'id': artist_id, 'limit': 12, 'offset': offset},
                                verify=True,
                                proxies={'http': lyric_crawler.useful_proxies[0][0]})
        # print response.text
        soup = BeautifulSoup(response.text, 'lxml')
        clazz = soup.find('ul', attrs={'class': 'm-cvrlst m-cvrlst-alb4 f-cb'})
        if clazz:
            tags = clazz.find_all('a', attrs={'class': 'tit s-fc0'})
            for tag in tags:
                aid = tag.attrs['href'][10:]
                albums.append([aid, tag.text])
                print aid, tag.text

        u_page = soup.find('div', attrs={'class': 'u-page'})
        if u_page is not None:
            next_page = u_page.find('a', attrs={'class': re.compile('zbtn znxt'), 'href': re.compile('/artist/album')})
            if next_page is not None:
                download_one_page(offset + 12)

    download_one_page()

    return albums


def get_songs_in_album(album_id):
    songs = {}
    response = requests.get('http://music.163.com/album', {'id': album_id}, verify=True,
                            proxies={'http': lyric_crawler.useful_proxies[0][0]})
    soup = BeautifulSoup(response.text, 'lxml')
    song_list = soup.find('div', attrs={'id': 'song-list-pre-cache'})
    if song_list:
        song_tags = song_list.find_all('a')
        for tag in song_tags:
            songs[tag['href'][9:]] = tag.text
    return songs


lrc_db = OneSingerCache('all_songs_of_top_singer')


def has_this_album(album_id):
    return lrc_db.query_album(album_id) is not None


def is_valid_song_name(song_name):
    p1 = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z0-9\u00a0\u2028\ue3ac 　\'.,，。！!？?:]')
    p2 = re.compile(u'\([国]\)')
    p3 = re.compile(u'cover|伴奏|remix|mix|instrumental|kala|demo|live|version|d\.?j|伴唱|纯音乐', re.I)
    if (re.search(p1, song_name) and not re.search(p2, song_name)) or re.search(p3, song_name):
        return False
    return True


def get_all_songs_of_singer(artist_id, artist_name):
    # db = OneSingerCache('singer' + str(artist_id))
    print artist_name, ' all albums:'
    albums = get_all_albums(artist_id)

    for i in range(len(albums)):
        aid = albums[i][0]
        album_name = albums[i][1]
        print '--------', aid, album_name, artist_name, '--------'
        p = re.compile(u'音乐会|演唱会|精选|live|现场录音|世界巡回|concert', re.I)
        if re.search(p, album_name):
            print 'ignore this album...'
            continue

        songs = get_songs_in_album(aid)
        lyric_list = []
        j = 0
        for sid in songs.keys():
            song_name = songs[sid]
            if not is_valid_song_name(song_name):
                print threading.currentThread().getName(), "ignore.....", artist_id, artist_name, sid, song_name, str(
                    j + 1) + '/' + str(len(songs.keys())), str(i + 1) + '/' + str(len(albums)), '.............'
                continue
            print threading.currentThread().getName(), "downloading.....", artist_id, artist_name, sid, song_name, str(
                j + 1) + '/' + str(len(songs.keys())), str(i + 1) + '/' + str(len(albums)), '.............'
            lyric_text = lyric_crawler.download_lrc(sid)
            if lyric_text is not None:
                # lrc_author = lyric_crawler.find_author(lyric_text)
                lyric_list.append((int(sid), song_name, artist_id, artist_name, aid, album_name, lyric_text))
                print 'dl OK'
            else:
                print 'lyric is none'
            j = j + 1

        if len(lyric_list) > 0:
            print '************** saving', aid, album_name, artist_name, ' **************'
            lrc_db.insert_many(lyric_list)
            print artist_name, album_name, 'save OK'


singer_db = AllSingerCache()
top_singers = singer_db.query_all()

# for i in range(0, len(top_singers), 3):
#     singer = top_singers[i]
#     singer2 = top_singers[i+1]
#     singer3 = top_singers[i+2]
#
#     print singer[0], singer[1], singer2[0], singer2[1], singer3[0], singer3[1]

thread_num = 3


def crawl_run(thread_index):
    print thread_index
    for i in range(thread_index, len(top_singers), 3):
        singer = top_singers[i]
        sid = singer[0]
        sname = singer[1]
        # if sname == u'王杰' or sname == u'汪峰' or sname == u'谭咏麟':
        #     print sid, sname
        if (thread_index == 0 and sid >= 7220) or (thread_index == 1 and sid >= 7570) or (
                        thread_index == 2 and sid >= 9292):
            get_all_songs_of_singer(sid, sname)


for i in range(thread_num):
    t = threading.Thread(target=crawl_run, args=(i,))
    t.start()
    time.sleep(1)
