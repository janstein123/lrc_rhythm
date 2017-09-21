#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
import time
from one_singer_lyric_cache import OneSingerCache
from bs4 import BeautifulSoup

import lyric_crawler


def get_all_albums(artist_id):
    albums = {}

    def download_one_page(offset=0):
        response = requests.get('http://music.163.com/artist/album', {'id': artist_id, 'limit': 12, 'offset': offset})
        soup = BeautifulSoup(response.text, 'lxml')
        tags = soup.find('ul', attrs={'class': 'm-cvrlst m-cvrlst-alb4 f-cb'}).find_all('a',
                                                                                        attrs={'class': 'tit s-fc0'})
        for tag in tags:
            aid = tag.attrs['href'][10:]
            albums[aid] = tag.text
            print aid, tag.text

        u_page = soup.find('div', attrs={'class': 'u-page'})
        if u_page is not None:
            next_page = u_page.find('a', attrs={'class': re.compile('zbtn znxt'), 'href': re.compile('/artist/album')})
            if next_page is not None:
                download_one_page(offset + 12)

    download_one_page()
    return albums


def get_songs_in_album(album_id):
    response = requests.get('http://music.163.com/album', {'id': album_id})
    soup = BeautifulSoup(response.text, 'lxml')
    song_tags = soup.find('div', attrs={'id': 'song-list-pre-cache'}).find_all('a')
    songs = {}
    for tag in song_tags:
        songs[tag['href'][9:]] = tag.text
    return songs


def get_all_songs_of_singer(artist_id, artist_name):
    db = OneSingerCache('singer' + str(artist_id))
    albums = get_all_albums(artist_id)
    for id in albums.keys():
        print '--------', id, albums[id], '--------'
        if u'演唱会' in albums[id]:
            continue
        songs = get_songs_in_album(id)
        lyric_list = []
        for id in songs.keys():
            lyric_text = lyric_crawler.download_lrc(id)
            print "downloaded.....", artist_id, artist_name, id, ' ', songs[id], '.............'

            if lyric_text is not None:
                lrc_author = lyric_crawler.find_author(lyric_text)
                lyric_list.append((int(id), songs[id], artist_id, artist_name, lrc_author, lyric_text))
            else:
                print 'lyric is none'
        if len(lyric_list) > 0:
            db.insert_many(lyric_list)


get_all_songs_of_singer(6452, u'周杰伦')

