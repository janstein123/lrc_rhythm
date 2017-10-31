#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import threading


class LyricCache:
    __table_name = 'all_lyrics'
    __lock = threading.Lock()

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
            print 'insert:' + str(e)

    def insert_many(self, lyric_list):
        c = self.__conn.cursor()
        sql = "REPLACE INTO " + self.__table_name + " VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            c.executemany(sql, lyric_list)
            self.__conn.commit()
            print len(lyric_list), 'songs inserted.'
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

    # for merging songs
    def query_songs(self, table_name):
        c = self.__conn.cursor()
        try:
            c.execute('SELECT song_id, song_name, singer_id, singer_name, lyric, lrc_lines from ' + table_name)
            self.__conn.commit()
            return c.fetchall()
        except MySQLdb.Error as e:
            print 'query_songs:' + str(e)
            return None

    # for merging songs
    def insert_many_songs(self, lyric_list, table_name):
        c = self.__conn.cursor()
        sql = "REPLACE INTO " + table_name + " (song_id, song_name, singer_id, singer_name, lyric, lrc_lines) VALUES (%s, %s, %s, %s, %s, %s)"
        print sql
        try:
            rows = c.executemany(sql, lyric_list)
            self.__conn.commit()
            print rows, 'songs inserted.'
        except MySQLdb.Error as e:
            print 'insert_many_songs:' + str(e)

    def query_name(self):
        c = self.__conn.cursor()
        try:
            c.execute('SELECT song_id, song_name, singer_id, singer_name from ' + self.__table_name)
            self.__conn.commit()
            return c.fetchall()
        except MySQLdb.Error as e:
            print 'query_name:' + str(e)
            return None

    def query_all_lrc(self):
        c = self.__conn.cursor()
        try:
            sql = 'SELECT song_id, song_name, singer_name, lyric from ' + self.__table_name
            # sql = 'SELECT song_id, song_name, singer_name, lyric FROM ' + self.__table_name + ' WHERE song_id in (357336)'
            c.execute(sql)
            self.__conn.commit()
            return c.fetchall()
        except MySQLdb.Error as e:
            print 'query_name:' + str(e)
            return None

    def query_all_lines(self):
        c = self.__conn.cursor()
        try:
            c.execute('SELECT song_id, song_name, singer_name, lrc_lines from ' + self.__table_name)
            # sql = 'SELECT song_id, song_name, singer_name, lrc_lines FROM ' + self.__table_name + ' WHERE song_id = 248097'
            # print sql
            # c.execute(sql)
            self.__conn.commit()
            return c.fetchall()
        except MySQLdb.Error as e:
            print 'query_name:' + str(e)
            return None

    def delete_songs(self, ids):
        c = self.__conn.cursor()
        sql = "DELETE FROM " + self.__table_name + " WHERE song_id = %s"
        try:
            rows = c.executemany(sql, ids)
            self.__conn.commit()
            print rows, 'songs deleted'
        except MySQLdb.Error as e:
            print 'delete_songs:' + str(e)

    def delete_song_by_id(self, id):
        c = self.__conn.cursor()
        sql = "DELETE FROM " + self.__table_name + " WHERE song_id = " + str(id)
        try:
            rows = c.execute(sql)
            self.__conn.commit()
            print rows, 'song deleted'
        except MySQLdb.Error as e:
            print 'delete_songs:' + str(e)

    def update_lines(self, lines=[]):
        if not lines:
            print 'list is empty'
            return
        self.__lock.acquire()
        c = self.__conn.cursor()
        sql = "UPDATE " + self.__table_name + " SET lrc_lines = %s WHERE song_id = %s"
        # print sql
        try:
            rows = c.executemany(sql, lines)
            self.__conn.commit()
            print rows, "rows updated"
        except MySQLdb.Error as e:
            print 'update_lines:', type(e), e
        finally:
            self.__lock.release()

    def update_name(self, new_names=[]):
        if not new_names:
            print 'list is empty'
            return
        self.__lock.acquire()
        c = self.__conn.cursor()
        sql = "UPDATE " + self.__table_name + " SET song_name = %s WHERE song_id = %s"
        # print sql
        try:
            rows = c.executemany(sql, new_names)
            self.__conn.commit()
            print rows, "rows updated"
        except MySQLdb.Error as e:
            print 'update_lines:', type(e), e
        finally:
            self.__lock.release()
