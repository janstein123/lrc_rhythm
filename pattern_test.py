#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

key = r'''[00:00.00] 作曲 : 刘珂矣/百慕三石
[00:01.00] 作词 : 刘珂矣/百慕三石
[00:25.970]墨已入水     渡一池青花
[00:31.740]揽五分红霞   采竹回家
[00:38.020]悠悠风来     埋一地桑麻
[00:44.290]一身袈裟     把相思放下'''
p1 = r"\[.+?\]"  # 这是我们写的正则表达式规则，你现在可以不理解啥意思
pattern1 = re.compile(p1)  # 我们在编译这段正则表达式
print pattern1.findall(key)


tup1 = re.subn(pattern1, "", key)

print len(tup1)
for str in tup1:
    print str

print key

