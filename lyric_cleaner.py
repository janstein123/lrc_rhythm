#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
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

n, m, j = 0, 0, 0

AUTHOR_NAMES_1 = (u'词', u'曲', u'编', u'鼓', u'白', u'监', u'詞', u'混', u'箫', u'編')

AUTHOR_NAMES_2 = (
    u'作词', u'作曲', u'编曲', u'词曲', u'演唱', u'合声', u'伴唱', u'混音', u'母带', u'制作', u'童音', u'微博', u'编排', u'手绘', u'填词', u'原曲',
    u'哼唱',
    u'原唱',
    u'翻唱', u'副歌', u'念白', u'视频', u'独白', u'混缩', u'缩混' u'发行', u'配音', u'后期', u'作者', u'监制', u'配器', u'歌手', u'设备', u'策划',
    u'文案',
    u'出品', u'美工', u'鸣谢', u'笛箫', u'古筝', u'弦乐', u'二胡', u'琵琶', u'柳琴', u'长笛', u'笛子', u'录音', u'曲目', u'吉他', u'和声', u'钢琴',
    u'海报', u'键盘', u'首席', u'编舞', u'和音', u'舞蹈')

AUTHOR_NAMES_3 = (
    u'小提琴', u'中提琴', u'大提琴', u'录音棚', u'录音室', u'混音室', u'录音师', u'混音师', u'弦乐团', u'制作人', u'出品人', u'出品方', u'电吉他', u'演唱者',
    u'专辑名', u'编曲唱', u'架子鼓', u'打击乐',
    u'曲编唱', u'词曲唱')

AUTHOR_NAMES_4 = (u'封面设计', u'词曲编唱', u'游戏原著', u'伴奏混音', u'舞蹈总监')


def remove_time(lrc):
    p = re.compile(u"\[.+\]")
    lrc = re.sub(p, "", lrc)
    return lrc


def has_no_chinese(str):
    # 如果行中没有任何中文字符
    pattern = re.compile(u'[\u3400-\u4db5\u4E00-\u9FCB]')
    return re.search(pattern, str) is None


def has_special_char(str):
    pattern = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z0-9\s　\u00a0\u2028\ue3ac,，。]')
    return re.search(pattern, str) is not None


def remove_non_lrc_line(sid, name, sname, lrc):
    global m, n

    pattern = re.compile(u'\n')
    lines = re.split(pattern, lrc)
    # if len(lines) < 4:
    #     return None

    new_lines = []
    # remove empty lines
    for line in lines:
        if len(line.strip()) > 0:
            new_lines.append(line)
    head_to_del = []
    tail_to_del = []

    def is_lrc_line(line_with_colon):
        if u':' not in line and u'：' not in line:
            return True

        p = re.compile(u'[:：]')
        lst = re.split(p, line_with_colon, 1)
        l1 = re.sub(re.compile(u'[ 　\u00a0\u2028\ue3ac]'), '', lst[0].strip())
        l2 = lst[1].strip()
        # 冒号前面是单字，并且不是以下表示作者信息的字，说明已经到了歌词正文
        # 冒号后面如果是全中文字符，且长度大于等于7，也认为是到了歌词正文了
        if (len(l1) == 1 and l1 in AUTHOR_NAMES_1) \
                or (len(l1) == 2 and l1 in AUTHOR_NAMES_2) \
                or len(l1) == 3 and l1 in AUTHOR_NAMES_3 \
                or len(l1) > 3 \
                or has_special_char(l1) \
                or has_special_char(l2) \
                or has_no_chinese(l2) \
                or len(l2) < 7:
            return False
        return True

    # 寻找头部非歌词正文行
    for i in range(len(new_lines)):
        line = new_lines[i].strip()
        if has_no_chinese(line):
            head_to_del.append(i)
        elif u':' in line or u'：' in line:
            if is_lrc_line(line):
                break
            else:
                head_to_del.append(i)
        # 如果头部行中有特殊字符，认为是非歌词行，加入删除队列
        elif re.search(re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z\s　\u00a0\u2028\ue3ac,，。.?？（()）！!]'), line):
            head_to_del.append(i)
        else:
            name = name.strip()

            def is_song_title_line():
                # 如果行和歌名完全相同，认为是歌名行
                # 如果行中包含歌名，并且同时包含非中文非空格非逗号的字符，也认为是歌名行
                # 行中包含歌名，但是行内只有中文空格逗号字符，说明可能是歌词正文
                # 如果行中包含歌名，同时也包含歌手名，那一定是歌名行
                if name == line:
                    return True
                elif name in line:
                    if sname in line:
                        return True
                    else:
                        p = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCB\s　\u00a0\u2028\ue3ac,，。]')
                        return re.search(p, line) is not None
                return False

            if is_song_title_line():
                head_to_del.append(i)
            else:
                break

    # 反向遍历寻找尾部非歌词正文行
    for i in range(len(new_lines) - 1, 0, -1):
        line = new_lines[i].strip()
        if has_no_chinese(line):
            tail_to_del.append(i)
        elif u':' in line or u'：' in line:
            if is_lrc_line(line):
                break
            else:
                tail_to_del.append(i)
        # 如果头部行中有特殊字符，认为是非歌词行，加入删除队列
        elif re.search(re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z\s　\u00a0\u2028\ue3ac,，。.?？（()）！!]'), line):
            tail_to_del.append(i)
        # 认为它是到了歌词正文了
        else:
            break

    # 删除头尾非歌词行
    start = 0
    end = len(new_lines) - 1
    if len(head_to_del) > 0:
        start = head_to_del[len(head_to_del) - 1] + 1

    if len(tail_to_del) > 0:
        end = tail_to_del[len(tail_to_del) - 1] - 1

    # 小于行忽略的歌词
    if end - start + 1 < 1:
        # n = n + 1
        # print_title(sid, name)
        # print_lines(lines)
        # print '----------------------'
        # print_lines(new_lines[start:end + 1])
        return None
    else:
        return new_lines[start:end + 1]


