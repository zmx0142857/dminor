#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Lagrange(object):

    """Build Lagrange interpolation polynomial and compute its value.
    The formula is:

    L(x) = sum_(i=1)^n y_i * prod_(1<=j!=i<=n) (x - x_j) / (x_i - x_j)

    >>> x0 = [1, 2, 3, 4, 5]
    >>> y0 = [0, 2, 12, 42, 116]
    >>> f = Lagrange(x0, y0)
    >>> f(1.5)
    0.28125
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
                    self.coef[i] *= 1 / (self.x[i] - self.x[j])

    def __call__(self, s):
        ret = 0
        for i in range(self.n):
            item = 1
            for j in range(self.n):
                if j != i:
                    item *= (s - self.x[j])
            ret += item * self.coef[i]
        return ret

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
    """
    def __init__(self, x_list, y_list):

        if (len(x_list) != len(y_list)):
            raise ValueError('The size of two lists are not equal!')

        self.x = x_list             # warning: self.x is read-only
        self.n = len(self.x)
        self.diff = [[yi] for yi in y_list]
        self._compute_diff(self.diff, self.x)

    def _compute_diff(self, d, x):
        """diff table
        x0 y0
        x1 y1 [x0,x1]
        x2 y2 [x1,x2] [x0,x1,x2]
        x3 y3 [x2,x3] [x1,x2,x3] [x0,x1,x2,x3]
        """
        for i in range(1, self.n):
            for j in range(i):
                d[i].append((d[i][j] - d[i-1][j]) / (x[i] - x[i-j-1]))

    def __call__(self, s):
        ret = self.diff[-1][-1]
        for i in range(self.n-2, -1, -1):
            ret = ret * (s - self.x[i]) + self.diff[i][i]
        return ret

    def insert(self, x_list, y_list):
        """insert new data 
        """
        from collections import Iterable
        if not isinstance(x_list, Iterable):
            x_list = [x_list]
        if not isinstance(y_list, Iterable):
            y_list = [y_list]
        if (len(x_list) != len(y_list)):
            raise ValueError('The size of two lists are not equal!')

        d = self.diff
        x = self.x
        for i in range(len(x_list)):
            x.append(x_list[i])
            d.append([y_list[i]])
            for j in range(self.n + i):
                d[-1].append((d[-1][j] - d[-2][j]) / (x[-1] - x[-2-j]))
        self.n += len(x_list)

    def erase(self, n):
        """erase n of the existing data
        """
        if len(self.diff) < n:
            raise IndexError('Does not have enough data to erase!')
        for k in range(n):
            self.diff.pop()
        self.n -= n

if __name__ == '__main__':
    import doctest
    doctest.testmod()
