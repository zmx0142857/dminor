"""
Deal with matrix, of course.
"""

__author__ = 'Clarence'

from rational import Rat

class Mat(object):
    """
    Doctest:

    >>> m = Mat('''
    ... 3.1 -0.4 1/3 0
    ... 3 5/2
    ... 2 0.3 -1''')
    >>> m
    31/10  -2/5   1/3     0
        3   5/2     0     0
        2  3/10    -1     0
    >>> m.size()
    (3, 4)
    >>> m[0][1]
    -2/5
    >>> m[0][1] += Rat('0.6')
    >>> m(1, 2)
    1/5
    >>> -1 in m
    True

    >>> m = Mat('')
    >>> m
    <empty matrix>
    >>> m.size()
    (0, 0)

    >>> m = E(2)
    >>> n = Mat('0.5\\n0.4', cols=2)
    >>> m + n
    3/2   0
    2/5   1
    >>> m
    1 0
    0 1

    >>> m = Mat(lambda i,j: 2*i+j+1, 3, 2)
    >>> m
    1 2
    3 4
    5 6
    >>> m.trans()
    1 3 5
    2 4 6
    >>> n = diag(2, 0.5, rows=2)
    >>> m*n
     2  1
     6  2
    10  3
    >>> m
    1 2
    3 4
    5 6
    >>> n
      2   0
      0 1/2

    >>> m.resize(3,3)
    >>> m
    1 2 0
    3 4 0
    5 6 0
    >>> m.resize(2,2)
    >>> m
    1 2 0
    3 4 0
    5 6 0
    >>> m.resize(2,2,trunc=True)
    >>> m
    1 2
    3 4

    >>> m == Mat(lambda i,j: 2*i+j+1, 2, 2)
    True

    >>> m.pr(row = 0, k = 0.5)
    1/2   1
      3   4
    >>> m.pr(row = 0, row2 = 1)
      3   4
    1/2   1
    >>> m.pr(row = 0, row2 = 1, k = -2)
      2   2
    1/2   1
    >>> m.pc(col = 1, k = 0.5)
      2   1
    1/2 1/2
    >>> m.pc(col = 1, col2 = 0)
      1   2
    1/2 1/2
    >>> m.pc(col = 1, col2 = 0, k = 1.5)
      1 7/2
    1/2 5/4

    >>> diag(1,2,3,rows=4,cols=5)
    1 0 0 0 0
    0 2 0 0 0
    0 0 3 0 0
    0 0 0 1 0
    >>> diag(1,2,3,rows=4,cols=5,loop=False)
    1 0 0 0 0
    0 2 0 0 0
    0 0 3 0 0
    0 0 0 0 0

    >>> det(diag(3, rows=4, fill=1))
    48
    >>> det(Mat('''
    ... 246 427 327
    ... 1014 543 443
    ... -342 721 621'''))
    -29400000
    >>> det(Mat('''
    ... 1 2 3 4
    ... 2 3 4 1
    ... 3 4 1 2
    ... 4 1 2 3'''))
    160

    >>> Mat('''
    ... 4 -2 1
    ... 1 2 -2
    ... -1 8 -7
    ... 2 14 -13''').rank()
    2

    >>> Mat('''
    ... 1 -1 1 -1 1
    ... 1 -1 -1 1
    ... 1 -1 -2 2 -1/2''').solve()
      T1   T2   X0
       0    1  1/2
       0    1    0
       1    0    0
       1    0 -1/2
    >>> Mat('''
    ... 1 2 0 -3 2 1
    ... 1 -1 -3 1 -3 2
    ... 2 -3 4 -5 2 7
    ... 9 -9 6 -16 2 25''').solve()
    'No solution!'

    >>> inv(Mat('''
    ... 3 -4 5
    ... 2 -3 1
    ... 3 -5 -1'''))
     -8  29 -11
     -5  18  -7
      1  -3   1
    """
    def __init__(self, init, rows=0, cols=0, title=()):

        self._data = []
        self._title = title

        if isinstance(init, Mat):
            for i in range(init.rows()):
                self._data.append([])
                for j in range(init.cols()):
                    self._data[i].append(init[i][j])

        elif isinstance(init, list):
            if init == []:
                self._data = [[]]
            elif isinstance(init[0], list):
                self._data = init
            else:
                raise TypeError('If init is a list, it has to '
                                'be a list of list.')

        elif isinstance(init, str):

            init = init.strip()

            # also: self._data = [ [Rat(elem) for elem in row.split()] for row in init.split('\n')]
            # >>> ''.split('\n')
            # ['']
            # >>> ''.split()
            # []
            for row_str in init.split('\n'):
                row = []
                for elem_str in row_str.split():
                    row.append(Rat(elem_str))
                cols = max(cols, len(row))
                self._data.append(row)

        elif callable(init):

            for i in range(rows):
                self._data.append([])
                for j in range(cols):
                    self._data[i].append(Rat(init(i, j)))

        self.resize(rows, cols)

    # specials-------------------------------------------------

    def __str__(self):
        if self.is_empty():
            return '<empty matrix>'

        width = max( max((len(str(elem)) for elem in row))  for row in self._data)
        content = '\n'.join((' '.join(( str(elem).rjust(width) for elem in row)) for row in self._data))
        if self._title == ():
            return content
        else:
            title = ' '.join((t.rjust(width) for t in self._title)) + '\n'
            return title + content

    __repr__ = __str__

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __call__(self, *args):
        """
        It's a bit like __getitem__, but index starts from 1.
        """
        argc = len(args)
        if argc == 1:
            return self._data[args[0]-1]
        elif argc == 2:
            return self._data[args[0]-1][args[1]-1]
        else:
            raise TypeError('Mat.__call__() takes 1 or 2 '
                            'arguments, %d given.' % argc)

    def __contains__(self, key):
        for row in self._data:
            if key in row:
                return True
        return False

    def __eq__(self, other):
        try:
            other = Mat(other)
        except Exception:
            return False

        if self.size() != other.size():
            return False

        for i in range(self.rows()):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        if self.size() != other.size():
            raise ValueError('Matrixes for adding must have '
                             'same size.')

        return Mat(lambda i,j: self[i][j] + other[i][j], self.rows(), self.cols())

    def __mul__(self, other):
        if self.cols() != other.rows():
            raise ValueError('cols of the first Mat must '
                             'equals to rows of the second '
                             'Mat when doing mul.')

        return Mat(lambda i,j: sum(self[i][k] * other[k][j] for k in range(self.cols())), self.rows(), other.cols())

    def __floordiv__(self, other):
        """
        Returns other**(-1) * self
        """
        return self._mul_inv(other, left=True)

    def __truediv__(self, other):
        """
        Returns self * other**(-1)
        """
        return self._mul_inv(other, left=False)

    def __pow__(self, other):
        """
        Returns self**other, calculates inverse of matrix if
        other < 0
        """
        if not self.is_square():
            raise ValueError('Expecting a square matrix.')
        if not isinstance(other, int):
            raise NotImplementedError

        ret = E(self.rows())
        if other == 0:
            return ret
        elif other == 1:
            return self
        elif other == -1:
            return ret // self
        elif other < 0:
            m = ret // self
            other = -other
        elif other > 0:
            m = Mat(self)

        while other != 0:
            ret *= m
            other -= 1

        return ret

