#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
from time import sleep


def run(name, sec):
    sleep(sec)
    print name, ' run'

threads = []
for i in range(10):
    t = threading.Thread(target=run, args=("t"+str(i), 2))
    t.start()
    # t.join()

# for t in threads:
#     print 'join'
#     t.join()



