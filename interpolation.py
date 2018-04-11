#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import polynomial

class Lagrange(object):

    """Build Lagrange interpolation polynomial and compute its value.
    The formula is:

    L(x) = sum_(i=1)^n y_i * prod_(1<=j!=i<=n) (x - x_j) / (x_i - x_j)

    >>> x0 = [1, 2, 3, 4, 5]
    >>> y0 = [0, 2, 12, 42, 116]
    >>> f = Lagrange(x0, y0)
    >>> f(1.5)
    0.28125
    >>> f
    0.4999999999999991x^4 - 3.0x^3 + 9.5x^2 - 13.0x + 6.0
    """

    def __init__(self, x_list, y_list):

        if (len(x_list) != len(y_list)):
            raise ValueError('The size of two lists are not equal!')

        self.x = x_list             # warning: self.x is read-only
        self.n = len(self.x)
        self.coef = y_list.copy()
        for i in range(self.n):
            for j in range(self.n):
                if j != i:
                    self.coef[i] /= (self.x[i] - self.x[j])

    def __call__(self, s):
        ret = 0
        for i in range(self.n):
            item = 1
            for j in range(self.n):
                if j != i:
                    item *= (s - self.x[j])
            ret += item * self.coef[i]
        return ret

    def __str__(self):
        return str(self(polynomial.Poly()))

    __repr__ = __str__

class Neville(object):

    """Build Neville interpolation polynomial and compute its value.
    The formula is:

    P(x,i,j) = ((x_j - x)*P(x,i,j-1) + (x - x_i)*P(x,i+1,j)) / (x_j - x_i)

    >>> x0 = [-1, 0, 0.5, 1]
    >>> y0 = [-1.5, 0, 0, 0.5]
    >>> f = Neville(x0, y0)
    >>> f(-1), f(0), f(0.5), f(1)
    (-1.5, 0.0, 0.0, 0.5)
    >>> f
    x^3 - 0.5x^2
    """
    def __init__(self, x_list, y_list):

        if (len(x_list) != len(y_list)):
            raise ValueError('The size of two lists are not equal!')

        self.x = x_list             # warning: self.x is read-only
        self.y = y_list
        self.n = len(self.x)

    def __call__(self, s):
        x = self.x
        y = self.y.copy()
        for i in range(1, self.n):
            for j in range(self.n-i):
                y[j] = ((x[j+i]-s)*y[j] + (s-x[j])*y[j+1]) / (x[j+i] - x[j])
        return y[0]

    def __str__(self):
        return str(self(polynomial.Poly()))

    __repr__ = __str__

class Newton(object):

    """Build Newton interpolation polynomial and compute its value.
    The formula is:

    N_0(x) = y0
    N_n(x) = N_(n-1)(x) + prod_(i=0)^(n-1) (x-x_j) * f[x0,x1,x2..xn]

    and

    N(x) = f[x0] + (x-x0)f[x0,x1]
                 + (x-x0)(x-x1)f[x0,x1,x2]
                 + (x-x0)(x-x1)(x-x2)f[x0,x1,x2,x3]
                 + ...
                 + (x-x0)(x-x1)...(x-x(n-1))f[x0..xn]

    >>> x0 = [1, 2, 3, 4, 5]
    >>> y0 = [0, 2, 12, 42, 116]
    >>> f = Newton(x0, y0)
    >>> f(1.5)
    0.28125
    >>> f.insert(6, 282)
    >>> f(1.5)
    0.609375
    >>> f.erase(1)
    >>> f(1.5)
    0.28125

    >>> x0 = [0, 1, 1]
    >>> y0 = [1, 0, 0]
    >>> f = Newton(x0, y0)
    >>> f.insert(0, 0)
    >>> f # f(0) = 1, f'(0) = 0, f(1) = 0, f'(1) = 0
    2.0x^3 - 3.0x^2 + 1.0
    """
    def __init__(self, x_list, y_list):

        if (len(x_list) != len(y_list)):
            raise ValueError('The size of two lists are not equal!')

        self.diff = [[x_list[i], y_list[i]] for i in range(len(x_list))]
        self.diff.sort(key=lambda L: L[0]) # sort in-place by value of x
        self._compute_diff()

    def _compute_diff(self):
        """
        diff table
        x0 y0
        x1 y1 [x0,x1]
        x2 y2 [x1,x2] [x0,x1,x2]
        x3 y3 [x2,x3] [x1,x2,x3] [x0,x1,x2,x3]

        repeated node situation
        x0 y0
        x0 y0 y'0
        x0 y0 y'0     y''0
        x1 y1 [x0,x1] [x0,x0,x1] [x0,x0,x0,x1]
        x1 y1 y'1     [x0,x1,x1] [x0,x0,x1,x1] [x0,x0,x0,x1,x1]
        """
        d = self.diff
        x = lambda i: d[i][0]

        for i in range(1, len(d)):
            while len(d[i]) < i + 2:
                j = len(d[i]) - 1
                if x(i) != x(i-j):
                    d[i].append( (d[i][j] - d[i-1][j]) / (x(i) - x(i-j)) )
                else:
                    d[i] = d[i-1][:j+1] + [d[i][1]]

    def insert(self, x_list, y_list):
        """
        insert new data
        """
        from collections import Iterable
        if not isinstance(x_list, Iterable):
            x_list = [x_list]
        if not isinstance(y_list, Iterable):
            y_list = [y_list]
        if (len(x_list) != len(y_list)):
            raise ValueError('The size of two lists are not equal!')

        self.diff.extend([x_list[i], y_list[i]] for i in range(len(x_list)))
        self.diff.sort(key=lambda L: L[0]) # sort in-place by value of x
        self._compute_diff()

    def erase(self, n=1):
        """
        erase n of the existing data from the end
        """
        if len(self.diff) < n:
            raise IndexError('Does not have enough data to erase!')
        for k in range(n):
            self.diff.pop()

    def __call__(self, s):
        """
        returns value by Horner's rule
        """
        ret = self.diff[-1][-1]
        for i in range(len(self.diff)-2, -1, -1):
            ret = ret * (s - self.diff[i][0]) + self.diff[i][i+1]
        return ret

    def __str__(self):
        return str(self(polynomial.Poly()))

    def dump(self):
        """
        for debugging
        """
        print('\n'.join(' '.join(str(elem) for elem in row) for row in self.diff))

    __repr__ = __str__

if __name__ == '__main__':
    import doctest
    doctest.testmod()
