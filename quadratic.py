"""Provides quadratic number (e.g., p + q √n) calculation.

"""

__author__ = '卓铭鑫'

import Rational

class Quad(object):

    def __init__(self, p, q, n):
        self._p = p
        self._q = q
        self._n = n

    def __len__(self):
        return len(str(self._p)) + len(str(self._q)) + len(str(self._n)) + 5

    def __str__(self):
        width = len(str(self._n))
        lower = '%d + %d√%s' % (self._p, self._q, self._n)
        upper = ''.center(width, '_').rjust(len(self))
        return upper + '\n' + lower

    __repr__ = __str__