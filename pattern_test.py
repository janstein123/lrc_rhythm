#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

txt = u'中国哦哦哦ohoh中'

p = re.compile(u"[\u4e00-\u9fa5]+$")

found_list = re.findall(p, txt)

print found_list