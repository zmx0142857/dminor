#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provides operations on quadratic numbers like p + q√n."""

__author__ = 'Clarence Zhuo'

import rational

class Quad(object):
    """
    Doctest:
    >>> sqrt(5)
    √5
    >>> Quad(rational.Rat('1/2'), rational.Rat('-1/5'), 108)
    3 - 6/5√3
    >>> Quad(1, 1, 1)
    2
    """
    def __init__(self, *args):
        """
        Quad(Quad)
        Quad(p, q, positive-int n) -> p + q√n
            p and q must be able to convert to Rat
        """
        argc = len(args)
        if argc == 1:
            if not isinstance(args[0], Quad):
                raise TypeError('when there is only one argument, it '
                                'must be a Quad.')
            self.p = args[0].p
            self.q = args[0].q
            self.n = args[0].n

        elif argc == 3:
            if not isinstance(args[2], int) or args[2] <= 0:
                raise TypeError('argument 3 must be a positive int.')
            try:
                self.p = rational.Rat(args[0])
                self.q = rational.Rat(args[1])
            except Exception:
                raise TypeError('argument 1 and 2 must be able to convert '
                                'to Rat.')
            self.n = args[2]
            self.simplify()
        else:
            raise TypeError('Quad() takes 1 or 3 arguments, %d given.' % argc)

    def __str__(self):
        part1 = str(self.p) if self.p != 0 else ''
        if self.q == 0:
            part2 = ''
            part3 = ''
        else:
            if self.q > 0:
                part2 = ' + ' if self.p != 0 else ''
            else: # self.q < 0:
                part2 = ' - '
            absq = abs(self.q)
            if absq != 1:
                part2 += str(absq)
            part3 = '√' + str(self.n)
        return part1 + part2 + part3

    __repr__ = __str__

    def __pos__(self):
        return self

    def __neg__(self):
        return Quad(-self.p, -self.q, self.n)

    def __abs__(self):
        if self < 0:
            return -self
        else:
            return self

    def __float__(self):
        return float(self.p) + float(self.q) * math.sqrt(self.n) 

    def __int__(self):
        return int(float(self))

    def __eq__(self, other):
        # this requires Quad being simplified in __init__
        return self.p == other.p and self.q == other.q\
                and self.n == other.n

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __le__(self, other):
        pass

    def __ge__(self, other):
        pass

    def __add__(self, other):
        if not isinstance(other, Quad):
            return Quad(self.p + other, self.q, self.n)
        _checkn(self, other)
        return Quad(self.p + other.p, self.q + other.q, self.n)

    def __radd__(self, other):
        return other + self

    def __sub__(self, other):
        if not isinstance(other, Quad):
            return Quad(self.p - other, self.q, self.n)
        _checkn(self, other)
        return Quad(self.p - other.p, self.q - other.q, self.n)

    def __rsub__(self, other):
        return other - self

    def __mul__(self, other):
        if not isinstance(other, Quad):
            return Quad(self.p * other, self.q * other, self.n)
        _checkn(self, other)
        return Quad(self.p * other.p + self.q * other.q * self.n,\
                other.p * self.q + other.q * self.p, self.n)

    def __rmul__(self, other):
        return other * self

    def __truediv__(self, other):
        if not isinstance(other, Quad):
            return Quad(self.p / other, self.q / other, self.n)
        _checkn(self, other)
        den = other.p**2 - other.q**2 * self.n
        return Quad((self.p * other.p - self.q * other.q * self.n)/den,\
                (other.p * self.q - other.q * self.p)/den, self.n)

    def __rtruediv__(self, other):
        return other / self

    def __pow__(self, other):
        if not isinstance(other, int) or other < 0:
            raise TypeError('the exponent must be a non-negative int')
        # other.......................................
        #.........................
        #..........................

    def simplify(self):
        # generator for prime numbers <= self.n
        p = prime(self.n)
        i = next(p)
        sqi = i*i
        while sqi <= self.n:
            if self.n % sqi == 0:
                self.p *= i
                self.q *= i
                self.n //= sqi
            else:
                i = next(p)
                sqi = i*i
        # rational actually
        if self.n == 1:
            self.p += self.q
            self.q = 0

    def conj(self):
        return Quad(self.p, -self.q, self.n)

def sqrt(n):
    return Quad(0, 1, n)

def prime(upper_bound=float('inf'), count=None):
    """
    yields prime numbers <= upper_bound,
    or first <count> prime numbers.
    """

    def odd_iter():
       n = 3
       while True:
           yield n
           n += 2

    def not_divisible(p):
        return lambda x: x % p != 0

    yield 2
    it = odd_iter()
    i = 1
    # this is always true if count == None
    while i != count:
        p = next(it)
        # this is always false if upper_bound == inf
        if p > upper_bound:
            break
        yield p
        i += 1
        if i == count or p == upper_bound:
            break
        it = filter(not_divisible(p), it)

def _checkn(self, other):
    if self.n != other.n:
        raise TypeError('two arguments must have the same n.')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