# Other Methods------------------------------------------------

    def is_empty(self):
        """
        -> bool

        Returns True if self is empty.
        """
        return self._data == [[]]

    def size(self, index = None):
        """
        -> (int, int)

        Returns rows and cols of self.
        """
        tup = (0, 0) if self.is_empty() else (len(self._data), len(self._data[0]))
        if index == None:
            return tup
        elif index == 0 or index == 1:
            return tup[index]
        else:
            raise ValueError('Index for method m.size() must '
                             'be 0 or 1.')

    def rows(self):
        """
        -> int

        Returns the number of rows in self.
        """
        return self.size(0)

    def cols(self):
        """
        -> int

        Returns the number of columns in self.
        """
        return self.size(1)

    def is_square(self):
        """
        -> bool

        Returns True if self is square matrix.
        """
        return self.rows() == self.cols()

    def resize(self, rows, cols, trunc = False):
        """
        -> None

        Resize self, truncate it if trunc == True.
        """
        while self.rows() < rows:
            self._data.append([])

        for row in self._data:
            while len(row) < cols:
                row.append(Rat(0))

        if trunc:
            while self.rows() > rows:
                self._data.pop()
            for row in self._data:
                while len(row) > cols:
                    row.pop()

    def copy(self):
        """
        -> Mat

        Returns copy of self.
        """
        return Mat(self)

    def trans(self):
        """
        -> Mat

        Returns the transpose of self.
        """
        return Mat(lambda i,j: self[j][i], self.cols(), self.rows())

    def tr(self):
        """
        -> Rat

        Returns trace of self, self should be square.
        """
        if not self.is_square():
            raise ValueError('Expecting a square matrix.')

        return sum(self[i][i] for i in range(self.rows()))

    def det(self):
        """
        -> Rat

        Returns determinant of self, self should be square.
        """
        if not self.is_square():
            raise ValueError('Expecting a square matrix.')

        # det can be changed by _simplify
        return Mat(self)._simplify( det = [Rat(1)] )

    def inv(self):
        """
        -> Mat

        Returns inverse of self, self should be square.
        """
        return E(self.rows()) // self

    def check(self, func, r_range=None, c_range=None):
        """
        -> bool

        Returns true if for all r, c in r_range and c_range
        (they are sequeneces), self[r][c] == func(r, c).
        """
        if r_range == None:
            r_range = range(self.rows())
        if c_range == None:
            c_range = range(self.cols())
        for r in r_range:
            for c in c_range:
                if self[r][c] != func(r, c):
                    return False
        return True

    def pr(self, *, row, row2=None, k=None):
        """
        -> self

        Primary row transform on self. The form of transform
        depends on the arguments given. row and row2 start from 0.
        """
        if row2 == None and k == None:
            raise ValueError("At least one of 'row2' and 'k' "
                             "is required.")

        # pr1: row *= k
        elif row2 == None: # k != None
            self[row] = [elem * k for elem in self[row]]

        # pr3: swap row, row2
        elif k == None: # row2 != None
            if row == row2:
                return self
            tmp = self[row]
            self[row] = self[row2]
            self[row2] = tmp

        # pr2: row += row2 * k
        else: # row2, k != None
            for col in range(self.cols()):
                self[row][col] += self[row2][col] * k

        # print(self, '\n')
        return self

    def pc(self, *, col, col2=None, k=None):
        """
        -> self

        Primary column transform on self. The form of transform
        depends on the arguments given. col and col2 start from 0.
        """
        if col2 == None and k == None:
            raise ValueError("At least one of 'col2' and 'k' "
                             "is required.")

        # pc1: col *= k
        elif col2 == None: # k != None
            for row in range(self.rows()):
                self[row][col] *= k

        # pc3: swap col, col2
        elif k == None: # col2 != None
            if col == col2:
                return self
            for row in range(self.rows()):
                tmp = self[row][col]
                self[row][col] = self[row][col2]
                self[row][col2] = tmp

        # pc2: col += col2 * k
        else: # col2, k != None
            for row in range(self.rows()):
                self[row][col] += self[row][col2] * k

        # print(self, '\n')
        return self

    def p(self, *, pr, ix, ix2=None, k=None):
        """
        -> self

        Do self.pr() if pr == True; else do self.pc().
        """
        if pr == True:
            return self.pr(row=ix, row2=ix2, k=k)
        else:
            return self.pc(col=ix, col2=ix2, k=k)

    def _target(self, col):
        """
        Help to find proper target row for number 1.
        """
        target = col
        while target != 0:
            for c in range(0, col):
                if self[target-1][c] != 0:
                    return target
            target -= 1
        return target

    def _p3(self, col, det, target):
        """
        Search for 1 or -1 and swap it to desired position.
        Returns True if success.
        """
        for row in range(target, self.rows()):

            if self[row][col] == 1:
                if row != target:
                    self.pr(row = row, row2 = target)
                    if det != None:
                        det[0] = -det[0]
                return True

            elif self[row][col] == -1:
                self.pr(row = row, k = -1)
                self.pr(row = row, row2 = target)
                if det != None and row == target:
                    det[0] = -det[0]
                return True

        return False

    def _p2(self, col, target):
        """
        Generate number 1 by adding/subtracting.
        Returns True if success.
        """
        for row in range(target, self.rows()):
            for find in range(target, self.rows()):
                if find == row:
                    continue
                for k in (1, -1):
                    if abs(self[row][col] + k * self[find][col]) == 1:
                        self.pr(row = row, row2 = find, k = k)
                        return True
        return False

    def _p1(self, col, det, target):
        """
        Generate number 1 by division.
        Returns True if success.
        """
        for row in range(target, self.rows()):
            tmp = self[row][col]
            if tmp != 0:
                self.pr(row = row, k = 1 / tmp)
                if det != None:
                    det[0] *= tmp
                return True
        return False

    def _swap_col(self, col, target, vars):
        """
        When current column has only 0 for row >= target, we
        need to _swap_col.
        Returns True if success.
        """
        for c in range(self.cols()-2, col, -1):
            for r in range(target, self.rows()):
                if self[r][c] != 0:
                    # we don't care that this changes det
                    self.pc(col = col, col2 = c)
                    # but this matters when solving system
                    if vars != None:
                        vars[col], vars[c] = vars[c], vars[col]
                    return True
        return False

    def _simplify(self, *, det=None, rowsimp=False, vars=None, inv=False):
        """
        Help to simplify the matrix (what great help!).
        """
        col = 0
        while col != min(self.rows(), self.cols()):
            target = self._target(col)

            if self._p3(col, det, target):
                pass
            elif self._p2(col, target):
                self._p3(col, det, target)
            elif self._p1(col, det, target):
                self._p3(col, det, target)

            # so there are only 0 below target in this column!
            elif det != None:
                return Rat(0)
            elif inv == True:
                raise ValueError('This matrix is '
                                 'irreversible!')
            elif self.cols() >= 2:
                if not self._swap_col(col, target, vars):
                    col += 1
                continue

            # for all rows below: goto 0!
            for row in range(target+1, self.rows()):
                self.pr(row = row, row2 = target, k = -self[row][col])

            col += 1

        if rowsimp == True:
            # reverse iter:
            for col in range(min(self.cols(), self.rows())-1, -1, -1):
                if self[col][col] == 0:
                    continue
                # for all rows above: goto 0!
                for row in range(0, col):
                    self.pr(row = row, row2 = col, k = -self[row][col])

        if det != None:
            return det[0]

    def to_stair(self):
        """
        -> self

        Transfrom self to a stair-like matrix.
        """
        self._simplify()
        return self


    def to_rowsimp(self):
        """
        -> self

        Transfrom self to a row-simplified stair-like matrix.
        """
        self._simplify(rowsimp=True)
        return self

    def rank(self, simplified=False, with_last_col=True):
        """
        -> int

        Returns rank of self. Skip self.to_stair() if
        simplified == True. Returns rank of self without last column if with_last_col == False.
        """
        m = Mat(self) if simplified else Mat(self).to_stair()
        col = m.cols()
        if not with_last_col:
            col -= 1

        # note that r will never == m.rows() so I returned r+1.
        for r in range(m.rows()):
            all_zero = True
            for c in range(r, col):
                if m[r][c] != 0:
                    all_zero = False
                    break
            if all_zero:
                return r
        return r+1

    def solve(self):
        """
        -> Mat or str

        Solve the system, save the result k1T1 +...+ knTn + X0
        as Mat, where T1, ..., Tn, X0 are the columns, return
        a str if the system can't be solved.
        """
        m = Mat(self)
        vars = [x for x in range(m.cols()-1)]
        m._simplify(rowsimp=True, vars=vars)

        if m.rank(simplified=True, with_last_col=False) != m.rank(simplified=True, with_last_col=True):
            return 'No solution!'

        r = 0
        while r != min(m.rows(), m.cols()):
            if m[r][r] == 0:
                break
            r += 1

        def _solve_func(i, j):
            if vars[i] < r:
                if r + j < m.cols():
                    ret = m[vars[i]][r+j]
                    return ret if r + j == m.cols()-1 else -ret
            else:
                return 1 if vars[i] == r+j and r+j != m.cols()-1 else 0

        title = tuple( 'T%d' % x for x in range(1, m.cols()-r) ) + ('X0',)
        return Mat(_solve_func, m.cols()-1, m.cols()-r, title=title)

    def _mul_inv(self, other, left=True):
        """
        -> Mat

        Help to do mat division. Returns other**(-1) * self if
        left == True; else returns self * other**(-1).
        """
        if not other.is_square:
            raise ValueError('The second Matrix must be '
                             'square.')
        if left:
            if self.rows() != other.rows():
                raise ValueError('They should have the same rows.')
            ret = Mat(lambda i,j: other[i][j] if j < other.cols() else self[i][j-other.cols()], other.rows(), other.cols()+self.cols())
        else:
            if self.cols() != other.cols():
                raise ValueError('They should have the same cols.')
            ret = Mat(lambda j,i: other[i][j] if i < other.rows() else self[i-other.rows()][j], other.cols(), other.rows()+self.rows())

        ret._simplify(rowsimp=True, inv=True)

        if left:
            return Mat(lambda i,j: ret[i][j+other.cols()], self.rows(), self.cols())
        else:
            return Mat(lambda j,i: ret[i][j+other.rows()], self.rows(), self.cols())


