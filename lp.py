#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Linear Programming"""

__author__ = 'Clarence Zhuo'

import matrix, rational

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
    
    >>> mat = matrix.Mat('''
    ... 1 4 2 8
    ... 3 2 0 6''')
    >>> chk = [2, 3, 1]
    >>> rel = [ge, ge]
    >>> lp = LP(mat, chk, maximum=False, relation=rel)
    >>> lp.solve()
    ('best solution', [4/5, 9/5, 0, 0, 0], 7)
    """
    def __init__(self, mat, chk_list, base=None, maximum=True,\
            relation=None):
        """
        LP(Mat, check_list, base_index) -> LP object

        mat := [A, b] is the argumented matrix for a standardized LP problem
        base is indeces of base vectors
        artificial is the column number of the first artificial variable
        chk_list is a list of checking numbers for each variable x_i
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
        self.chk_list = list(chk_list)
        # make chk_list has same columns as mat by appending zeros
        matrix.resize(self.chk_list, self.mat.cols())
        self.relation = relation if relation != None\
                else [eq for col in self.mat]
        matrix.resize(self.relation, self.mat.rows(), fill=eq)

    # adding artificial variables
    def art(self):
        rows = self.mat.rows()
        for i, rel in enumerate(self.relation):
            if rel == le:
                # add loose variable
                # matrix.e is unit vector with ith element == 1
                self.mat.insert(matrix.e(rows, i), col=self.artificial)
                self.chk_list.append(0)
                self.base.append(self.artificial)
                self.artificial += 1
            elif rel == eq:
                # add artificial variable
                # insert before last column
                self.mat.insert(matrix.e(rows, i), col=-1)
            elif rel == ge:
                # subtract remaining variable,
                # add artificial variable
                self.mat.insert(((rational.Rat(-1) if i == j else\
                    rational.Rat(0)) for j in range(rows)),\
                    col=self.artificial)
                self.chk_list.append(0)
                self.artificial += 1
                self.mat.insert(matrix.e(rows, i), col=-1)
        self.base.extend(range(self.artificial, self.mat.cols()-1))

    def compute_theta(self, col):
        min_theta = 0
        ret = None
        # after appending chk_list to mat, rows has increased by 1
        for row in range(self.mat.rows()-1):
            if self.mat[row][col] == 0:
                continue
            theta = self.mat[row][-1] / self.mat[row][col]
            if theta > 0 and (min_theta == 0 or theta < min_theta):
                min_theta = theta
                ret = row
        return ret

    def two_step(self, verbose=False):
        chk_list = [(0 if i < self.artificial else 1)\
                for i in range(self.mat.cols()-1)]
        lp = LP(self.mat, chk_list, self.base, maximum=False) 
        result = lp.solve(verbose)

        if verbose:
            print('after first step:\n%s' % self.mat)
            print('base: %s' % self.base)

        # no solution
        if not isinstance(result, tuple) or result[2] != 0:
            return False

        while self.artificial < self.mat.cols() - 1:
            self.mat.pop(col=-2)

        return True

    def solve(self, verbose=False):

        status_str = ['processing', 'no solution', 'best solution',\
                'unbounded solution']
        status = 0

        if verbose:
            print('solving lp:\n%s' % self)
        if self.base == []:
            self.art()
        if verbose:
            print('base: %s' % self.base)

        # append check list
        # use two-step method if artificial variable exists
        if self.artificial < self.mat.cols() - 1:
            if not self.two_step(verbose):
                return status_str[1]
            # replace last line with self.chk_list
            self.mat[-1] = self.chk_list
        else:
            self.mat._data.append(self.chk_list)
        if verbose:
            print('check list appended:\n%s' % self.mat)

        # use primary transform on check numbers
        for r, col in enumerate(self.base):
            chk = self.mat[-1][col]
            if chk != 0:
                self.mat.pr(row = -1, row2 = r, k = -chk)
        if verbose:
            print('check list processed:\n%s' % self.mat)

        # main loop
        while status == 0:
            status = 2
            if self.maximum:
                cond = lambda x: x <= 0
            else:
                cond = lambda x: x >= 0
            for col in range(self.mat.cols()-1):
                if col in self.base or cond(self.mat[-1][col]):
                    continue

                # positive check number for non-base variable found
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

            # no positive check number means best solution obtained
            if status == 2:
                x = [0 for i in range(self.mat.cols()-1)]
                for i, b in enumerate(self.base):
                    # non-zero artificial variable exist in base
                    if b >= self.artificial and self.mat[i][-1] != 0:
                        return status_str[1]
                    x[b] = self.mat[i][-1]
                return status_str[2], x, -self.mat[-1][-1]

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
                print("after iteration:\n%s" % self.mat)
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
            else:
                m = 'min'
            return m + ' z = ' + line(self.chk_list) + '\ns.t.\n'

        return target() + '\n'.join(expr(r) for r in\
                range(self.mat.rows())) + '\n    all xi >= 0'

    __repr__ = __str__

if __name__ == '__main__':
    import doctest
    doctest.testmod()
