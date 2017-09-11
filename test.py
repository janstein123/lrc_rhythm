#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import requests
import re
import time
from bs4 import BeautifulSoup
import alphabet

rhythm_table = [['a', 'ia', 'ua'],
                ['e', 'o', 'uo'],
                ['ie', 'ue', 've'],
                ['i', 'v', 'er'],
                ['u'],
                ['ai', 'uai'],
                ['ei', 'ui'],
                ['ao', 'iao'],
                ['iu', 'ou'],
                ['an', 'ian', 'uan'],
                ['ang', 'iang', 'uang'],
                ['eng', 'ing', 'ong', 'iong'],
                ['en', 'in', 'un']]

initial_table = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'z', 'c', 's', 'zh', 'ch', 'sh',
                 'r']


def getSongList():
    response = requests.get("https://music.163.com/#/discover/artist")
    print response.text
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    print soup.find('div', attrs={"class": "j-showoff u-showoff f-hide"})


def downloadLrcById(id):
    url = 'https://music.163.com/api/song/lyric?id=' + id + '&lv=1&kv=1&tv=-1'
    # data = urllib2.urlopen(url).read()
    response = requests.get(url)
    print response.content
    return response.json()["lrc"]["lyric"]


def process_lrc(lrc):
    lines = lrc.split('\n')
    newlines = []
    author = None
    for line in lines:
        print line
        if len(line) != 0 and (':' not in line) and ('：' not in line):
            p = re.compile(u"[^\u4e00-\u9fa5]$")
            found_list = re.findall(p, line)
            if len(found_list) > 0:
                print found_list
            # avoid repeated line
            if line not in newlines:
                newlines.append(line)
        elif len(line) != 0:
            p = re.compile(u"^(作词)(:|：)")
            match = re.match(p, line)
            if match is not None:
                parts = line.split(':')
                if len(parts) < 2:
                    parts = line.split('：')
                if len(parts) > 1:
                    author = parts[1]
    return newlines, author


# downloadLrcById('471385043')
# lrc = downloadLrcById('28793140').encode('utf8')
# print lrc

def clear_lrc(lrc):
    # remove time line
    pattern = re.compile("\[.+\]")
    lrc = re.sub(pattern, "", lrc)

    #remove aside
    pattern = re.compile("(\(.+\))|(（.+）)")
    lrc = re.sub(pattern, '', lrc)

    # remove all spaces
    pattern = re.compile(r" +")
    lrc = re.sub(pattern, "", lrc)

    return lrc


def find_author(lrc):
    p = re.compile(u"作词 *[:：].+\n")
    match = re.search(p, lrc)

    if match is not None:
        match_str = match.group()
        print match_str
        if ':' in match_str:
            author = match_str.split(':')[1].strip()
            if author:
                return author
        elif '：' in match_str:
            author = match_str.split('：')[1]
            if author:
                return author
    return None


def remove_time(lrc):
    p = re.compile(u"\[.+\]")
    lrc = re.sub(p, "", lrc)
    return lrc


def remove_authors(lrc):
    p = re.compile(u".*[：:].*\n")
    lrc = re.sub(p, "", lrc)
    return lrc


def remove_aside(lrc):
    # pattern = re.compile(u"(\(.+\))|(（.+）)")
    pattern = re.compile(u"[(（].+[)）]")
    lrc = re.sub(pattern, '', lrc)
    return lrc


# lyric_text = downloadLrcById('479028095')
lyric_text = u"fafa作曲 : 周杰伦\n[00:01.00] 作词 : 方文山 \n[00:22.170]从前从前有只猫头鹰 \n (kjfladjl大姐夫那就对了）\n hello my world(发链接了)\n"
lrc_author = find_author(lyric_text)
if lrc_author is not None:
    print '--------'+lrc_author+'-----------'
lyric_text = remove_time(lyric_text)
print lyric_text
print '----------------------------'
lyric_text = remove_authors(lyric_text)
print lyric_text
print '----------------------------'
lyric_text = remove_aside(lyric_text)
print lyric_text


# lyric_text = clear_lrc(lyric_text)

# print lyric_text

# lrc_lines, author = process_lrc(lyric_text)

# print author
#
# line_dict = {}
# for line in lrc_lines:
#     print line
#     ab = alphabet.alphabet()
#     line_ab = ab.chinese2ab(line)
#     line_dict[line] = line_ab

# for k in line_dict.keys():
#     print k, line_dict[k]


