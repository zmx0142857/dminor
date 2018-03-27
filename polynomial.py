#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deal with polynomials.
Comming soon:
    init by interpolation formula;
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
    """
    def __init__(self, *args, sym='x', reverse=True):
        """
        Poly() -> polynomial x
        Poly(Poly p) -> a copy of p
        Poly(Iterable) -> init from Iterable
        Poly(callable f, n) -> f(n) x^n + ... + f(1) x + f(0) 
        Poly(an, ..., a1, a0) -> an x^n + ... + a1 x + a0
        """
        from collections import Iterable
        self._sym = sym

        argc = len(args)
        if argc == 0:
            self._coef = [0, 1] # polynomial x
        elif argc == 1 and isinstance(args[0], Poly):
            self._coef = list(args[0]._coef)
        elif argc == 1 and isinstance(args[0], Iterable):
            self._coef = list(args[0])
        elif argc == 2 and callable(args[0]):
            if not isinstance(args[1], int) or args[1] < 0:
                raise TypeError('The 2nd argument (degree) '
                                'must be a non-negative int.')
            self._coef = [args[0](i) for i in range(args[1]+1)]
        else:
            if reverse:
                self._coef = list(reversed(args))
            else:
                self._coef = list(args)
    
        # invariant: len(self._coef) >= 1

        self.rmzero()
    
    # specials-------------------------------------------------
    
    def __getitem__(self, key):
        """
        Returns Cn, the coefficient of item x^n.
        """
        if not isinstance(key, int):
            raise TypeError('Key must be an int.')
        elif key < -len(self._coef):
            raise IndexError('Index out of range.')
        elif key > len(self._coef)-1:
            return 0 # higher degree coefficient == 0
        else:
            return self._coef[key]
    
    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError('Key must be an int.')
        elif key < -len(self._coef):
            raise IndexError('Index out of range.')
    
        while key > self.deg():
            self._coef.append(0)
        self._coef[key] = value
    
    def __str__(self):
    
        n = len(self._coef)-1
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
            abs_coef = abs(self[k])
            if abs_coef == 1 and k != 0:
                coef = ''
            else:
                coef = str(abs_coef)

            # 'symbol and its exponent'
            if k == 0:
                expo = ''
            elif k == 1:
                expo = self._sym
            else:
                expo = self._sym + '^' + str(k)

            ret += sign + coef + expo

        return ret
    
    __repr__ = __str__
    
    def __call__(self, v):
        """
        Poly(v) -> result
    
        Assign a value to polynomial, using Horner's rule.
        """
        ret = self[-1]
        for c in self._coef[-2::-1]:
            ret = ret * v + c
        return ret
    
    def __eq__(self, other):
        try:
            other = Poly(other)
        except Exception:
            return False
        # list will compare lexicographically
        return self._coef == other._coef
    
    def __ne__(self, other):
        return not self == other
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return Poly(-c for c in self._coef)
    
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

    def __mod__(self, other):
        return _do_operation(self, other, '%')

    def __pow__(self, other):
        if not isinstance(other, int) or other < 0:
            raise TypeError('arg2 for __pow__() must be '
                            'non-negative integer!')
        ret = Poly(1)
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
            return len(self._coef)-1
    
    def sym(self, c=None):
        """
        Poly.sym() -> str
        Poly.sym(c) -> None
        
        Reset the variable name for self.
        """
        if c == None:
            return self._sym
        self._sym = c

    def iszero(self):
        """Returns True iff self == zero polynomial."""
        return len(self._coef) == 1 and self[0] == 0

    def rmzero(self):
        """Remove extra zeros."""
        while len(self._coef) > 1 and self._coef[-1] == 0:
            self._coef.pop()

    def diff(self):
        """Derivate of polynomial."""
        if len(self._coef) == 1:
            return Poly(0)
        return Poly(self[i] * i for i in range(1, len(self._coef)))

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
        length = max(len(lhs._coef), len(rhs._coef))
        return Poly(func(lhs[i], rhs[i]) for i in range(length))

    elif method == '*':
        if lhs.iszero() or rhs.iszero():
            return Poly(0)
        # 0 <= i < len(lhs._coef)
        # 0 <= j-i < len(rhs._coef) <---> j-len(rhs._coef) < i <= j
        # hence max(0, j-len(rhs)+1) <= i < min(j+1, len(lhs._coef))
        lenl, lenr = len(lhs._coef), len(rhs._coef)
        return Poly(sum(lhs[i] * rhs[j-i] for i in range(max(0, j-lenr+1),\
                min(j+1, lenl))) for j in range(lenl+lenr) )

    elif method == '/%':
        pass
    elif method == '//':
        pass
    elif method == '%':
        pass
    else:
        return NotImplemented

if __name__ == '__main__':
    import doctest
    doctest.testmod()

