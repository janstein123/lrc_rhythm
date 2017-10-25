#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import re
import time
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
# 一 七 i (—i) v (er) / i v（西）
# 姑 苏 u / u （出）
# 发 花 a ia ua /a (佳)
# 梭 波 o e uo / o e （坐）
# 乜 斜 ie ve / ie ve （捏）
# 怀 来 ai uai /ai （来）
# 灰 堆 ei uei / ei （北）
# 遥 条 ao iao / ao （俏）
# 由 求 ou iou /ou （扭）
# 言 前 an ian uan van /an（南）
# 人 辰 en in uen vn / en （人）
# 江 阳 ang iang uang /ang （房）
# 中 东 eng ing ueng ong iong /eng ong （东）

rhythm_dict = {
    'i': 0, 'v': 0, 'er': 0,
    'u': 1,
    'a': 2, 'ia': 2, 'ua': 2,
    'e': 3, 'o': 3, 'uo': 3,
    'ie': 4, 'ue': 4, 've': 4,
    'ai': 5, 'uai': 5,
    'ei': 6, 'ui': 6,
    'ao': 7, 'iao': 7,
    'iu': 8, 'ou': 8,
    'an': 9, 'ian': 9, 'uan': 9,
    'en': 10, 'in': 10, 'un': 10,
    'ang': 11, 'iang': 11, 'uang': 11,
    'eng': 12, 'ing': 12, 'ong': 12, 'iong': 12,
}

initial_list = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'z', 'c', 's', 'zh', 'ch', 'sh',
                'r', 'y', 'w']


def get_rhythm(abs=[]):
    rhythms = []
    for ab in abs:
        if ab in ['ju', 'qu', 'xu', 'yu']:
            ab = ab.replace('u', 'v')
        p = re.compile('^(zh|ch|sh|[bpmfdtnlgkhjqxzcsryw])')
        rhythm = re.sub(p, '', ab)
        rhythms.append(rhythm)
    return rhythms


def analyze_rhythm_result(lyric_lines=[]):

    lyric_ab_lines = [1] * len(lyric_lines)

    ab = alphabet.alphabet()
    for i in range(len(lyric_lines)):
        line_ab = ab.chinese2ab(lyric_lines[i])
        lyric_ab_lines[i] = line_ab
        # print lyric_lines[i]
        # print line_ab
    result = [[] for rows in range(RHYTHM_NUM)]

    for i in range(1, len(lyric_ab_lines)):
        last_last_ab = lyric_ab_lines[i - 2][-1:] if i > 1 else None
        last_ab = lyric_ab_lines[i - 1][-1:]
        current_ab = lyric_ab_lines[i][-1:]

        last_ab_rhythm = get_rhythm(last_ab)
        current_ab_rhythm = get_rhythm(current_ab)

        last_rhythm_index = rhythm_dict[last_ab_rhythm[-1]]
        current_rhythm_index = rhythm_dict[current_ab_rhythm[-1]]

        if last_rhythm_index == current_rhythm_index:
            if not result[last_rhythm_index]:
                result[last_rhythm_index].append(lyric_lines[i - 1][-2:])
            result[last_rhythm_index].append(lyric_lines[i][-2:])
            # print 'match last'
            # print last_rhythm_index, current_rhythm_index
            # print last_ab_rhythm, current_ab_rhythm
            # print lyric_lines[i - 1][-1:], lyric_lines[i][-1:]

        elif last_last_ab is not None:
            last_last_ab_rhythm = get_rhythm(last_last_ab)
            last_last_rhythm_index = rhythm_dict[last_last_ab_rhythm[-1]]
            if last_last_rhythm_index == current_rhythm_index:
                if not result[last_last_rhythm_index]:
                    result[last_last_rhythm_index].append(lyric_lines[i - 2][-2:])
                result[last_last_rhythm_index].append(lyric_lines[i][-2:])
                # print 'match last last'
                # print last_last_rhythm_index, current_rhythm_index
                # print last_last_ab_rhythm, current_ab_rhythm
                # print lyric_lines[i - 2][-1:], lyric_lines[i][-1:]
    return result


