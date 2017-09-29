#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb


class OneSingerCache:
    def __init__(self, table_name):
        self.__table_name = table_name
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb',
                                      charset='utf8')
        c = self.__conn.cursor()

        # c.execute('DROP TABLE IF EXISTS lyrics')
        c.execute('CREATE TABLE IF NOT EXISTS ' + self.__table_name +
                  '('
                  'song_id INT PRIMARY KEY, '
                  'song_name VARCHAR(128), '
                  'singer_id INT, '
                  'singer_name VARCHAR(128), '
                  'album_id INT, '
                  'album_name VARCHAR(128), '
                  'lyric TEXT NOT NULL, '
                  'lrc_lines TEXT );')
        c.close()

    def insert(self, song_id, lyric, song_name=None, singer_id=0, singer_name=None, lyricist=None):
        lyric = lyric.replace(u"'", u"''")
        sql = "REPLACE INTO " + self.__table_name + " VALUES (%d, '%s', %d, '%s', '%s', '%s')" % (
            song_id, song_name, singer_id, singer_name, lyricist, lyric)
        c = self.__conn.cursor()
        try:
            c.execute(sql)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print e

    def insert_many(self, lyric_list):
        c = self.__conn.cursor()
        sql = "INSERT IGNORE INTO " + self.__table_name + " (song_id, song_name, singer_id, singer_name, album_id, album_name, lyric) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            c.executemany(sql, lyric_list)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print e

    def clear(self):
        c = self.__conn.cursor()
        c.execute('TRUNCATE TABLE ' + self.__table_name)
        self.__conn.commit()
