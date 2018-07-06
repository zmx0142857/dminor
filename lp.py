#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Linear Programming"""

__author__ = 'Clarence Zhuo'

import matrix, rational

le, eq, ge = -1, 0, 1

class LP(object):
    """
    Doctest:
    >>> mat = matrix.rMat('''
    ... 1 2 1 0 0 8
    ... 4 0 0 1 0 16
    ... 0 4 0 0 1 12''')
    >>> chk = [2, 3, 0, 0, 0]
    >>> base = [2, 3, 4]
    >>> lp = LP(mat, chk, base)
    >>> lp.solve()
    ('optimal solution', [4, 2, 0, 0, 4], 14)
    >>> base
    [1, 0, 4]
    >>> chk
    [2, 3, 0, 0, 0]

    >>> mat = matrix.rMat('''
    ... 1 -2 1 1 0 0 0 11
    ... -4 1 2 0 -1 1 0 3
    ... -2 0 1 0 0 0 1 1''')
    >>> chk = [0, 0, 0, 0, 0, 1, 1]
    >>> base = [3, 5, 6]
    >>> lp = LP(mat, chk, base, maximum=False)
    >>> lp.solve()
    ('optimal solution', [0, 1, 1, 12, 0, 0, 0], 0)

    >>> mat = matrix.rMat('''
    ... 1 -2 1 11
    ... -4 1 2 3
    ... -2 0 1 1''')
    >>> chk = [-3, 1, 1]
    >>> rel = [le, ge, eq]
    >>> lp = LP(mat, chk, maximum=False, relation=rel)
    >>> lp
    min -3x0 + x1 + x2
    s.t.
        x0 - 2x1 + x2 <= 11
        -4x0 + x1 + 2x2 >= 3
        -2x0 + x2 = 1
        all xi >= 0
    >>> lp.solve()
    ('optimal solution', [4, 1, 9, 0, 0], -2)

    >>> mat = matrix.rMat('''
    ... 1 4 2 8
    ... 3 2 0 6''')
    >>> chk = [2, 3, 1]
    >>> rel = [ge, ge]
    >>> lp = LP(mat, chk, maximum=False, relation=rel)
    >>> lp.solve()
    ('optimal solution', [4/5, 9/5, 0, 0, 0], 7)

    >>> # will this loop?
    >>> mat = matrix.rMat('''
    ... 1 0 0 1/4 -8 -1 9 0
    ... 0 1 0 1/2 -12 -1/2 3 0
    ... 0 0 1 0 0 1 0 1''')
    >>> chk = [0, 0, 0, 0.75, -20, 0.5, -6]
    >>> base = [0, 1, 2]
    >>> lp = LP(mat, chk, base)
    >>> lp.solve()
    ('optimal solution', [3/4, 0, 0, 1, 0, 1, 0], 5/4)
    """
    def __init__(self, mat, chk_list, base=None, maximum=True,\
            relation=None):
        """
        LP(Mat, check_list, base_index) -> LP object

        mat := [A, b] is the argumented matrix for a standardized LP problem
        base is indeces of base variables
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
        self.base = base
        self.artificial = self.mat.cols()-1
        self.maximum = maximum
        self.chk_list = list(chk_list)
        # make chk_list has same columns as mat by appending zeros
        matrix.resize(self.chk_list, self.mat.cols())
        self.relation = list(relation) if relation != None\
                else [eq for row in self.mat]
        matrix.resize(self.relation, self.mat.rows(), fill=eq)

    # adding artificial variables
    def art(self):
        self.base = []
        rows = self.mat.rows()
        for i, rel in enumerate(self.relation):
            if rel == le:
                # add slack variable
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
                self.mat.insert(((self.mat.field(-1) if i == j else\
                    self.mat.field(0)) for j in range(rows)),\
                    col=self.artificial)
                self.chk_list.append(0)
                self.artificial += 1
                self.mat.insert(matrix.e(rows, i), col=-1)
        self.base.extend(range(self.artificial, self.mat.cols()-1))

    def exist_art(self):
        return self.artificial < self.mat.cols() - 1

    def compute_theta(self, col):
        min_theta = None
        ret = None
        # after appending chk_list to mat, rows has increased by 1
        for row in range(self.mat.rows()-1):
            if self.mat[row][col] <= 0:
                continue
            theta = self.mat[row][-1] / self.mat[row][col]
            if min_theta == None or theta < min_theta or (theta ==\
                    min_theta and self.base[row] < self.base[ret]):
                min_theta = theta
                ret = row
        return ret

    def two_step(self, verbose=False):
        chk_list = [0 for i in range(self.artificial)]\
                + [1 for i in range(self.artificial, self.mat.cols()-1)]
        lp = LP(self.mat, chk_list, self.base, maximum=False) 

        if verbose:
            print('step 1:')
        result = lp.solve(verbose)

        # no solution
        if not isinstance(result, tuple) or result[2] != 0:
            return False

        while self.exist_art():
            self.mat.pop(col=-2)

        return True

    def solve(self, verbose=False):

        from rational import choose
        processing = 0
        no_solution = 1
        optimal_solution = 2
        unbounded_solution = 3

        if self.base == None:
            self.art()
        if verbose:
            print('solving lp:\n%s' % self)
            print('base: %s' % self.base)

        # append check list
        # use two-step method if artificial variable exists
        if self.exist_art():
            if not self.two_step(verbose):
                return 'no solution'
            if verbose:
                print('step 2:')
            # replace last line with self.chk_list
            self.mat[-1] = self.chk_list
        else:
            self.mat._data.append(self.chk_list)
        if verbose:
            print('check list appended:\n%s' % self.mat)

        # use primary transform on check numbers
        for r, col in enumerate(self.base):
            if self.mat[-1][col] != 0:
                self.mat.eliminate(r, col, range(-1, 0))
        if verbose:
            print('check list processed:\n%s' % self.mat)

        # main loop
        cnt = 0
        max_iter = choose(self.mat.cols()-1, self.mat.rows()-1)
        cond = (lambda x: x <= 0) if self.maximum else (lambda x: x >= 0)
        status = processing
        
        while status == processing:
            status = optimal_solution
            for col in range(self.mat.cols()-1):
                if col in self.base or cond(self.mat[-1][col]):
                    continue

                # positive check number for non-base variable found
                swap_in = col
                swap_out = self.compute_theta(col)

                # this happens when there's no non-negative theta, or the
                # denominator == 0 when computing theta
                if swap_out == None:
                    status = unbounded_solution
                    continue
                else:
                    status = processing
                    break

            # no positive check number means optimal solution obtained
            if status == optimal_solution:
                x = [0 for i in range(self.mat.cols()-1)]
                for i, b in enumerate(self.base):
                    # non-zero artificial variable exist in base
                    if b >= self.artificial and self.mat[i][-1] != 0:
                        return 'no solution'
                    x[b] = self.mat[i][-1]
                return 'optimal solution', x, -self.mat[-1][-1]

            # swap_out == None for each col with chk_number > 0
            elif status == unbounded_solution:
                return 'unbounded solution'

            # now that status == processing, the iteration have to continue
            self.mat.eliminate(swap_out, swap_in, range(swap_out))
            self.mat.eliminate(swap_out, swap_in, range(swap_out+1,\
                self.mat.rows()))

            # update base, cnt
            self.base[swap_out] = swap_in
            cnt += 1
            if cnt > max_iter:
                return 'stopped on reaching max_iter'

            if verbose:
                print('iteration #%d:\n%s' % (cnt, self.mat))
                print('base: %s' % self.base)

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
            ret = []
            first_item = True
            for i in range(len(row)-1):
                # skip zero
                if row[i] == 0:
                    continue
                # sign
                if first_item:
                    ret.append('-' if row[i] < 0 else '')
                    first_item = False
                else:
                    ret.append(' - ' if row[i] < 0 else ' + ')
                # coefficient
                abs_coef = abs(row[i])
                if abs_coef != 1:
                    ret.append(str(abs_coef))
                # symbol
                ret.append('x' + str(i))
            return ''.join(ret)

        return ('max ' if self.maximum else 'min ')\
                + line(self.chk_list) + '\ns.t.\n'\
                + '\n'.join(expr(r) for r in range(self.mat.rows()))\
                + '\n    all xi >= 0'

    __repr__ = __str__

if __name__ == '__main__':
    import doctest
    doctest.testmod()