def analyze_rhythm_twice_result(lyric_lines=[]):

    lyric_ab_lines = [''] * len(lyric_lines)

    ab = alphabet.alphabet()
    for i in range(len(lyric_lines)):
        line_ab = ab.chinese2ab(lyric_lines[i])
        lyric_ab_lines[i] = line_ab
        # print lyric_lines[i]
        # print line_ab
    result = {}

    for i in range(1, len(lyric_ab_lines)):
        last_last_abs = lyric_ab_lines[i - 2][-2:] if i > 1 and len(lyric_ab_lines[i-2]) > 1 else None
        last_abs = lyric_ab_lines[i - 1][-2:]
        current_abs = lyric_ab_lines[i][-2:]

        if len(current_abs) > 1 and len(last_abs) > 1 and current_abs != last_abs:
            last_ab_rhythm = get_rhythm(last_abs)
            current_ab_rhythm = get_rhythm(current_abs)

            last_rhythm_index_1 = rhythm_dict[last_ab_rhythm[-1]]
            last_rhythm_index_2 = rhythm_dict[last_ab_rhythm[-2]]

            current_rhythm_index_1 = rhythm_dict[current_ab_rhythm[-1]]
            current_rhythm_index_2 = rhythm_dict[current_ab_rhythm[-2]]

            key = (current_rhythm_index_2, current_rhythm_index_1)
            if last_rhythm_index_1 == current_rhythm_index_1 and last_rhythm_index_2 == current_rhythm_index_2:
                if key not in result.keys():
                    result[key] = [lyric_lines[i - 1][-2:], ]
                result[key].append(lyric_lines[i][-2:])
                # print 'match last'
                # print last_rhythm_index_1, current_rhythm_index_1
                # print last_ab_rhythm, current_ab_rhythm
                # print lyric_lines[i - 1][-1:], lyric_lines[i][-1:]
        elif len(current_abs) > 1 and last_last_abs is not None and len(last_last_abs) > 1 and last_last_abs != current_abs:
            current_ab_rhythm = get_rhythm(current_abs)
            current_rhythm_index_1 = rhythm_dict[current_ab_rhythm[-1]]
            current_rhythm_index_2 = rhythm_dict[current_ab_rhythm[-2]]

            last_last_ab_rhythm = get_rhythm(last_last_abs)
            last_last_rhythm_index_1 = rhythm_dict[last_last_ab_rhythm[-1]]
            last_last_rhythm_index_2 = rhythm_dict[last_last_ab_rhythm[-2]]

            if last_last_rhythm_index_1 == current_rhythm_index_1 and last_last_rhythm_index_2 == current_rhythm_index_2:
                if key not in result.keys():
                    result[key] = [lyric_lines[i - 1][-2:], ]
                result[key].append(lyric_lines[i][-2:])
                # print 'match last last'
                # print last_last_rhythm_index, current_rhythm_index_1
                # print last_last_ab_rhythm, current_ab_rhythm
                # print lyric_lines[i - 2][-1:], lyric_lines[i][-1:]
    return result

print unichr(0x7256), unichr(0x5463)
db = LyricCache()
rows = db.query_all_lines()
all_results = {}

n = 0
for row in rows:
    n += 1
    song_id = row[0]
    song_name = row[1]
    singer_name = row[2]
    line_txt = row[3]
    print '--------------------', song_id, song_name, singer_name, '--------------------', n
    lines = line_txt.split('\n')
    print '|'.join(lines)
    results = analyze_rhythm_twice_result(lines)
    for key in results.keys():
        print key, '|'.join(results[key])
        if key not in  all_results.keys():
            all_results[key] = results[key]
        else:
            all_results[key].extend(results[key])

sorted_lst = sorted(all_results.items(), key=lambda a:len(a[1]), reverse=True)

for l in sorted_lst:
    print l[0], '|'.join(l[1])


# all_results = [[] for rs in range(RHYTHM_NUM)]
#
# print len(all_rhyme_dict)
#
# for key in all_rhyme_dict.keys():
#     for i in range(len(all_rhyme_dict[key])):
#         all_results[i].extend(all_rhyme_dict[key][i])
#
# for result in all_results:
#     print len(result), '|'.join(result)
#     count_dict = {}
#     for word in result:
#         if word not in count_dict.keys():
#             count_dict[word] = 1
#         else:
#             count_dict[word] += 1
#     count_dict = sorted(count_dict.items(), key=lambda a:a[1], reverse=True)
#     i = 0
#     for count in count_dict:
#         i += 1
#         if i < len(count_dict):
#             print count[0], count[1],
#         if i == 100:
#             break
#     print
#     print

