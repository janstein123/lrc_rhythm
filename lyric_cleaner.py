#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import requests
import re
import time
from bs4 import BeautifulSoup
import alphabet
from lyric_cache import LyricCache

# rhythm_table = [['a', 'ia', 'ua'],
#                 ['e', 'o', 'uo'],
#                 ['ie', 'ue', 've'],
#                 ['i', 'v', 'er'],
#                 ['u'],
#                 ['ai', 'uai'],
#                 ['ei', 'ui'],
#                 ['ao', 'iao'],
#                 ['iu', 'ou'],
#                 ['an', 'ian', 'uan'],
#                 ['ang', 'iang', 'uang'],
#                 ['eng', 'ing', 'ong', 'iong'],
#                 ['en', 'in', 'un']]
RHYTHM_NUM = 13

rhythm_dict = {'a': 0, 'ia': 0, 'ua': 0,
               'e': 1, 'o': 1, 'uo': 1,
               'ie': 2, 'ue': 2, 've': 2,
               'i': 3, 'v': 3, 'er': 3,
               'u': 4,
               'ai': 5, 'uai': 5,
               'ei': 6, 'ui': 6,
               'ao': 7, 'iao': 7,
               'iu': 8, 'ou': 8,
               'an': 9, 'ian': 9, 'uan': 9,
               'ang': 10, 'iang': 10, 'uang': 10,
               'eng': 11, 'ing': 11, 'ong': 11, 'iong': 11,
               'en': 12, 'in': 12, 'un': 12
               }

initial_list = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'z', 'c', 's', 'zh', 'ch', 'sh',
                'r', 'y', 'w']


def remove_time(lrc):
    if not lrc:
        return None

    p = re.compile(u"\[.+\]")
    lrc = re.sub(p, "", lrc)
    return lrc


def is_chinese_str(str):
    pattern = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCB ]')
    return re.search(pattern, str) is None


def remove_authors(sid, name, lrc):
    if not lrc:
        return None

    pattern = re.compile(u'\n')
    lines = re.split(pattern, lrc)
    if len(lines) < 4:
        return None

    new_lines = []
    # remove empty lines
    for line in lines:
        if len(line.strip()) > 0:
            new_lines.append(line)
    head_to_del = []
    tail_to_del = []
    for i in range(len(new_lines)):
        line = new_lines[i].strip()
        if u':' in line or u'：' in line:
            p = re.compile(u'[:：]')
            lst = re.split(p, line, 1)
            l1 = lst[0].strip()
            l2 = lst[1].strip()
            # 冒号前面是单字，并且不是以下表示作者信息的字，说明已经到了歌词正文
            # 冒号后面如果是全中文字符，且长度大于等于7，也认为是到了歌词正文了
            if (len(l1) == 1 and l1 not in (u'词', u'曲', u'编', u'鼓', u'白', u'监', u'詞', u'混', u'箫', u'編')) \
                    or (is_chinese_str(l2) and len(l2) >= 7):
                break
            else:
                head_to_del.append(i)
        else:
            # 判断第一行是否是歌名
            if i == 0:
                if line.strip() == name.strip():
                    # print "match title before"
                    head_to_del.append(i)
                else:
                    break
            # 判断紧接着作者信息的行是否是歌名
            else:
                if line.strip() == name.strip():
                    head_to_del.append(i)
                    # print "match title after"
                break

    for i in range(len(new_lines) - 1, 0, -1):
        line = new_lines[i].strip()
        if u':' in line or u'：' in line:
            p = re.compile(u'[:：]')
            lst = re.split(p, line, 1)
            l1 = lst[0].strip()
            l2 = lst[1].strip()
            # 冒号前面是单字，并且不是以下表示作者信息的字，说明已经到了歌词正文
            # 冒号后面如果是全中文字符，且长度大于等于7，也认为是到了歌词正文了
            if (len(l1) == 1 and l1 not in (u'词', u'曲', u'编', u'鼓', u'白', u'监', u'詞', u'混', u'箫', u'編')) \
                    or (is_chinese_str(l2) and len(l2) >= 7):
                break
            else:
                tail_to_del.append(i)
        # 如果一行文字中没有冒号了，认为它是到了歌词正文了
        else:
            break
    start = 0
    end = len(new_lines)

    if len(head_to_del) > 0:
        start = head_to_del[len(head_to_del) - 1] + 1

    if len(tail_to_del) > 0:
        end = tail_to_del[len(tail_to_del) - 1] - 1

    # 小于四行忽略的歌词
    if end - start + 1 < 4:
        # print '--------------------------', sid, name, '-----------------------------'
        # if end >= start:
        #     for l in new_lines[start:end + 1]:
        #         print l
        return None
    else:
        return new_lines[start:end + 1]


