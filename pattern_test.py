#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

import threading
from time import sleep


# def run(name):
#     sleep(3)
#     print name, ' run'
#
# threads = []
# for i in range(10):
#     t = threading.Thread(target=run, kwargs={'name':"t"+str(i)})
#     t.setDaemon(True)
#     t.start()
#     threads.append(t)
#
# for t in threads:
#     t.join()

def get_top_100_female_singers():
    # response = requests.get('http://music.baidu.com/artist/cn/male')
    response = requests.get('https://music.163.com/discover/artist/cat?id=1002')
    soup = BeautifulSoup(response.text, 'lxml')
    # < ul class ="m-cvrlst m-cvrlst-5 f-cb" id="m-artist-box" >
    singers = soup.find('ul', attrs={'class':'m-cvrlst m-cvrlst-5 f-cb'}).find_all('a', attrs={'class':'nm nm-icn f-thide s-fc0'})
    print len(singers)
    for singer in singers:
        print singer
    # print response.content

def get_top_100_male_singers():
    # response = requests.get('http://music.baidu.com/artist/cn/male')
    response = requests.get('https://music.163.com/discover/artist/cat?id=1001')
    soup = BeautifulSoup(response.text, 'lxml')
    # < ul class ="m-cvrlst m-cvrlst-5 f-cb" id="m-artist-box" >
    singers = soup.find('ul', attrs={'class':'m-cvrlst m-cvrlst-5 f-cb'}).find_all('a', attrs={'class':'nm nm-icn f-thide s-fc0'})
    print len(singers)
    for singer in singers:
        print singer

def get_top_100_band():
    # response = requests.get('http://music.baidu.com/artist/cn/male')
    response = requests.get('https://music.163.com/discover/artist/cat?id=1003')
    soup = BeautifulSoup(response.text, 'lxml')
    # < ul class ="m-cvrlst m-cvrlst-5 f-cb" id="m-artist-box" >
    singers = soup.find('ul', attrs={'class':'m-cvrlst m-cvrlst-5 f-cb'}).find_all('a', attrs={'class':'nm nm-icn f-thide s-fc0'})
    print len(singers)
    for singer in singers:
        print singer

get_top_100_male_singers()
get_top_100_female_singers()
get_top_100_band()

