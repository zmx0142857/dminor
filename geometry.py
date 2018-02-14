#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Classes for 2d and 3d geometry"""

__author__ = 'Clarence Zhuo'

import math

#typedef Point Vec;

# class Point-----------------------------------------------------------

class Point(object):
    """
    Doctest:
    >>> Point(0, 0, name='Q')   # init by args
    Q = (0, 0)
    >>> p = Point((0, 3, 2))    # init by Iterable
    >>> p
    (0, 3, 2)
    >>> Point(p)                # init by another Point
    (0, 3, 2)
    >>> p.z = 4                 # set/get item with index or x,y,z
    >>> p[2]
    4
    >>> p
    (0, 3, 4)
    >>> p.dim()                 # dimension of p
    3
    >>> p.norm()                # norm of p as a vector
    5.0
    """
    def __init__(self, *args, name=''):
        """
        Point(x1, x2, ...) -> point with x1, x2, ... as its components
        Point(Iterable) -> point construct from Iterable
        Point(Point) -> copy-construct
        """
        from collections import Iterable
        if len(args) == 1:
            if isinstance(args[0], Point):
                self.data = args[0].data.copy()
            elif isinstance(args[0], Iterable):
                self.data = list(args[0])
        else:
            self.data = list(args)
        self.name = name if not name.isspace() else ''

    # getters and setters--------------------------------------

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value
    
    @property
    def x(self):
        return self.data[0]

    @property
    def y(self):
        return self.data[1]

    @property
    def z(self):
        return self.data[2]

    @x.setter
    def x(self, value):
        self.data[0] = value

    @y.setter
    def y(self, value):
        self.data[1] = value

    @z.setter
    def z(self, value):
        self.data[2] = value

    # magic methods---------------------------------------------

    def __str__(self):
        pos = '(' + ', '.join(str(x) for x in self.data) + ')'
        if self.name == '':
            return pos
        else:
            return self.name + ' = ' + pos

    __repr__ = __str__

    def __len__(self):
        return self.dim()

    def __abs__(self):
        return self.norm()

    def __eq__(self, other):
        return isinstance(other, Point) and self.data == other.data

    def __ne__(self, other):
        return not self == other

    def __neg__(self):
        return Point(-x for x in self.data)

    def __add__(self, other):
        if not isinstance(other, Point):
            raise TypeError("unsupported operand type(s) for '+': 'Point' and '%s'" % str(type(other)))
        if self.dim() != other.dim():
            raise ValueError("the dimensions of two points don't match")
        return Point(self[i] + other[i] for i in range(self.dim()))

    def __sub__(self, other):
        if not isinstance(other, Point):
            raise TypeError("unsupported operand type(s) for '-': 'Point' and '%s'" % str(type(other)))
        if self.dim() != other.dim():
            raise ValueError("the dimensions of two points don't match")
        return Point(self[i] - other[i] for i in range(self.dim()))

    def __mul__(self, other):
        """Return inner product or multiplication by scalar"""
        if isinstance(other, Point):
            if self.dim() != other.dim():
                raise ValueError("the dimensions of two points don't match")
            return sum(self[i] * other[i] for i in range(self.dim()))
        return Point(x * other for x in self.data)

    def __rmul__(self, other):
        """Return multiplication by scalar"""
        return Point(x * other for x in self.data)
    
    def __truediv__(self, other):
        """Return self * (1 / other)"""
        return Point(x / other for x in self.data)

    def __pow__(self, other):
        """
        if dim == 2, return bracket multiply:
            | x1 y1 |
            | x2 y2 |
        if dim == 3, return exterior product:
            | i  j  k  |
            | x1 y1 z1 |
            | x2 y2 z2 |
        """
        if not isinstance(other, Point):
            raise TypeError("unsupported operand type(s) for '**': 'Point' and '%s'" % str(type(other)))
        if self.dim() != other.dim():
            raise ValueError("the dimensions of two points don't match")
        if self.dim() == 2:
            return self.x * other.y - self.y * other.x
        elif self.dim() == 3:
            return Point(\
                    Point(self.y, self.z) ** Point(other.y, other.z),\
                    Point(self.z, self.x) ** Point(other.z, other.x),\
                    Point(self.x, self.y) ** Point(other.x, other.y))
        else:
            raise ValueError("'**' expects dimension 2 or 3")
	
    # other methods---------------------------------------------

    def dim(self):
        return len(self.data)

    def norm(self):
        return math.sqrt(self.normsq())

    def normsq(self):
        """Return the square of self.norm()"""
        return sum(x**2 for x in self.data)

    def arg(self, x=None, y=None):
        """
        Return polar coordinate theta for (x,y), 0 <= theta < 2*pi
        Return None if x == 0 and y == 0
        """
        if x == None:
            x = self.x
        if y == None:
            y = self.y
        if x > 0 and y >= 0:    # quadrant I and positive x axis
            return math.atan(y/x)
        elif x < 0:             # quadrant II and III and negative x axis
            return math.atan(y/x) + math.pi
        elif x > 0 and y < 0:   # quadrant IV
            return math.atan(y/x) + 2*math.pi
        elif y > 0:             # positive y axis
            return math.pi / 2
        elif y < 0:             # negative y axis
            return math.pi * 3 / 2

    def rotate(self, theta, point):
        """
        Rotate self by angle theta around point
        Return a rotated copy of self
        """
        r = self - point
        x = r.x * math.cos(theta) - r.y * math.sin(theta)
        y = r.x * math.sin(theta) + r.y * math.cos(theta)
        return Point(point + x, point + y, *self[2:])

    def polar(self):
        """
        p.polar() -> tuple
        Return the polar coordinate
        """
        if self.dim() != 2:
            raise ValueError("p.polar() expects a point of 2 dimensions, %d given" % self.dim())
        return self.norm(), self.arg()
    
    def copy(self):
        """
        Return a copy of this
        """
        return Point(self.data, name=self.name+"'")

