#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import threading


class OneSingerCache:
    lock = threading.Lock()

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

    def reconnect(self):
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb',
                                      charset='utf8')

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

        self.lock.acquire()
        c = self.__conn.cursor()
        sql = "INSERT IGNORE INTO " + self.__table_name + " (song_id, song_name, singer_id, singer_name, album_id, album_name, lyric) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            c.executemany(sql, lyric_list)
            self.__conn.commit()
        except MySQLdb.OperationalError as e:
            print e
            print e
            print e
            print e
            print e
            self.reconnect()
            c = self.__conn.cursor()
            c.executemany(sql, lyric_list)
            self.__conn.commit()
            print "reconnect and save OK"
        finally:
            self.lock.release()

    def query_album(self, album_id):
        c = self.__conn.cursor()
        sql = "SELECT singer_id from " + self.__table_name + " where album_id = " + album_id + " limit 1"
        c.execute(sql)
        self.__conn.commit()
        print c.fetchone()
        return c.fetchone()

    def clear(self):
        c = self.__conn.cursor()
        c.execute('TRUNCATE TABLE ' + self.__table_name)
        self.__conn.commit()
