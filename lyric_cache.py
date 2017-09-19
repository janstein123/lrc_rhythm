#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb


class LyricCache:
    __conn = None

    def __init__(self):
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb',
                                      charset='utf8')
        c = self.__conn.cursor()

        # c.execute('DROP TABLE IF EXISTS lyrics')
        c.execute('CREATE TABLE IF NOT EXISTS lyrics ('
                  'song_id INT PRIMARY KEY, '
                  'song_name VARCHAR(128), '
                  'singer_id INT, '
                  'singer_name VARCHAR(128), '
                  'lyricist VARCHAR(128), '
                  'lyric TEXT NOT NULL);')
        c.close()

    def insert(self, song_id, lyric, song_name=None, singer_id=0, singer_name=None, lyricist=None):
        lyric = lyric.replace(u"'", u"''")
        sql = "REPLACE INTO lyrics VALUES (%d, '%s', %d, '%s', '%s', '%s')" % (
        song_id, song_name, singer_id, singer_name, lyricist, lyric)
        c = self.__conn.cursor()
        try:
            c.execute(sql)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print e

    def insert_many(self, lyric_list):
        c = self.__conn.cursor()
        sql = "REPLACE INTO lyrics VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            c.executemany(sql, lyric_list)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print e

    def clear(self):
        c = self.__conn.cursor()
        c.execute('TRUNCATE TABLE lyrics')
        self.__conn.commit()

# cache = LyricCache()
# ll = [(1236, '告白气球', 2123, '周杰伦', '方文山', '你说你有点难追 想让我知难而退 礼物不需挑最贵 只要想写的落叶'),
#       (1233, '告气球白', 2124, '周解', '方山文', '最贵你说你 想让我有点难追要想写的落知难而不需挑退 礼物 只叶')]
#
# cache.clear()
# cache.insert_many(ll)