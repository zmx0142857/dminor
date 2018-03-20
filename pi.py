#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pi to your desired digit"""

__author__ = 'Clarence Zhuo'

import math, rational

def pi(n):
    ret = 0
    for i in range(int(n / math.log10(2.25))):
        ret += rational.Rat(rational.choose(2*i, i)*3, (16**i * (2*i+1)))
    return ret.to_float(n)

print(pi(100))
