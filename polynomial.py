#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deal with polynomials.
Comming soon:
    Bernoulli summation algorithm - p.sum()
"""

__author__ = 'Clarence Zhuo'

class Poly(object):
    """
    Doctest:

    >>> Poly(0)
    0
    >>> Poly()
    x
    >>> Poly(1,2,3)
    x^2 + 2x + 3
    >>> Poly(1,-1,-1)
    x^2 - x - 1
    >>> Poly(1,-4,-10)
    x^2 - 4x - 10
    >>> Poly(-1,-4,-10)
    -x^2 - 4x - 10
    >>> Poly(-1,-4,0)
    -x^2 - 4x
    >>> Poly(-1,0,-90)
    -x^2 - 90
    >>> Poly(lambda i: -i*i, 3)
    -9x^3 - 4x^2 - x
    
    >>> p = Poly(1,-2,3)
    >>> q = Poly(9,0,-1,3)
    >>> p+q
    9x^3 + x^2 - 3x + 6
    >>> p-q
    -9x^3 + x^2 - x
    
    >>> p = Poly(1,1)
    >>> p**2
    x^2 + 2x + 1
    >>> p
    x + 1
    >>> q = Poly(1,-1)
    >>> p*q
    x^2 - 1
    
    >>> p = Poly(1,-3,2)
    >>> p(5)
    12
    >>> p
    x^2 - 3x + 2
    >>> p(2)
    0
    >>> Poly(-1, 0, -2, 1).diff()
    -3x^2 - 2
    >>> divmod(Poly(1, -1)**5, Poly(1, -2)**4)
    (x + 3.0, 10.0x^3 - 50.0x^2 + 85.0x - 49.0)

    >>> Poly(1, 0, 0, sym='t')(Poly(1, -1))
    x^2 - 2x + 1
    >>> #Poly(1, -1)(Poly(1, 0, 0, sym='t')) # got t^2 - 1
    """
    symbol = 'x'
    def __init__(self, *args, sym=None, reverse=True):
        """
        Poly() -> polynomial x
        Poly(Poly p) -> a copy of p
        Poly(Iterable) -> init from Iterable
        Poly(callable f, n) -> f(n) x^n + ... + f(1) x + f(0) 
        Poly(an, ..., a1, a0) -> an x^n + ... + a1 x + a0
        """
        from collections import Iterable
        self.sym = sym if sym != None else self.symbol

        argc = len(args)
        if argc == 0:
            self.coef = [0, 1] # polynomial x
        elif argc == 1 and isinstance(args[0], Poly):
            self.coef = list(args[0].coef)
        elif argc == 1 and isinstance(args[0], Iterable):
            self.coef = list(args[0])
        elif argc == 2 and callable(args[0]):
            if not isinstance(args[1], int) or args[1] < 0:
                raise TypeError('The 2nd argument (degree) '
                                'must be a non-negative int.')
            self.coef = [args[0](i) for i in range(args[1]+1)]
        else:
            if reverse:
                self.coef = list(reversed(args))
            else:
                self.coef = list(args)
    
        # invariant: len(self.coef) >= 1

        self.rmzero()
    
    # specials-------------------------------------------------
    
    def __getitem__(self, key):
        """
        Returns Cn, the coefficient of item x^n.
        """
        if not isinstance(key, int):
            raise TypeError('Key must be an int.')
        elif key < -len(self.coef):
            raise IndexError('Index out of range.')
        elif key > len(self.coef)-1:
            return 0 # higher degree coefficient == 0
        else:
            return self.coef[key]
    
    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError('Key must be an int.')
        elif key < -len(self.coef):
            raise IndexError('Index out of range.')
    
        while key > self.deg():
            self.coef.append(0)
        self.coef[key] = value
    
    def __str__(self):
    
        n = len(self.coef)-1
        ret = ''

        # reversed iteration
        for k in range(n, -1, -1):

            # ignore those with coef == 0
            # except for zero polynomial
            if self[k] == 0 and n != 0:
                continue

            # 'sign'
            # process highest degree item specially
            # self[k] is the kth degree coefficient
            if k == n:
                sign = '-' if self[k] < 0 else ''
            else:
                sign = ' - ' if self[k] < 0 else ' + '

            # 'coefficient'
            abscoef = abs(self[k])
            if abscoef == 1 and k != 0:
                coef = ''
            else:
                coef = str(abscoef)

            # 'symbol and its exponent'
            if k == 0:
                expo = ''
            elif k == 1:
                expo = self.sym
            else:
                expo = self.sym + '^' + str(k)

            ret += sign + coef + expo

        return ret
    
    __repr__ = __str__
    
    def __call__(self, v):
        """
        Poly(v) -> result
    
        Assign a value to polynomial, using Horner's rule.
        """
        ret = self[-1]
        for c in self.coef[-2::-1]:
            ret = ret * v + c
        return ret
    
    def __eq__(self, other):
        try:
            other = Poly(other)
        except Exception:
            return False
        # list will compare lexicographically
        return self.coef == other.coef
    
    def __ne__(self, other):
        return not self == other
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return Poly((-c for c in self.coef), sym=self.sym)
    
    def __add__(self, other):
        return _do_operation(self, other, '+')
    
    def __radd__(self, other):
        return _do_operation(other, self, '+')
    
    def __sub__(self, other):
        return _do_operation(self, other, '-')
    
    def __rsub__(self, other):
        return _do_operation(other, self, '-')
    
    def __mul__(self, other):
        return _do_operation(self, other, '*')
    
    def __rmul__(self, other):
        return _do_operation(other, self, '*')

    def __divmod__(self, other):
        return _do_operation(self, other, '/%')

    def __floordiv__(self, other):
        return _do_operation(self, other, '//')

    __truediv__ = __floordiv__

    def __mod__(self, other):
        return _do_operation(self, other, '%')

    def __pow__(self, other):
        if not isinstance(other, int) or other < 0:
            raise TypeError('arg2 for __pow__() must be '
                            'non-negative integer!')
        ret = Poly(1, sym=self.sym)
        for i in range(other):
            ret *= self
        return ret

    # other methods--------------------------------------------
    
    def deg(self):
        """
        Poly.deg() -> non-negative int
    
        Returns the degree of self. Degree of zero is -1.
        """
        if self.iszero():
            return -1
        else:
            return len(self.coef)-1
    
    def sym(self, c=None):
        """
        Poly.sym() -> str
        Poly.sym(c) -> None
        
        Reset the variable name for self.
        """
        if c == None:
            return self.sym
        self.sym = c

    def iszero(self):
        """Returns True iff self == zero polynomial."""
        return len(self.coef) == 1 and self[0] == 0

    def rmzero(self):
        """Remove extra zeros."""
        while len(self.coef) > 1 and self.coef[-1] == 0:
            self.coef.pop()

    def diff(self):
        """Derivate of polynomial."""
        if len(self.coef) == 1:
            return Poly(0, sym=self.sym)
        return Poly((self[i] * i for i in range(1, len(self.coef))),\
                sym=self.sym)

    def precedence(self):
        cnt = 0
        for c in self.coef:
            if c != 0:
                if cnt == 0:
                    cnt = 1
                else:
                    return 9 # binary +
        return 15 # highest precedence

# class ends---------------------------------------------------

def _do_operation(lhs, rhs, method):
    """helper function for method __add__, __radd__, __sub__ and so on"""
    try:
        if not isinstance(lhs, Poly):
            lhs = Poly(lhs)
        if not isinstance(rhs, Poly):
            rhs = Poly(rhs)
    except Exception:
        return NotImplemented

    if method == '+' or method == '-':
        if method == '+':
            func = lambda x,y: x+y
        else:
            func = lambda x,y: x-y
        length = max(len(lhs.coef), len(rhs.coef))
        return Poly((func(lhs[i], rhs[i]) for i in range(length)),\
                sym=lhs.sym)

    elif method == '*':
        if lhs.iszero() or rhs.iszero():
            return Poly(0, sym=lhs.sym)
        """
        0 <= i < len(lhs.coef)
        0 <= j-i < len(rhs.coef) <---> j-len(rhs.coef) < i <= j
        hence max(0, j-len(rhs)+1) <= i < min(j+1, len(lhs.coef))
        """
        lenl, lenr = len(lhs.coef), len(rhs.coef)
        return Poly((sum(lhs[i] * rhs[j-i] for i in range(max(0, j-lenr+1),\
                min(j+1, lenl))) for j in range(lenl+lenr)), sym=lhs.sym )

    elif method == '/%':
        if rhs.iszero():
            raise ZeroDivisionError
        elif lhs.deg() < rhs.deg():
            return Poly(0, sym=lhs.sym), lhs
        elif rhs.deg() == 0:
            return 1 / rhs[0] * lhs, 0
        """ considering M / N: first have their coef reversed, so N0 is
        the highest degree coef for N
                    N0                  N1      N2
        q0 = c0/N0  c0 = M0             q0N1    q0N2
        q1 = c1/N0  c1 = M1-q0N1        q1N1    q1N2
        q2 = c2/N0  c2 = M2-q0N2-q1N1   q2N1    q2N2
        """
        m, n = lhs.deg(), rhs.deg()
        q = []
        for i in range(m-n+1):
            q.append( lhs[m-i] - sum(q[j] * rhs[n-i+j] for j in\
                range(max(0, i-n), i)) )
            q[i] /= rhs[n]
        r = (lhs[i] - sum(q[m-n-i+j] * rhs[j] for j in range(max(0, n+i-m),\
                i+1)) for i in range(n))
        return Poly(reversed(q), sym=lhs.sym), Poly(r, sym=lhs.sym)

    elif method == '//':
        return _do_operation(lhs, rhs, '/%')[0]
    elif method == '%':
        return _do_operation(lhs, rhs, '/%')[1]
    else:
        return NotImplemented

if __name__ == '__main__':
    import doctest
    doctest.testmod()

