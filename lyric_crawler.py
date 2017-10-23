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

useful_proxies = [
    ['http://124.232.148.7:3128', True, 0.29140000343322753, 10],
    ['http://118.31.103.7:3128', True, 0.4494999647140503, 10],
    ['http://39.88.13.3:53281', True, 0.4750000105963813, 9],
    ['http://101.37.79.125:3128', True, 0.6138999938964844, 10],
    ['http://115.233.210.218:808', True, 0.7549000263214112, 10],
    ['http://221.229.252.98:8080', True, 1.1174000263214112, 5],
    ['http://221.206.5.183:53281', True, 1.7516666650772095, 6],
    ['http://121.43.178.58:3128', True, 1.848799991607666, 10],
    ['http://116.11.254.37:80', True, 3.29699993134, 10],
    ['http://61.160.208.222:8080', True, 5.305333296457927, 9],
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.3',
    # 'Referer': 'http://www.xicidaili.com/'
}

test_id = 186016


def crawl_proxies():
    url_prefix = 'http://www.xicidaili.com/wn/'

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
                proxies.append([proxy, False])

    print len(proxies)
    test_proxy(proxies, 1)


def test_proxy(proxies=[], times=1):
    url = 'https://music.163.com/api/song/lyric'
    proxies_ok = []

    def test_repeatedly():
        success_time = 0
        all_time_consumed = 0
        for n in range(times):
            try:
                t = time.time()
                response = requests.get(url, params={'id': test_id, 'lv': 1, 'kv': 1, 'tv': -1}, headers=headers,
                                        timeout=3,
                                        verify=True,
                                        proxies={'https': proxy})
                # print response.headers
                time_consumed = time.time() - t
                all_time_consumed += time_consumed
                print response.status_code
                if response.status_code == 200:
                    print 'SUCCESS', time_consumed, 'sec', 'count:', n + 1
                    success_time += 1
                else:
                    print 'FAILED', 'count:', n + 1

            except Exception as e:
                print e
                print 'FAILED', 'count:', n + 1

        return success_time, 0 if success_time == 0 else (all_time_consumed / success_time)

    for i in range(len(proxies)):
        proxy = proxies[i][0]
        print '[' + str(i + 1) + ']', proxy
        # count_and_time = test_repeatedly()
        # s_time, tc = count_and_time[0], count_and_time[1]
        s_time, tc = test_repeatedly()
        print s_time, "time successs", 'consumed ', tc, 'sec'
        if s_time >= 1:
            proxies_ok.append([proxy, True, tc, s_time])

    print '-------------------------all', len(proxies_ok), 'useful proxies------------------------------'
    proxies_ok = sorted(proxies_ok, key=lambda a: a[2])
    for proxy in proxies_ok:
        print proxy, ','
    return proxies_ok


# crawl_proxies()

# test_proxy(useful_proxies, 10)
def request(url, params={}, is_https=False, timeout=None):

    for row in useful_proxies:
        if not row[1]:
            continue
        proxy = row[0]
        try:
            t = time.time()
            if is_https:
                param_proxies = {'http': proxy}
            else:
                param_proxies = {'https': proxy}

            response = requests.get(url, params=params, verify=is_https, proxies=param_proxies, timeout=timeout, headers=headers)
            print 'via proxy', proxy, response.status_code, time.time() - t
            if response.status_code != 200:
                row[1] = False
                continue
            else:
                return response
        except Exception as e:
            print proxy, e.message
            continue

    try:
        t = time.time()
        response = requests.get(url, params=params, timeout=timeout, headers=headers)
        print 'via 163', time.time() - t
        return response
    except Exception as e:
        request(url, params, is_https, timeout)


def download_lrc(id):
    url = 'https://music.163.com/api/song/lyric'
    response = request(url, {'id': id, 'lv': 1, 'kv': 1, 'tv': -1}, True, 1)
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
        song_name = tag.text.strip()
        if not is_good_song(song_name):
            continue
        sid = str(tag.attrs['href'])[9:]
        song_dict[sid] = song_name
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
