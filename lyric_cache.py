#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb


class LyricCache:
    __conn = None

    def __init__(self):
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb', charset='utf8')
        c = self.__conn.cursor()

        # c.execute('DROP TABLE IF EXISTS lyrics')
        c.execute('CREATE TABLE IF NOT EXISTS lyrics ('
                  'song_id INT PRIMARY KEY, '
                  'song_name VARCHAR(128), '
                  'singer_id INT, '
                  'singer_name VARCHAR(32), '
                  'lyricist VARCHAR(32), '
                  'lyric TEXT NOT NULL);')
        c.close()

    def insert(self, song_id, lyric, song_name=None, singer_id=0, singer_name=None, lyricist=None):
        sql = "INSERT INTO lyrics VALUES (%d, '%s', %d, '%s', '%s', '%s')" % (song_id, song_name, singer_id, singer_name, lyricist, lyric)
        c = self.__conn.cursor()
        c.execute(sql)
        self.__conn.commit()
        c.close()


# cache = LyricCache()
# cache.insert(1235, '告白气球', 2123, '周杰伦', '方文山', '你说你有点难追 想让我知难而退 礼物不需挑最贵 只要想写的落叶')
