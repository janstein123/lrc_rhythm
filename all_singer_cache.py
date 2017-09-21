#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb


class AllSingerCache:
    __table_name = 'all_singers'

    def __init__(self):
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb',
                                      charset='utf8')
        self.create_table()

    def create_table(self):
        c = self.__conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS ' + self.__table_name +
                  '('
                  'singer_id INT PRIMARY KEY, '
                  'singer_name VARCHAR(128) NOT NULL, '
                  'singer_type INT NOT NULL, '
                  'singer_order TINYINT)')

    def insert(self, singer_id, singer_name, singer_type, order):
        c = self.__conn.cursor()
        try:
            c.execute("REPLACE INTO %s VALUES (%d, '%s', %d, %d)" % (self.__table_name, singer_id, singer_name, singer_type, order))
            self.__conn.commit()
        except MySQLdb.Error as e:
            print e

    def update_singers(self, singer_list):
        c = self.__conn.cursor()
        try:
            c.execute('DROP TABLE IF EXISTS ' + self.__table_name)
            self.create_table()
            self.insert_many(singer_list)
        except MySQLdb.Error as e:
            print e

    def insert_many(self, singer_list):
        c = self.__conn.cursor()
        try:
            sql = "INSERT INTO " + self.__table_name + " VALUES(%s, %s, %s, %s)"
            c.executemany(sql, singer_list)
            self.__conn.commit()
        except MySQLdb.Error as e:
            print 'insert_many error:', e

    def query_all(self):
        c = self.__conn.cursor()
        c.execute("SELECT * FROM " + self.__table_name)
        self.__conn.commit()
        return c.fetchall()
