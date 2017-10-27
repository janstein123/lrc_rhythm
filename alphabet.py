#!/usr/bin/python
# -*- coding: utf-8 -*-


class AlphaBet(object):
    __singleton = None

    def __init__(self):
        self.ab_dict = {}
        ab_file = open('word.data', 'r')
        for line in ab_file.readlines():
            kv = line.split('   ')
            self.ab_dict[kv[0]] = kv[1]
        ab_file.close()

    @staticmethod
    def get_instance():
        if AlphaBet.__singleton is None:
            AlphaBet.__singleton = AlphaBet()
        return AlphaBet.__singleton

    def chinese2ab(self, chinesestr):
        # print (chinesestr)
        ab_list = []
        if not isinstance(chinesestr, unicode):
            chinesestr = chinesestr.decode('utf-8')
        for char in chinesestr:
            # print ord(char)
            xkey = '%X' % ord(char)
            # print xkey
            if self.ab_dict.has_key(xkey):
                ab_list.append(self.ab_dict[xkey].split()[0][:-1].lower())
            else:
                ab_list.append(char)
        return ab_list
