#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pi to your desired digit"""

__author__ = 'Clarence Zhuo'

import math, rational

def my_first_pi(n):
    """performs well for n <= 100. bigger n costs too much time."""
    ret = 0
    N = int(n / math.log10(2.25))
    for i in range(N):
        ret += rational.Rat(rational.choose(2*i, i)*3, (16**i * (2*i+1)))
    return ret.to_float(n)
