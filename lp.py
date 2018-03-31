#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Linear Programming"""

__author__ = 'Clarence Zhuo'

import matrix

le = -1
eq = 0
ge = 1

class LP(object):
    """
    Doctest:
    >>> mat = matrix.Mat('''
    ... 1 2 1 0 0 8
    ... 4 0 0 1 0 16
    ... 0 4 0 0 1 12''')
    >>> chk = [2, 3, 0, 0, 0]
    >>> base = [2, 3, 4]
    >>> lp = LP(mat, chk, base)
    >>> lp.solve()
    ('best solution', [4, 2, 0, 0, 4], 14)
    >>> base
    [1, 0, 4]
    >>> chk
    [2, 3, 0, 0, 0]

    >>> mat = matrix.Mat('''
    ... 1 -2 1 1 0 0 0 11
    ... -4 1 2 0 -1 1 0 3
    ... -2 0 1 0 0 0 1 1''')
    >>> chk = [0, 0, 0, 0, 0, 1, 1]
    >>> base = [3, 5, 6]
    >>> lp = LP(mat, chk, base, maximum=False)
    >>> lp.solve()
    ('best solution', [0, 1, 1, 12, 0, 0, 0], 0)

    >>> mat = matrix.Mat('''
    ... 1 -2 1 11
    ... -4 1 2 3
    ... -2 0 1 1''')
    >>> chk = [-3, 1, 1]
    >>> rel = [le, ge, eq]
    >>> lp = LP(mat, chk, maximum=False, relation=rel)
    >>> lp
    min z = -3x1 + x2 + x3
    s.t.
        x1 - 2x2 + x3 <= 11
        -4x1 + x2 + 2x3 >= 3
        -2x1 + x3 = 1
        all xi >= 0
    >>> lp.solve()
    ('best solution', [4, 1, 9, 0, 0], -2)

    >>> mat = matrix.Mat('''
    ... 1 0 0 1/4 -8 -1 9 0
    ... 0 1 0 1/2 -12 -1/2 3 0
    ... 0 0 1 0 0 1 0 1''')
    >>> chk = [0, 0, 0, 0.75, -20, 0.5, -6]
    >>> base = [0, 1, 2]
    >>> lp = LP(mat, chk, base)
    >>> lp.solve()
    ('best solution', [3/4, 0, 0, 1, 0, 1, 0], 5/4)
    """
    def __init__(self, mat, chk_list, base=None, maximum=True,\
            relation=None):
        """
        LP(Mat, check_list, base_index) -> LP object

        mat := [A, b] is the argumented matrix for a standardized LP problem
        chk_list is a list of checking numbers for each variable x_i
        base is indeces of base vectors
        build a matrix like:
            A | b
          chk | -z

        * NOTE *
        1. LP changes mat and base;
        2. LP does maximization by default.
        """
        self.mat = mat
        self.base = base if base != None else []
        self.artificial = self.mat.cols()-1
        self.maximum = maximum
        self.chk_list = list(chk_list) if maximum else [-c for c in chk_list]
        matrix.resize(self.chk_list, self.mat.cols())
        self.relation = relation if relation != None\
                else [eq for col in self.mat]

    # adding artificial variables
    def art(self, relation):
        if self.base == []:
            if relation == None:
                raise ValueError('relation must not be None when base is not '
                                 'given')
            rows = self.mat.rows()
            matrix.resize(relation, rows, fill=0)
            for i, rel in enumerate(relation):
                if rel == le:
                    self.mat.insert(matrix.e(rows, i), col=self.artificial)
                    self.chk_list.append(0)
                    self.base.append(self.artificial)
                    self.artificial += 1
                elif rel == eq:
                    # insert before last column
                    self.mat.insert(matrix.e(rows, i), col=-1)
                    self.base.append(self.mat.cols()-2)
                elif rel == ge:
                    self.mat.insert(((matrix.Rat(-1) if i == j else\
                        matrix.Rat(0)) for j in range(rows)),\
                        col=self.artificial)
                    self.artificial += 1
                    self.mat.insert(matrix.e(rows, i), col=-1)
                    self.chk_list.append(0)
                    self.base.append(self.mat.cols()-2)

    def compute_theta(self, col):
        rows = self.mat.rows()-1
        theta = [0 for i in range(rows)]
        min_theta = 0
        ret = None
        for row in range(rows):
            if self.mat[row][col] == 0:
                continue
            theta[row] = self.mat[row][-1] / self.mat[row][col]
            if theta[row] > 0 and (min_theta == 0 or theta[row] < min_theta):
                min_theta = theta[row]
                ret = row
        return ret

    def solve(self, verbose=False):

        status_str = ['processing', 'no solution', 'best solution',\
                'unbounded solution']
        status = 0

        self.art(self.relation)
        # exist artificial variable, use two-step method
        if self.artificial < self.mat.cols() - 1:
            chk_list = [(0 if i < self.artificial else -1)\
                    for i in range(self.mat.cols()-1)]
            lp = LP(self.mat, chk_list, self.base) 
            result = lp.solve(verbose)
            if verbose:
                print('after first step:\n%s' % self.mat)
                print('base: %s' % self.base)
            if not isinstance(result, tuple) or result[2] != 0:
                return status_str[1]
            while self.artificial < self.mat.cols() - 1:
                self.mat.pop(col=-2)
            self.mat[-1] = self.chk_list
            if verbose:
                print('chk-appended:\n%s' % self.mat)
        else:
            self.mat._data.append(self.chk_list)

        # use primary transform on check numbers
        row = 0
        for col in self.base:
            chk = self.mat[-1][col]
            if chk != 0:
                self.mat.pr(row = -1, row2 = row, k = -chk)
            row += 1
        if verbose:
            print('chk-processed:\n%s' % self.mat)
            print('base: %s' % self.base)

        while status == 0:
            status = 2
            for col in range(self.mat.cols()-1):
                if col in self.base or self.mat[-1][col] <= 0:
                    continue

                # positie chk_number for non-base variable found
                swap_in = col
                swap_out = self.compute_theta(col)

                # this happens when there's no positive theta, or the
                # denominator == 0 when computing theta
                if swap_out == None:
                    status = 3
                    continue
                else:
                    status = 0
                    break

            # no positive chk_number means best solution obtained
            if status == 2:
                x = [0 for i in range(self.mat.cols()-1)]
                for i, b in enumerate(self.base):
                    # non-zero artificial variable exist in base
                    #if b >= self.artificial and self.mat[i][-1] != 0:
                    #    return status_str[1]
                    x[b] = self.mat[i][-1]
                z = self.mat[-1][-1]
                if self.maximum:
                    z = -z
                return status_str[status], x, z

            # swap_out == None for each col with chk_number > 0
            elif status == 3:
                break

            # now that status == 0, the iteration have to continue
            self.mat.pr(row = swap_out, k = 1/self.mat[swap_out][swap_in])
            for row in range(self.mat.rows()):
                if row != swap_out:
                    self.mat.pr(row = row, row2 = swap_out,\
                            k = -self.mat[row][swap_in])

            # update base
            self.base[swap_out] = swap_in

            if verbose:
                print("after transformation:\n%s" % self.mat)
                print("base: %s" % self.base)

        return status_str[status]

    def __str__(self):

        def expr(r):
            if self.relation[r] == le:
                rel = ' <= '
            elif self.relation[r] == eq:
                rel = ' = '
            else:
                rel = ' >= '
            row = self.mat[r]
            return '    ' + line(row) + rel + str(row[-1])

        def line(row):
            ret = ''
            first_item = True
            for i in range(len(row)-1):
                # skip zero
                if row[i] == 0:
                    continue
                # sign
                if first_item:
                    sign = '-' if row[i] < 0 else ''
                    first_item = False
                else:
                    sign = ' - ' if row[i] < 0 else ' + '
                # coefficient
                abs_coef = abs(row[i])
                if abs_coef == 1:
                    coef = ''
                else:
                    coef = str(abs_coef)
                # symbol
                sym = 'x' + str(i+1)
                ret += sign + coef + sym
            return ret

        def target():
            if self.maximum:
                m = 'max'
                chk_list = self.chk_list
            else:
                m = 'min'
                chk_list = [-c for c in self.chk_list]
            return m + ' z = ' + line(chk_list) + '\ns.t.\n'

        return target() + '\n'.join(expr(r) for r in\
                range(self.mat.rows())) + '\n    all xi >= 0'

    __repr__ = __str__

if __name__ == '__main__':
    import doctest
    doctest.testmod()
