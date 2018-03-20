#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""longer float as long as you like"""

__author__ = 'Clarence Zhuo'

import math

def quantity_level(n):
    if n == 0:
        return 0
    return math.floor(math.log10(abs(n))) + 1

class Lfloat(object):
    """
    Doctest:
    >>> Lfloat(0)
    0.0e0
    >>> Lfloat(-42)
    -0.42e2
    >>> Lfloat(259, -4)
    0.259e-1
    >>> Lfloat(0.0)
    0.0e0
    >>> Lfloat(31.364)
    0.31364e2
    >>> Lfloat(0.31364, 2)
    0.3136399999999e2
    >>> Lfloat(25) * Lfloat(0.4)
    0.1e2
    >>> Lfloat(25) * Lfloat(0.1)
    0.25e1
    """
    def __init__(self, value, exp=0, length=15):
        self.strip = True
        if isinstance(value, int):
            self.digits = value
            self.exp = exp
            self.length = quantity_level(value)
        elif isinstance(value, float):
            self.length = length
            self.exp = exp + quantity_level(value) - length
            self.digits = int(value * (10**(-self.exp)))

    def __str__(self):
        sign = '-' if self.digits < 0 else ''
        d = str(abs(self.digits))
        if self.strip:
            d = d.rstrip('0')
        if d == '':
            d = '0'
        return sign + '0.' + d + 'e' + str(self.length + self.exp)
    __repr__ = __str__

    def __mul__(self, other):
        return Lfloat(self.digits * other.digits, self.exp + other.exp)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
