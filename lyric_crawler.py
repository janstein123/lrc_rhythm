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

useful_proxies = (
    'http://219.135.164.245:3128',
    # 'http://61.160.208.222:8080',
    'http://122.72.32.83:80',
    'http://118.31.103.7:3128',
    'http://119.23.161.182:3128',
    'http://139.224.24.26:8888',
    'http://42.202.130.246:3128',
    'http://222.222.169.60:53281',
    'http://124.232.148.7:3128',
    'http://61.158.111.142:53281',
    'http://222.89.112.48:53281',
    'http://58.255.45.23:9000',
    'http://119.90.248.245:9999',
    'http://116.236.151.166:8080',
    'http://113.108.204.74:8888',
    'http://58.17.116.115:53281',
    'http://115.233.210.218:808',
)
proxies = {
    'https': 'http://220.248.207.105:53281',
    'http': 'http://110.73.7.165:8123',
}


def crawl_proxies():
    url_prefix = 'http://www.xicidaili.com/wn/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.3',
        # 'Referer': 'http://www.xicidaili.com/'
    }
    proxies = []
    for page in range(2):
        url = url_prefix + str(page + 1)
        response = requests.get(url, headers=headers)
        # print response.text
        soup = BeautifulSoup(response.text, 'lxml')
        tags = soup.find('table', attrs={'id': 'ip_list'}).find_all('tr')
        for tag in tags:
            tds = tag.find_all('td')
            if len(tds) > 3:
                ip = tds[1].text.strip()
                port = tds[2].text.strip()
                proxy = 'http://' + ip + ':' + port
                # print proxy
                proxies.append(proxy)

    print len(proxies)
    url = 'https://music.163.com/api/song/lyric'
    proxies_ok = []
    for proxy in proxies:
        print proxy
        try:
            t = time.time()
            response = requests.get(url, params={'id': id, 'lv': 1, 'kv': 1, 'tv': -1}, headers=headers, timeout=10,
                                    verify=False,
                                    proxies={'https': proxy})
            # print response.headers
            print 'SUCCESS', time.time() - t, 'sec'
            proxies_ok.append(proxy)
        except Exception as e:
            # print e
            print 'FAILED'
    print '-------------------------all', len(proxies_ok), 'useful proxies------------------------------'
    for proxy in proxies_ok:
        print proxy


# crawl_proxies()


def test_proxy():
    url = 'http://ip.chinaz.com'
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        soup = BeautifulSoup(response.text, 'lxml')
        my_ip = soup.find('p', attrs={'class': 'getlist pl10'})
        print response.text
        print my_ip
    except Exception as e:
        print 'test_proxy', e


# test_proxy()


def download_lrc(id):
    url = 'https://music.163.com/api/song/lyric'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    for i in range(len(useful_proxies)):
        try:
            t = time.time()
            response = requests.get(url, params={'id': id, 'lv': 1, 'kv': 1, 'tv': -1}, headers=headers, timeout=5,
                                    verify=False,
                                    proxies={'https': useful_proxies[i]})
            print 'via proxy', i, useful_proxies[i], response.status_code, time.time() - t
            if response.status_code != 200:
                continue
        except Exception as e:
            if i < len(useful_proxies) - 1:
                continue
            else:
                print 'via 163'
                response = requests.get(url, params={'id': id, 'lv': 1, 'kv': 1, 'tv': -1}, headers=headers)
        # print response.headers
        # print response.content
        rep_dict = response.json()

        try:
            lrc = rep_dict["lrc"]["lyric"]
            if len(lrc) < 50:
                print 'lrc is too short'
                return None
            return lrc
        except KeyError as e:
            print '2 key error', e
            return None

# print download_lrc(29393117)


def find_author(lrc):
    if lrc is None:
        return None

    p = re.compile(u"词 *[:：].+\n")
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
        print '[' + song_name + '] is not a good song'
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
            t1 = time.time()
            lyric_text = download_lrc(sid)
            print "[" + threading.currentThread().getName() + "] downloaded.....", artist_id, artist_name, sid, ' ', \
                top_songs[sid], str(i) + '/' + str(
                len(top_songs)), '.............', time.time() - t1, 'sec'
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

# s_db = AllSingerCache()
# all_singers = s_db.query_all()
#
# singer_num = len(all_singers)
# print singer_num
# part_len = singer_num / 20
#
# for i in range(20):
#     start = i * part_len
#     if i < 9:
#         end = start + part_len
#     else:
#         end = singer_num
#     t = threading.Thread(target=crawl_top_song_lyric,
#                          kwargs={'singer_list': all_singers[start:end], 'start': start, 'end': end - 1})
#     t.start()

# lyric_text = download_lrc(str(36089838))
# print lyric_text
# lrc_author = find_author(lyric_text)
# print lrc_author, len(lrc_author)
# l_db = LyricCache()
# l_db.insert(song_id=int(408277951), lyric=lyric_text, lyricist=lrc_author)

# get_top_songs(1111005)