def print_lines(lines=[]):
    for l in lines:
        print l


def print_title(sid, name):
    print '----------------------', sid, name, '----------------------'


def remove_text_before_colon(sid, name, sname, lines=[]):
    global n, m
    new_lines = []
    p = re.compile(u'.+[:：]')
    for line in lines:
        if u':' in line or u'：' in line:
            line = re.sub(p, '', line).strip()
            if line.strip():
                new_lines.append(line)
        else:
            new_lines.append(line)

    # if len(new_lines) < 4:
    #     return None
    return new_lines


def remove_aside(sid, name, lrc_lines=[]):
    # pattern = re.compile(u"(\(.+\))|(（.+）)")
    new_lines = []
    pattern = re.compile(u"[(（].+?[)）]")
    for line in lrc_lines:
        line = re.sub(pattern, '', line)
        if line.strip():
            new_lines.append(line)

    # if len(new_lines) < 4:
    #     # print_title(sid, name)
    #     # print_lines(new_lines)
    #     return None
    return new_lines


def remove_non_chinese_line(sid, name, lines=[]):
    global n
    showed = False
    # 注意同时包括全角和半角空格 non breaking space还有
    pattern = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z\s　\u00a0\u2028\ue3ac,，。?]')
    for line in lines:
        if re.search(pattern, line):
            if not showed:
                print '-----------------', sid, name, '-----------------'
                n += 1
                showed = True
            print line

    return lines


def replace_space_with_line_break(sid, name, lines=[]):
    if not lines:
        return None
    global m
    new_lines = []

    def has_special_char_1(line):
        p = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z0-9]')
        # print re.findall(p, line)
        return re.search(p, line) is not None

    for line in lines:
        pattern = re.compile(u'[\s　\u2028\u00a0\ue3ac?？,，。.~～!！、]+')
        split_list = re.split(pattern, line)
        for l in split_list:
            # print has_no_chinese(l), has_special_char_1(l)
            # 删除没有中文字符，或者带有特殊符号的行
            if l and not has_no_chinese(l) and not has_special_char_1(l):
                new_lines.append(l)
    if len(new_lines) < 4:
        return None

    return new_lines


def remove_nonsense_eng_word(lines=[]):
    pattern = re.compile(u'(yeah|wo+|wooh|oh|wu|o+)$', re.I)
    new_lines = []
    for line in lines:
        line = re.sub(pattern, '', line)
        if line:
            new_lines.append(line)
    return new_lines


def remove_line_end_with_english_and_repeated_line(sid, name, lines=[]):
    global n
    pattern = re.compile(u'.*[a-zA-Z]+$')
    new_lines = []
    for line in lines:
        if not re.search(pattern, line) and line not in new_lines:
            new_lines.append(line)

    if len(new_lines) < 4:
        return None

    return new_lines


def clean_lyric(sid, name, sname, raw_lrc):
    # print raw_lrc
    if raw_lrc:
        new_lrc = remove_time(raw_lrc)
        if new_lrc:
            lines = remove_non_lrc_line(sid, name, sname, new_lrc)
            if lines:
                lines = remove_text_before_colon(sid, name, sname, lines)
                if lines:
                    lines = remove_aside(sid, name, lines)
                    if lines:
                        lines = replace_space_with_line_break(sid, name, lines)
                        if lines:
                            lines = remove_nonsense_eng_word(lines)
                            lines = remove_line_end_with_english_and_repeated_line(sid, name, lines)
                            return lines

    return None


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
    # print len(names), type(names)
    to_del_ids = []
    for row in names:
        song_id = row[0]
        song_name = row[1]
        singer_name = row[3]
        # pattern = re.compile(u'cover|伴奏|remix|instrumental|kala|[(（【[].+版[]】）)]|demo|live|version|dj', re.I)
        p1 = re.compile(u'[^\u3400-\u4db5\u4E00-\u9FCBa-zA-Z0-9\u00a0\u2028\ue3ac 　\'.,，。！!？?:]')
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