# class ends---------------------------------------------------

def diag(*values, rows=None, cols=None, loop=True, fill=0):
    """
    -> Mat

    Returns a diagonal matrix with its main diagonal filled
    with 'values'. The values loop if loop == True, otherwise
    fill them with 'fill', which by default is 0.
    """
    sz = len(values)
    if rows == None:
        rows = sz
    if cols == None:
        cols = rows

    if loop:
        return Mat(lambda i,j: values[i % sz] if i == j else fill, rows, cols)
    else:
        return Mat(lambda i,j: values[i] if i == j and i<sz else fill, rows, cols)

def O(rows, cols = None, fill = 0):
    """
    -> Mat

    Returns a matrix filled with 'fill', which by default is 0.
    """
    if cols == None:
        cols = rows
    return Mat(lambda i,j: 0, rows, cols)

def E(size):
    """
    -> Mat

    Returns a unit matrix.
    """
    return diag(1, rows = size)

def trans(mat):
    """
    -> Mat

    Returns the transpose of mat.
    """
    return mat.trans()

def tr(mat):
    """
    -> Rat

    Returns trace of mat, mat should be square.
    """
    return mat.tr()

def det(mat):
    """
    -> Rat

    Returns determinant of mat, mat should be square.
    """
    return mat.det()

def inv(mat):
    """
    -> Mat

    Returns inverse of mat, mat should be square.
    """
    return mat.inv()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