def remove_aside(lrc_lines=[]):
    # pattern = re.compile(u"(\(.+\))|(（.+）)")
    if not lrc_lines:
        return None

    new_lines = []
    pattern = re.compile(u"[(（].+[)）]")
    for line in lrc_lines:
        line = re.sub(pattern, '', line)
        if not line.strip():
            new_lines.append(line)
    if len(new_lines) < 4:
        return None

    return new_lines


def remove_punctuation(lrc):
    pattern = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z\n ]')
    lrc = re.sub(pattern, '', lrc)
    return lrc


def replace_space_with_line_break(lrc):
    pattern = re.compile(u' +')
    lrc = re.sub(pattern, '\n', lrc)
    return lrc


def remove_nonsense_eng_word(lrc):
    pattern = re.compile(u'oh|yeah|um|ah|yo', re.I)
    lrc = re.sub(pattern, '', lrc)
    return lrc


def remove_line_end_with_english(lrc):
    pattern = re.compile(u'.*[a-zA-Z]+\n')
    lrc = re.sub(pattern, '', lrc)
    return lrc


def remove_repeated_line(lrc):
    pattern = re.compile(u'\n')
    lines = re.split(pattern, lrc)
    newlines = []
    for l in lines:
        if len(l) > 1 and l not in newlines:
            newlines.append(l)
    return newlines


def clear_lyric(sid, name, raw_lrc):
    new_lrc = remove_time(raw_lrc)
    lines = remove_authors(sid, name, new_lrc)

    lines = remove_aside(lines)
    # print lyric_text
    # print '----------------------------'
    new_lrc = remove_punctuation(new_lrc)
    # print lyric_text
    # print '----------------------------'
    new_lrc = replace_space_with_line_break(new_lrc)
    # print lyric_text
    # print '----------------------------'
    new_lrc = remove_nonsense_eng_word(new_lrc)
    # print lyric_text
    # print '----------------------------'
    new_lrc = remove_line_end_with_english(new_lrc)
    # print lyric_text
    # print '----------------------------'
    line_list = remove_repeated_line(new_lrc)

    return line_list


def get_rhythm(word):
    p = re.compile('^(zh|ch|sh|[bpmfdtnlgkhjqxzcsryw])')
    rhythm = re.sub(p, '', word)
    return rhythm