def update_lines():
    db = LyricCache()
    rows = db.query_all_lrc()
    total_len = len(rows)
    print total_len, 'songs in db'
    if total_len < 1:
        return

    def process_clean(rows_div):
        part_len = len(rows_div)
        process = 0
        print threading.currentThread().getName(), "start", part_len, rows_div[0][0], rows_div[len(rows_div) - 1][0]
        lines_list = []
        for r in rows_div:
            sid = r[0]
            name = r[1]
            sname = r[2]
            lines = clean_lyric(sid, name, sname, r[3])
            if lines:
                lines_list.append(['\n'.join(lines), sid])
            process += 1
            print threading.currentThread().getName(), sid, name, sname, 'updated', str(process) + '/' + str(
                part_len), ('%.2f%%' % (process / float(part_len) * 100))

        db.update_lines(lines_list)
        print threading.currentThread().getName(), "process completely", len(
            lines_list), '-------------------------------------------------------------------------------------------------------'

    thread_num = 1
    div_len = total_len / thread_num
    for index in range(thread_num):
        start = index * div_len
        end = (index + 1) * div_len if index < thread_num - 1 else total_len
        t = threading.Thread(target=process_clean, args=(rows[start: end],))
        t.start()
        time.sleep(0.1)


# 发现有很多歌词的前面几行还是有包含作词作曲演唱这些信息存在，需要去除
def remove_author_again():
    db = LyricCache()
    rows = db.query_all_lines()
    total_len = len(rows)
    print total_len, 'songs in db'
    lines_list_to_update = []
    for row in rows:
        song_id = row[0]
        song_name = row[1]
        lrc_lines_txt = row[3]
        lines = lrc_lines_txt.split(u'\n')
        num_to_del = 0
        flag = False
        has_info = False
        for i in range(0, len(lines)):
            if flag:
                flag = False
                continue
            line = lines[i]

            if line in AUTHOR_NAMES_1 or line in AUTHOR_NAMES_2 or line in AUTHOR_NAMES_3 or line in AUTHOR_NAMES_4:
                has_info = True

                # 考虑两个作者名称连续的情况
                try:
                    next_line = lines[i + 1]
                    if next_line in AUTHOR_NAMES_1 or next_line in AUTHOR_NAMES_2 or next_line in AUTHOR_NAMES_3 or next_line in AUTHOR_NAMES_4:
                        num_to_del += 1
                        print line
                    else:
                        flag = True
                        num_to_del += 2
                        print line
                        print lines[i + 1]
                except IndexError:
                    num_to_del += 1
                    print line
            else:
                # 有些歌曲将作者名称和人名连在一起，忘记了加标点隔开
                flag = False
                p = re.compile(u'作曲|作词|演唱|词曲|编曲|混音|编辑|封面设计')
                if re.search(p, line):
                    print line
                    num_to_del += 1
                    has_info = True
                else:
                    break
        if has_info:
            print '----------------------------'
            print '\n'.join(lines[num_to_del:])
            print '------------------', song_id, num_to_del, len(lines), '------------------'
            lines_list_to_update.append(['\n'.join(lines[num_to_del:]), song_id])
    print len(lines_list_to_update)
    db.update_lines(lines_list_to_update)


def remove_repeated_songs():
    db = LyricCache()
    rows = db.query_all_lines()
    total_len = len(rows)
    print total_len, 'songs in db'

    line_dict = {}
    for row in rows:
        song_id = row[0]
        song_name = row[1]
        singer_name = row[2]
        lrc_lines = row[3]
        pre_2_lines = lrc_lines.split(u'\n')[0] + '|' + lrc_lines.split(u'\n')[1]
        if pre_2_lines not in line_dict.keys():
            line_dict[pre_2_lines] = song_id
        else:
            print song_name, singer_name, pre_2_lines
    print len(line_dict.keys())


remove_repeated_songs()
# remove_author_again()
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
# print hex(ord(u'の'))
# l = u'许　仙 　'
# for a in l:
#     print hex(ord(a))
# p = re.compile(u'.*?[:：]+?')
# print re.sub(p, '', u'fafaf:fadaf 作词：ewwoeir你的')
