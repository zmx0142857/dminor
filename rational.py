#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""basic rational calculation"""

__author__ = 'Clarence Zhuo'

from polynomial import Poly

class Rat(object):
    """
    Doctest:

    >>> r1 = Rat(1,2)
    >>> r2 = Rat(2,4)
    >>> r3 = Rat(0,1)
    >>> r4 = Rat(0,3)
    >>> r5 = Rat(-3)
    >>> r6 = Rat('1/2')
    >>> r7 = Rat('3/')
    >>> r8 = Rat('0')
    >>> r9 = Rat('5.5')
    >>> r10 = Rat(5.5)
    >>> r1 == r2
    True
    >>> r1 < r3
    False
    >>> r3 != r4
    False
    >>> r7 == 3
    True
    >>> r9 == 5.5
    True
    >>> r10 == []
    False
    >>> r10 < ()
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'Rat' and 'tuple'

    >>> Rat(1,2) + Rat(-1,3)
    1/6
    >>> Rat(1,2) - Rat(-1, 3)
    5/6
    >>> Rat(100,90) * Rat(-3,25)
    -2/15
    >>> Rat(100,90) / Rat(-3,25)
    -250/27

    >>> from math import pi
    >>> approx(pi)
    355/113

    >>> Rat(1) * Poly(Rat(1), Rat(0))
    """
    def __init__(self, arg1=0, arg2=1):
        """
        Rat(int a=0, positive-int b=1) -> a/b
        Rat(Rat a, non-zero-value b=1) -> a/b
        Rat(float a, non-zero-value b=1) -> a/b
        Rat(str)
        """
        if isinstance(arg1, int):
            self._num = arg1
            # arg2 must be positive int:
            try:
                self._den = _check(arg2, key='den')
            except TypeError:
                print('TypeError:', type(arg1), arg1, type(arg2), arg2)
                self._num = Rat(type(arg2)(arg1))
                self._den = arg2

        elif isinstance(arg1, Rat):
            # arg2 must be Rat, int or float and arg2 != 0:
            _check(arg2, key='Rat')
            tmp = arg1 / arg2 if arg2 != 1 else arg1
            self._num = tmp._num
            self._den = tmp._den

        elif isinstance(arg1, float):
            # arg2 must be Rat, int or float and arg2 != 0:
            _check(arg2, key='float')
            tmp = arg1 / arg2
            if isinstance(tmp, Rat):
                self._num = tmp._num
                self._den = tmp._den
            else: # isinstance(tmp, float):
                self._num = tmp
                self._den = 1
                while self._num != int(self._num):
                    self._num *= 10
                    self._den *= 10
                self._num = int(self._num)
                self._self_reduce()

        elif isinstance(arg1, str):
            #  you may TRY STR.PARTITION in this part
            # arg2 must be 1:
            self._den = _check(arg2, key='str')
            index = arg1.find('/')
            try:
                # found '/':
                if index != -1:
                    self._num = int(arg1[:index])

                    # '/' is not the last character in the str:
                    if index + 1 != len(arg1):
                        self._den = int(arg1[index+1:])

                elif '.' in arg1:
                    tmp = Rat(float(arg1))
                    self._num, self._den = tmp._num, tmp._den

                else:
                    self._num = int(arg1)

            except ValueError as err:
                raise ValueError("Counldn't convert '%s' to Rat." % arg1)
        elif isinstance(arg1, Poly):
            self._num = arg1
            self._den = Poly(arg2)
        elif isinstance(arg1, type(arg2)) or isinstance(arg2, type(arg1)):
            self._num = arg1
            self._den = arg2
        else:
            print('Notimplemented:', type(arg1), arg1, type(arg2), arg2)
            raise NotImplementedError("Couldn't convert %s to Rat." % type(arg1))

    # getters and setters--------------------------------------

    @property
    def num(self):
        return self._num

    @property
    def den(self):
        return self._den

    @num.setter
    def num(self, value):
        self._num = _check(value, key='num')

    @den.setter
    def den(self, value):
        self._den = _check(value, key='den')

    # specials-------------------------------------------------

    # print()
    def __str__(self):

        def par(obj): # parenthesis
            try:
                if obj.precedence() < self.precedence():
                    return "(%s)" % obj
                else:
                    return "%s" % obj
            except AttributeError:
                return "%s" % obj

        if self._den == 1:
            return '%s' % self._num
        else:
            return par(self._num) + '/' +  par(self._den)

    # repr()
    __repr__ = __str__

    # float()
    def __float__(self):
        return self._num / self._den

    def to_float(self, length=15):
        num = self._num
        exp = quantity_level(float(self))
        while num < self._den:
            num *= 10
        return '0.%se%s' % (num * (10**length) // self._den, exp)

    # int()
    def __int__(self): # round up to 0
        if self._num >= 0:
            return self._num // self._den
        else:
            return -( -self._num // self._den )

    # len(): deprecated
    #def __len__(self):
    #    return len(str(self))

    # abs()
    def __abs__(self):
        return Rat(self._num, self._den) if (self._num >= 0) else Rat(-self._num, self._den)

    # operator ==
    def __eq__(self, other):
        try:
            other = Rat(other)
        except Exception:
            return False
        lhs = self.reduce()
        rhs = other.reduce()
        return lhs._num == rhs._num and lhs._den == rhs._den

    # operator !=
    def __ne__(self, other):
        return not self == other

    # operator <
    def __lt__(self, other):
        if not isinstance(other, Rat):
            try:
                other = Rat(other)
            except Exception:
                return NotImplemented
        return self._num * other._den < self._den * other._num

    # operator >
    def __gt__(self, other):
        if not isinstance(other, Rat):
            try:
                other = Rat(other)
            except Exception:
                return NotImplemented
        return other < self

    # operator <=
    def __le__(self, other):
        if not isinstance(other, Rat):
            try:
                other = Rat(other)
            except Exception:
                return NotImplemented
        return not other < self

    # operator >=
    def __ge__(self, other):
        return not self < other

    # unary operator +
    def __pos__(self):
        return self

    # unary operator -
    def __neg__(self):
        return Rat(-self._num, self._den)

    # operator +
    def __add__(self, other):
        return _do_operation(self, other, '+')

    def __radd__(self, other):
        return _do_operation(other, self, '+')

    # operator -
    def __sub__(self, other):
        return _do_operation(self, other, '-')

    def __rsub__(self, other):
        return _do_operation(other, self, '-')

    # operator *
    def __mul__(self, other):
        return _do_operation(self, other, '*')

    def __rmul__(self, other):
        return _do_operation(other, self, '*')

    # operator /
    def __truediv__(self, other):
        return _do_operation(self, other, '/')

    def __rtruediv__(self, other):
        return _do_operation(other, self, '/')

    # operator **
    def __pow__(self, other):
        return Rat(self._num ** other, self._den ** other)

    # other methods--------------------------------------------

    def copy(self):
        return Rat(self._num, self._den)

    def _self_reduce(self):
        d = _gcd(self._num, self._den)
        if d == 0:
            raise ValueError('Bug: d == 0 whlie reducing.')
        self._num //= d
        self._den //= d
        return None

    def reduce(self):
        r = self.copy()
        r._self_reduce()
        return r

    def str2d(self, pnt=True):
        """a delux view of the faction :)"""
        if self._den == 1:
            ret = '%s' % self._num
        else:
            width = max( len(str(self._num)), len(str(self._den)) ) + 2
            ret = str(self._num).center(width) + '\n'\
                    + ''.ljust(width, '-') + '\n'\
                    + str(self._den).center(width)

        if pnt:
            print(ret)
            return None
        else:
            return ret

    @staticmethod
    def precedence():
        return 10

# class ends---------------------------------------------------

def _check(value, *, key):
    """helper function for __init__()"""
    if key == 'num':
        if not isinstance(value, int):
            raise TypeError('Numerator must be int, %s given.' %\
                            type(value))

    elif key == 'den':
        msg = 'Denominator must be positive int, %s given' % value
        if not isinstance(value, int) or value <= 0:
            raise TypeError(msg)
        elif value <= 0:
            raise ValueError(msg)


    elif key == 'Rat' or key == 'float':
        if not isinstance(value, (int, float, Rat)):
            raise TypeError('The second argument must be '
                            'int, float or Rat when the first '
                            'argument is %s.' % key)
        elif value == 0:
            raise ZeroDivisionError('The second argument must '
                                    'be non-zero.')
    elif key == 'str':
        if value != 1:
            raise ValueError('The second argument must be 1 '
                             'when the first argument is str, '
                             '%s given.' % value)
    return value

def _gcd(a, b):
    try:
        a, b = abs(a), abs(b)
    except TypeError:
        pass
    while b != 0:
        a, b = b, a % b # same as: c = a % b; a = b; b = c
    return a

def gcd(*args):
    """
    gcd(*args) -> (int, list)

    Takes a few numbers, returns their greatest common
    denominator d, along with k0, k1, k2...kn, for which
    k0*args[0] + k1*args[1] + k2*args[2] +...+ kn*args[n] = d.
    """
    q = []
    r0, r1 = args[0], args[1]

    if r1 == 0:
        print(r0, '= 1 *', r0, '+ 1 * 0')
        return None

    while r1 != 0:
        q.append(-(r0 // r1))
        r0, r1 = r1, r0 % r1

    q.pop()
    if q == []:
        print(r0, '= 1 * 0 + 1 *', r0)
        return None

    c0, c1 = 1, q.pop()
    while q != []:
        c0 = c0 + q.pop() * c1
        c0, c1 = c1, c0

    if r0 < 0:
        r0, c0, c1 = -r0, -c0, -c1
    print(r0, '=', c0, '*', args[0], '+', c1, '*', args[1])

def _do_operation(lhs, rhs, method):
    """helper function for method __add__, __radd__, __sub__ and so on"""
    try:
        if not isinstance(lhs, Rat):
            lhs = Rat(lhs)
        if not isinstance(rhs, Rat):
            rhs = Rat(rhs)
    except Exception:
        return NotImplemented

    if method == '+' or method == '-':
        d = _gcd(lhs._den, rhs._den)
        if method == '+':
            func = lambda x,y: x+y
        else:
            func = lambda x,y: x-y
        ret = Rat(func(rhs._den // d * lhs._num, lhs._den // d * rhs._num),\
                lhs._den // d * rhs._den)
        ret._self_reduce()
        return ret
    elif method == '*':
        r1 = Rat(lhs._num, rhs._den)
        r1._self_reduce()
        r2 = Rat(rhs._num, lhs._den)
        r2._self_reduce()
        ret = Rat(r1._num * r2._num, r1._den * r2._den)
        ret._self_reduce()
        return ret
    elif method == '/':
        if rhs._num < 0:
            return _do_operation(lhs, Rat(-rhs._den, -rhs._num), '*')
        else:
            return _do_operation(lhs, Rat(rhs._den, rhs._num), '*')
    else:
        return NotImplemented

def _continued_frac(L):
    if len(L) == 1:
        return Rat(L[0])
    else:
        return Rat(L[0] + 1 / _continued_frac(L[1:]))

def approx(value, tolerance = 1e-6):
    """
    approx(value, tolerance = 1e-6) -> Rat

    returns a Rat with smaller _num and _den, abs(ret - value)
    < tolerance guarenteed.

    https://cn.mathworks.com/help/matlab/ref/rat.html
    """
    target = value
    den_list = []
    while True: # a substitute for do-while loop
        den_list.append(int(target))
        ret = _continued_frac(den_list)
        if abs(ret - value) < tolerance:
            return ret
        target = 1 /( target - den_list[-1] )

def choose(n, k):
    """
    choose(n, k) -> int

    Returns C_n^k, or n(n-1)...(n+1-k)/k!
    """
    err = 'Expecting a non-negative interger for k!'
    if not isinstance(k, int):
        raise TypeError(err)
    elif k < 0:
        raise ValueError(err)

    ret = 1
    if isinstance(n, int):
        if (k <= n):
            k = min(k, n-k)
        for i in range(1, k+1):
            # it's ok. int division won't truncate.
            ret = ret * (n - i + 1) // i
    else:
        for i in range(1, k+1):
            ret = ret * (n - i + 1) / i

    return ret

def Bernoulli(n):
    """
    Bernoulli(n) -> generator

    Algorithm Akiyama–Tanigawa algorithm for second Bernoulli numbers B_n^+
    yields Bernoulli number: 1, 1/2, 1/6, 0, -1/30...
    """
    err = 'Expecting a non-negative integer!'
    if not isinstance(n, int):
        raise TypeError(err)
    elif n < 0:
        raise ValueError(err)

    L = []
    for i in range(n+1):
        L.append(Rat(1, i+1))
        for j in range(i, 0, -1):
            L[j-1] = j * (L[j-1] - L[j])
        yield L[0]

def quantity_level(n):
    import math
    if n == 0:
        return 0
    return math.floor(math.log10(abs(n))) + 1

class RatFunc(Rat):
    def __call__(self, value):
        return self._num(value) / self._den(value)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
