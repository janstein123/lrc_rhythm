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
