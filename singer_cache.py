#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb


class SingerCache:

    def __init__(self):
        self.__conn = MySQLdb.connect(host='localhost', user='username', passwd='password', db='musicdb', charset='utf8')
        self.create_table()

    def create_table(self):
        c = self.__conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS singers ('
                  'singer_id INT PRIMARY KEY, '
                  'singer_name VARCHAR(128) NOT NULL, '
                  'singer_type INT NOT NULL)')

    def insert(self, singer_id, singer_name, singer_type):
        c = self.__conn.cursor()
        c.execute("REPLACE INTO singers VALUES (%d, '%s', %d)" %(singer_id, singer_name, singer_type))
        self.__conn.commit()

    def update_singers(self, singer_list):
        c = self.__conn.cursor()
        c.execute('DROP TABLE IF EXISTS singers')
        self.create_table()
        self.insert_many(singer_list)

    def insert_many(self, singer_list):
        c = self.__conn.cursor()
        c.execute('TRUNCATE TABLE singers')
        sql = "INSERT INTO singers VALUES(%s, %s, %s)"
        c.executemany(sql, singer_list)
        self.__conn.commit()

    def query_all(self):
        c = self.__conn.cursor()
        c.execute("SELECT * FROM singers")
        self.__conn.commit()
        return c.fetchall()