# class Line------------------------------------------------------------

class Line(object):
    """
    Doctest:
		std::cout << "\n----Testing struct Line----\n";
		Point p1(4, 1, "P1");
		std::cout << p1 << std::endl;
		Line l1(2, 3, 6, "line1");
		std::cout << l1 << std::endl;
		Line l2(-2, 12, "line2");
		std::cout << l2 << std::endl;
		Line l3(p1, 3, "line3");
		std::cout << l3 << std::endl;
		Point p2(0, 5, "P2");
		std::cout << p2 << std::endl;
		Line l4(p1, p2, "line4");
		std::cout << l4 << std::endl;
		Line l4cpy(l4);
		std::cout << l4cpy << std::endl;
    """
    def __init__(self, a=None, b=None, c=None, *, p=None, q=None, k=None,\
            norm=None, name=''):
        """
        Line(a, b, c) -> general form: ax + by + c
        Line(p, q) -> two-point form: (y-p.y)/(x-p.x) = (q.y-p.y)/(q.x-p.x)
        Line(p, norm) -> point with normal vector
        Line(x0, y0) -> point-slope form: y - p.y = k(x - p.x)
        """
        # general form
        if all(x != None for x in (a, b, c)):
            if a == 0 and b == 0:
                raise ValueError("a, b must not be zero at the same time")
            self.a = a
            self.b = b
            self.c = c

        # two-point form
        elif p != None and q != None:
            self.a = q.y - p.y
            self.b = p.x - q.x
            self.c = q.x * p.y - p.x * q.y

        # point-norm form
        elif p != None and norm != None:
            self.a = norm.y
            self.b = -norm.x
            self.c = norm.x * p.y - p.x * norm.y

        # point-slope form
        elif p != None and k != None:
            self.a = k
            self.b = -1
            self.c = p.y - k * p.x
            if a != None:
                self.a *= a
                self.b *= a
                self.c *= a

        else:
            raise ValueError("failed building Line: not enough arguments")

        self.name = name if not name.isspace() else ''

    def __str__(self):

        def item(coef, sym='', is_first=False):
            ret = ''
            if coef != 0:
                if coef < 0:
                    ret += '- '
                elif not is_first:
                    ret += '+ '
                tmp = abs(coef)
                if tmp != 1 or sym == '':
                    ret += str(tmp)
                ret += sym + ' '
            return ret
                    
        ret = ''
        if self.name != '':
            ret = self.name + ': '

        if self.is_vertical():
            return ret + 'x = %s' % self.x_intercept()
        elif self.is_horizontal():
            return ret + 'y = %s' % self.y_intercept()
        
        ret += item(self.a, 'x', is_first=True)
        ret += item(self.b, 'y')
        ret += item(self.c)
        return ret + '= 0'

    def __call__(self, p):
        if not isinstance(p, Point):
            raise TypeError('line.__call__() expects a point')
        return a * p.x + b * p.y + c

    def __contains__(self, p):
        return self(p) == 0

    # methods-----------------------------------------------------------
	
    def slope(self):
        return -a / b

    def x_intercept(self):
        return -c / a

    def y_intercept(self):
        return -c / b

    def is_horizontal(self):
        return a == 0 and b != 0

    def is_vertical(self):
        return b == 0 and a != 0

    def normal_vector(self):
        return Point(a, b)
	
X_AXIS = Line(0, 1, 0);
Y_AXIS = Line(1, 0, 0);

# non-member functions--------------------------------------------------

def origin(n=2):
    return Point(0 for i in range(n))

def distance(p, q):
    """Return distance between p and q, q can be a Point or a Line"""
    if not isinstance(p, Point):
        raise TypeError("distance() expects 2 Points or a Point and a Line")
    if isinstance(q, Point):
        if p.dim() != q.dim():
            raise ValueError("the dimensions of two points don't match")
        return (p - q).norm()
    elif isinstance(q, Line):
        return abs(L(p)) / L.normal_vector().norm()
    else:
        raise TypeError("distance() expects argument 2 to be a Point or a Line")

def cosia(p, q):
    """Return included angle cosine of Point p and q"""
    if not all(isinstance(x, Point) for x in (p, q)):
        raise TypeError("cosia() expects 2 Points")
    return (p * q) / math.sqrt(p.normsq() * p.normsq())

def ia(p, q):
    """Return included angle of Point p and q, in radians"""
    if all(isinstance(x, Point) for x in (p, q)):
        return math.acos(cosia(p, q))
    elif all(isinstance(x, Line) for x in (p, q)):
        return math.acos(abs(cosia(p.normal_vector(), q.normal_vector())))
    else:
        raise TypeError("ia() expects 2 Points or 2 Lines")
    
def ll(L1, L2):
    """Return True iff two lines are parallel"""
    if not all(isinstance(L, Line) for L in (L1, L2)):
        raise TypeError('ll() expects two lines')
    return L1.normal_vector() ** L2.normal_vector() == 0

def _l_(L1, L2):
    """Return True iff two lines are perpendicular"""
    if not all(isinstance(L, Line) for L in (L1, L2)):
        raise TypeError('_l_() expects two lines')
    return L1.normal_vec() * L2.normal_vec() == 0

if __name__ == '__main__':
    import doctest
    doctest.testmod()
