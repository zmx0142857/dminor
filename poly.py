#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Math tools including rationals, matrices and polynomials

>>> x
x
>>> Poly(3.14)
3.14
>>> p = Poly(Term(1,1)); p.cdr = Poly(Term(-2,42)); p
-2x^42 + x
>>> p.cdr.cdr = Poly(Term(7,100)); p
7x^100 - 2x^42 + x
>>> p(1)
6
>>> p(-1)
4
>>> +p
7x^100 - 2x^42 + x
>>> -p
-7x^100 + 2x^42 - x
>>> p = x**2 - 2*x + 3; q = 9*x**3 - x + 3; p+q
9x^3 + x^2 - 3x + 6
>>> p-q
-9x^3 + x^2 - x
>>> x + x
2x
>>> x - x
0
>>> x + 1 - x
1
>>> x*x*2
2x^2
>>> (x+1)*(x-1)
x^2 - 1
>>> (x-1)**3
x^3 - 3x^2 + 3x - 1
>>> Poly.desc = False; (x-1)**3; Poly.desc = True
-1 + 3x - 3x^2 + x^3
>>> divmod((x-1)**5, (x-2)**4)
(x + 3.0, 10.0x^3 - 50.0x^2 + 85.0x - 49.0)
"""

__author__ = 'Clarence Zhuo'

class Term(object):
    def __init__(self, coef, exp, sym='x'):
        self.coef = coef
        self.exp = exp
        self.sym = sym

    def toStr(self, first=False):
        if self.coef == 0:
            return '0' if first else ''
        # sign
        if self.coef < 0:
            sign = '-' if first else ' - '
        else:
            sign = '' if first else ' + '
        # coef
        abscoef = abs(self.coef)
        if abscoef == 1 and self.exp != 0:
            coef = ''
        else:
            coef = str(abscoef)
        # exp
        if self.exp == 0:
            exp = ''
        elif self.exp == 1:
            exp = self.sym
        else:
            exp = self.sym + '^' + str(self.exp)
        return sign + coef + exp

    def __str__(self):
        return '<Term %s>' % self.toStr(True)

    __repr__ = __str__

    def __call__(self, v):
        return self.coef * v**self.exp

    def __eq__(self, other):
        return self.exp == other.exp and self.coef == other.coef

    def copy(self):
        return Term(self.coef, self.exp, self.sym)

    def __neg__(self):
        return Term(-self.coef, self.exp, self.sym)

    def __mul__(self, other):
        if other is None:
            return Term(0, 0)
        elif isinstance(other, Poly):
            return other * self
        return Term(self.coef * other.coef, self.exp + other.exp, self.sym)

    def __truediv__(self, other):
        return Term(self.coef / other.coef, self.exp - other.exp, self.sym)

class Poly(object):
    def __init__(self, car=None, cdr=None, sym='x'):
        self.sym = sym
        if car is None:
            self.car = Term(0,0)
            self.cdr = None
        elif isinstance(car, Term):
            self.car = car
            self.cdr = cdr
        elif isinstance(car, Poly):
            self.car = car.car.copy()
            self.cdr = None if car.cdr is None else Poly(car.cdr)
        else:
            self.car = Term(car, 0)
            self.cdr = None
    
    desc = True
    def toStrArr(self, first):
        if self.cdr is None:
            return [self.car.toStr(first or self.desc)]
        return self.cdr.toStrArr(False) + [self.car.toStr(first)]
    
    def __str__(self):
        if self.desc:
            return ''.join(self.toStrArr(False))
        return ''.join(reversed(self.toStrArr(True)))
    
    __repr__ = __str__

    def __call__(self, v):
        # evaluate polynomial at given point
        if self.cdr is None:
            return self.car(v)
        return self.car(v) + self.cdr(v)
    
    def __getitem__(self, n):
        # return the coefficient of term x^n
        if self.car.exp == n:
            return self.car.coef
        return self.cdr[n]
    
    def __setitem__(self, n, coef):
        # set the coefficient of term x^n as coef
        if self.car.exp == n:
            self.car.coef = coef
        else:
            self.cdr[n] = coef

    def __eq__(self, other):
        return self.car == other.car and self.cdr == other.cdr
    
    def __ne__(self, other):
        return not self == other

    def __pos__(self):
        # return copy of self
        return Poly(self)
    
    def __neg__(self):
        if self.cdr is None:
            return Poly(-self.car)
        return Poly(-self.car, -self.cdr)
    
    def iszero(self):
        # returns True iff this is a zero polynomial
        return self.car.coef == 0

    def diff(self):
        # derivate of polynomial
        if self.cdr is None:
            return self.car.diff()
        car = self.car.diff
        if car.coef == 0:
            return self.cdr.diff()
        return Poly(car, self.cdr.diff())

    def __add__(self, other):
        return self.op(other, '+') or Poly(0)
    
    def __radd__(self, other):
        return self.op(other, '+') or Poly(0)
    
    def __sub__(self, other):
        return self.op(-other, '+') or Poly(0)
    
    def __rsub__(self, other):
        return (-self).op(other, '+') or Poly(0)
    
    def __mul__(self, other):
        return self.op(other, '*')
    
    def __rmul__(self, other):
        return self.op(other, '*')

    def __divmod__(self, other):
        return self.op(other, '/%')

    def __floordiv__(self, other):
        return self.op(other, '//')

    __truediv__ = __floordiv__ # 分式 ??

    def __mod__(self, other):
        return self.op(other, '%')

    def __pow__(self, exp):
        # fast power
        ret = Poly(1)
        mask = 1 << (exp.bit_length()-1)
        # iterate over each bit of exp
        while mask:
            ret *= ret
            if exp & mask:
                ret *= self
            mask >>= 1
        return ret

    def terms(self):
        # return list of terms
        ret = []
        p = self
        while p is not None:
            ret.append(p.car)
            p = p.cdr
        return ret

    def highest_term(self):
        # return term of the highest degree
        p = self
        while p.cdr is not None:
            p = p.cdr
        return p.car

    def deg(self):
        # return degree of polynomial. deg(zero polynomial) == -1.
        if self.iszero():
            return -1
        return self.highest_term().exp
    
    def op(lhs, rhs, method):
        # helper function for arithmetic (+ - * / %) methods
        if method == '*':
            if rhs is None:
                return Poly(0)
            if isinstance(rhs, Poly):
                return lhs * rhs.car + lhs * rhs.cdr
            if isinstance(rhs, Term):
                return Poly(rhs * lhs.car) + Poly(rhs * lhs.cdr)
            try:
                return lhs * Term(rhs, 0)
            except Exception:
                return NotImplemented

        if not isinstance(rhs, Poly):
            try:
                rhs = Poly(rhs)
            except Exception:
                return NotImplemented

        if method == '+':
            if lhs.iszero():
                return rhs
            if rhs.iszero():
                return lhs
            if lhs.car.exp < rhs.car.exp:
                return Poly(lhs.car, rhs.op(lhs.cdr, '+'))
            if lhs.car.exp > rhs.car.exp:
                return Poly(rhs.car, lhs.op(rhs.cdr, '+'))

            car = lhs.car.copy()
            car.coef += rhs.car.coef
            if lhs.cdr is None:
                cdr = rhs.cdr
            elif rhs.cdr is None:
                cdr = lhs.cdr
            else:
                cdr = lhs.cdr.op(rhs.cdr, '+')

            if car.coef != 0:
                return Poly(car, cdr)
            if cdr is not None:
                return cdr
            return None

        if method == '/%':
            if rhs.iszero():
                raise ZeroDivisionError
            if lhs.deg() < rhs.deg():
                return Poly(0), lhs
            if rhs.deg() == 0:
                return 1 / rhs.car.coef * lhs, 0
            t2 = rhs.highest_term()
            res = Poly(lhs)
            quo = None
            while True:
                t1 = res.highest_term()
                if t1.exp < t2.exp:
                    return quo, res
                q = t1 / t2
                res -= rhs * q
                quo = Poly(q, quo)

        elif method == '//':
            return lhs.op(rhs, '/%')[0]
        elif method == '%':
            return lhs.op(rhs, '/%')[1]
        return NotImplemented

x = Poly(Term(1,1))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