def analyze_rhythm_result(lyric_lines=[]):
    if len(lyric_lines) < 2:
        return None

    lyric_ab_lines = [1] * len(lyric_lines)

    ab = alphabet.alphabet()
    for i in range(len(lyric_lines)):
        line_ab = ab.chinese2ab(lyric_lines[i])
        lyric_ab_lines[i] = line_ab
        # print lyric_lines[i]
        # print line_ab
    result = [[] for rows in range(RHYTHM_NUM)]

    for i in range(1, len(lyric_ab_lines)):
        last_last_ab = lyric_ab_lines[i - 2][-1] if i > 1 else None
        last_ab = lyric_ab_lines[i - 1][-1]
        current_ab = lyric_ab_lines[i][-1]

        last_ab_rhythm = get_rhythm(last_ab)
        current_ab_rhythm = get_rhythm(current_ab)

        last_rhythm_index = rhythm_dict[last_ab_rhythm]
        current_rhythm_index = rhythm_dict[current_ab_rhythm]

        if last_rhythm_index == current_rhythm_index:
            if not result[last_rhythm_index]:
                result[last_rhythm_index].append(lyric_lines[i - 1][-2:])
            result[last_rhythm_index].append(lyric_lines[i][-2:])
            print 'match last'
            print last_rhythm_index, current_rhythm_index
            print last_ab_rhythm, current_ab_rhythm
            print lyric_lines[i - 1][-1:], lyric_lines[i][-1:]

        elif last_last_ab is not None:
            last_last_ab_rhythm = get_rhythm(last_last_ab)
            last_last_rhythm_index = rhythm_dict[last_last_ab_rhythm]
            if last_last_rhythm_index == current_rhythm_index:
                if not result[last_last_rhythm_index]:
                    result[last_last_rhythm_index].append(lyric_lines[i - 2][-2:])
                result[last_last_rhythm_index].append(lyric_lines[i][-2:])
                print 'match last last'
                print last_last_rhythm_index, current_rhythm_index
                print last_last_ab_rhythm, current_ab_rhythm
                print lyric_lines[i - 2][-1:], lyric_lines[i][-1:]
    return result


# if lrc_author is not None:
#     print '--------' + lrc_author + '-----------'
# lyric_lines = clear_lyric(lyric_text)
# for l in lyric_lines:
#     print l
# result = analyze_rhythm_result(lyric_lines)
# for i in range(len(result)):
#     print i
#     for w in result[i]:
#         print w
#     print '---------------------------'

def delete_bad_songs():
    db = LyricCache()
    names = db.query_name()
    print len(names), type(names)
    to_del_ids = []
    for row in names:
        song_id = row[0]
        song_name = row[1]
        singer_name = row[3]
        # pattern = re.compile(u'cover|伴奏|remix|instrumental|kala|[(（【[].+版[]】）)]|demo|live|version|dj', re.I)
        p1 = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z0-9\u00a0 \'.,，。！!？?:]')
        p2 = re.compile(u'\([国]\)')
        p3 = re.compile(u'cover|伴奏|remix|mix|instrumental|kala|demo|live|version|d\.?j|伴唱|纯音乐', re.I)
        if (re.search(p1, song_name) and not re.search(p2, song_name)) or re.search(p3, song_name):
            to_del_ids.append((song_id,))
            print song_id, song_name
    print len(to_del_ids)
    # print str(tuple(to_del_ids))
    if len(to_del_ids) > 0:
        db.delete_songs(to_del_ids)


def len_of_lines(lines=[]):
    length = 0
    for l in lines:
        length += len(l)
    return length


def delete_short_lrc():
    db = LyricCache()
    rows = db.query_all_lrc()
    new_dict = {}
    for r in rows:
        sid = r[0]
        name = r[1]
        lines = clear_lyric(sid, name, r[2])
        # length = len_of_lines(lines)
        # if length < 50:
        #     print '-----------------------------', id, length, '-----------------------------'
        #     for line in lines:
        #         print line
        # else:
        #     new_dict[id] = lines


# delete_short_lrc()
# new_dict = sorted(a_dict.items(), key=lambda a: a[1], reverse=True)

# file = open('nums.txt', 'w')
# for a in new_dict:
#     print a[0], a[1]
#     file.write(str(a[0]) + ', ' + str(a[1]) + '\n')
# file.close()
# print len(author_dict)
# new_dict = sorted(author_dict.items(), key=lambda a: a[1], reverse=True)
#
# file = open('keys.txt', 'w')
# for a in new_dict:
#     print a[0], a[1]
#     file.write(a[0].encode('utf-8') + ', ' + str(a[1]) + '\n')
# file.close()
