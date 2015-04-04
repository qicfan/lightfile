# coding=utf-8

__author__ = 'Dean'

import hashlib, random


class shortName(object):
    """
    生成短名称，适用于URL和文件名的缩短
    """
    charMap = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRr-SsTtUuVvWwXxYyZz_0123456789'
    prefixToken = 'wowotuan'

    @classmethod
    def getShortName(self, name):
        m = hashlib.md5('%s%s' % (self.prefixToken, name)).hexdigest()
        s = []
        for i in xrange(4):
            l = m[i*8:(i+1)*8]
            idx = int(l, 16) & int('3FFFFFFF', 16)
            o = []
            for k in xrange(6):
                index = int('0000003D', 16) & idx
                o.append(self.charMap[index])
                idx = idx >> 5
            s.append(''.join(o))
        return s[random.randint(0, 3)]