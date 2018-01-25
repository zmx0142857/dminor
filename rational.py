"""Provides basic rational calculation.

"""

__author__ = 'Clarence'

class Rat(object):
    '''
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
    NotImplementedError

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
    '''
    def __init__(self, first = 0, second = 1):

        if isinstance(first, int):
            self._num = first
            # second must be positive int:
            self._den = _check(second, type = 'den')

        elif isinstance(first, Rat):
            # second must be Rat, int or float and second != 0:
            _check(second, type = 'Rat')
            tmp = first / second
            self._num = tmp._num
            self._den = tmp._den

        elif isinstance(first, float):
            # second must be Rat, int or float and second != 0:
            _check(second, type = 'float')
            tmp = first / second
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

        elif isinstance(first, str):
            #  you may TRY STR.PARTITION in this part
            # second must be 1:
            self._den = _check(second, type = 'str')
            index = first.find('/')
            try:
                # found '/':
                if index != -1:
                    self._num = int(first[:index])

                    # '/' is not the last character in the str:
                    if index + 1 != len(first):
                        self._den = int(first[index+1:])

                elif '.' in first:
                    tmp = Rat(float(first))
                    self._num, self._den = tmp._num, tmp._den

                else:
                    self._num = int(first)

            except ValueError as err:
                raise ValueError("Counldn't convert '%s' to Rat." % first)
        else:
            raise NotImplementedError("Couldn't convert %s to Rat." % type(first))

    # getters and setters--------------------------------------

    @property
    def num(self):
        return self._num

    @property
    def den(self):
        return self._den

    @num.setter
    def num(self, value):
        self._num = _check(value, type = 'num')

    @den.setter
    def den(self, value):
        self._den = _check(value, type = 'den')

    # specials-------------------------------------------------

    # print()
    def __str__(self):
        if self._den == 1:
            return '%d' % self._num
        else:
            return '%d/%d' % (self._num, self._den)

    # repr()
    __repr__ = __str__

    # float()
    def __float__(self):
        return self._num / self._den

    # int()
    def __int__(self): # round up to 0
        if self._num >= 0:
            return self._num // self._den
        else:
            return -( -self._num // self._den )

    # len()
    def __len__(self):
        return len(self.__str__())

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
        try:
            other = Rat(other)
        except Exception:
            raise NotImplementedError
        return self._num * other._den < self._den * other._num

    # operator >
    def __gt__(self, other):
        return other < self

    # operator <=
    def __le__(self, other):
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
        return _do_add(self, Rat(other), lambda x,y: x+y)

    def __radd__(self, other):
        return _do_add(Rat(other), self, lambda x,y: x+y)

    # operator -
    def __sub__(self, other):
        return _do_add(self, Rat(other), lambda x,y: x-y)

    def __rsub__(self, other):
        return _do_add(Rat(other), self, lambda x,y: x-y)

    # operator *
    def __mul__(self, other):
        return _do_mul(self, Rat(other))

    def __rmul__(self, other):
        return _do_mul(Rat(other), self)

    # operator /
    def __truediv__(self, other):
        return _do_truediv(self, Rat(other))

    def __rtruediv__(self, other):
        return _do_truediv(Rat(other), self)

    # operator **
    def __pow__(self, other):
        return Rat(self._num ** other, self._den ** other)

    # other methods--------------------------------------------

    def _self_reduce(self):
        d = _gcd(self._num, self._den)
        if d == 0:
            raise ValueError('Bug: d == 0 whlie reducing.')
        self._num //= d
        self._den //= d
        return self

    def reduce(self):
        return Rat(self._num, self._den)._self_reduce()

    def delux_str(self, pnt = True):
        """Returns a delux view of the faction :)

        """
        if self._den == 1:
            ret = '%s' % self._num
        else:
            width = max( len(str(self._num)), len(str(self._den)) ) + 2
            ret = str(self._num).center(width) + '\n'  + ''.ljust(width, '-') + '\n' + str(self._den).center(width)

        if pnt:
            print(ret)
            return None
        else:
            return ret

# class ends---------------------------------------------------

def _check(value, *, type):
    if type == 'num':
        if not isinstance(value, int):
            raise TypeError('Numerator must be int.')

    elif type == 'den':
        if not isinstance(value, int) or value <= 0:
            raise ValueError('Denominator must be positive '
                             'int.')

    elif type == 'Rat' or type == 'float':
        if not isinstance(value, (int, float, Rat)):
            raise TypeError('The second argument must be '
                            'int, float or Rat when the first '
                            'argument is %s.' % type)
        elif value == 0:
            raise ZeroDivisionError('The second argument must '
                                    'be non-zero.')
    elif type == 'str':
        if value != 1:
            raise ValueError('The second argument must be 1 '
                             'when the first argument is str.')
    return value

def _gcd(a, b):
    a, b = abs(a), abs(b)
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

def _do_add(self, other, func):
    d = _gcd(self._den, other._den)
    ret = Rat(func(other._den // d * self._num, self._den // d * other._num), self._den // d * other._den)
    return ret._self_reduce()

def _do_mul(self, other):
    lhs = Rat(self._num, other._den)._self_reduce()
    rhs = Rat(other._num, self._den)._self_reduce()
    return Rat(lhs._num * rhs._num, lhs._den * rhs._den)._self_reduce()

def _do_truediv(self, other):
    if other._num < 0:
        return _do_mul(self, Rat(-other._den, -other._num))
    else:
        return _do_mul(self, Rat(other._den, other._num))

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
