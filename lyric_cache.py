#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb


class LyricCache:
    __table_name = 'new_new_lyrics'

    def __init__(self):
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb',
                                      charset='utf8')
        c = self.__conn.cursor()

        # c.execute('DROP TABLE IF EXISTS lyrics')
        c.execute('CREATE TABLE IF NOT EXISTS ' + self.__table_name +
                  ' ('
                  'song_id INT PRIMARY KEY, '
                  'song_name VARCHAR(128), '
                  'singer_id INT, '
                  'singer_name VARCHAR(128), '
                  'lyricist VARCHAR(128), '
                  'lyric TEXT NOT NULL);')
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
            print 'insert:' + str(e)

    def insert_many(self, lyric_list):
        c = self.__conn.cursor()
        sql = "REPLACE INTO " + self.__table_name + " VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            c.executemany(sql, lyric_list)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print 'insert_many:' + str(e)

    def clear(self):
        c = self.__conn.cursor()
        try:
            c.execute('TRUNCATE TABLE ' + self.__table_name)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print 'clear:' + str(e)
            return None

    def query_name(self):
        c = self.__conn.cursor()
        try:
            c.execute('SELECT song_id, song_name, singer_id, singer_name from ' + self.__table_name)
            self.__conn.commit()
            return c.fetchall()
        except MySQLdb.Error as e:
            print 'query_name:' + str(e)
            return None

    def delete_songs(self, ids):
        c = self.__conn.cursor()
        # s = '('
        # for i in range(len(ids)):
        #     s = s + str(ids[i])
        #     if i == len(ids) - 1:
        #         s = s + ')'
        #     else:
        #         s = s + ','
        # print s
        sql = "DELETE FROM " + self.__table_name + " WHERE song_id = %s"
        try:
            c.executemany(sql, ids)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print 'delete_songs:' + str(e)
