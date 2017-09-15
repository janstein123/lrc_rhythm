#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
from time import sleep


def run(name):
    sleep(3)
    print name, ' run'

threads = []
for i in range(10):
    t = threading.Thread(target=run, kwargs={'name':"t"+str(i)})
    t.setDaemon(True)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
