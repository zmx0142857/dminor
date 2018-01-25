#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A Function class representing mathematical functions"""

__author__ = 'Clarence'

import math, basic

class FuncType(object):
    def __init__(self, name, expr, flags):
        self._name = name
        self._expr = expr
        self._flags = flags

    def __eq__(self, other):
        return self._name == other._name and self._flags == other._flags

    def __call__(self, *args):
        if len(args) >= 1 and all(isinstance(arg, Function) for arg in args):
            return Function(self, *args)

    """ ABOUT 'FLAGS'
            argument-count  precedence  associativity   fix-style
    bits:   xx              xxx         x               xx
    note:   0-2             0-7         0 for left      0 for prefix
                                        1 for right     1 for infix
                                                        2 for postfix
                                                        3 for bothside

    * FuncType with flags == 0x138 is an identity function, like x, y, ...
    * FuncType with flags == 0x038 is a const number, like 1, 3.14, ...
    """

def Const(val):
    return FuncType('const', lambda: val, 0x38)

def Identity(s):
    return FuncType(s, None, 0x138)

NEG = FuncType('-', lambda x: -x, 0x58)         # 001011000, 0130
ABS = FuncType('| |', abs, 0x7b)                # 001111011, 0173
ceil = FuncType('|~ ~|', math.ceil, 0x7b)
floor = FuncType('|_ _|', math.floor, 0x7b)
sin = FuncType('sin', math.sin, 0x68)           # 001101000, 0150
cos = FuncType('cos', math.cos, 0x68)
tan = FuncType('tan', math.tan, 0x68)
sinh = FuncType('sinh', math.sinh, 0x68)
cosh = FuncType('cosh', math.cosh, 0x68)
tanh = FuncType('tanh', math.tanh, 0x68)
asin = FuncType('arcsin', math.asin, 0x68)
acos = FuncType('arccos', math.acos, 0x68)
atan = FuncType('arctan', math.atan, 0x68)
asinh = FuncType('arcsinh', math.asinh, 0x68)
acosh = FuncType('arccosh', math.acosh, 0x68)
atanh = FuncType('arctanh', math.atanh, 0x68)
# FAC = FuncType('!', math.factory, 0x72)         # 001110010, 0162
ADD = FuncType(' + ', lambda x, y: x+y, 0x89)   # 010001001, 0211
SUB = FuncType(' - ', lambda x, y: x-y, 0x89)
MUL = FuncType(' * ', lambda x, y: x*y, 0x91)   # 010010001, 0221
DIV = FuncType(' / ', lambda x, y: x/y, 0x91)
LOG = FuncType('log', math.log, 0xa0)           # 010100000, 0240
POW = FuncType('^', lambda x, y: x**y, 0xb5)    # 010110101, 0265

class Function(object):
    """
    Doctest:
    >>> c = Function(3.14)
    >>> c
    3.14
    >>> x, y = var('x', 'y')
    >>> x
    x
    >>> x(42)
    42
    >>> u = atan(x + abs(1+x**2))
    >>> u
    arctan(x + |1 + x^2|)
    >>> z = x**2 + 3 * y + x*y
    >>> z(0.5, 2)
    7.25

    """
    def __init__(self, arg=None, *funcs):

        if len(funcs) == 0:
            if arg == None:
                self._type = Identity('x')
            elif isinstance(arg, str):
                self._type = Identity(arg)
            else:
                self._type = Const(arg)
        else:
            self._type = arg

        self._funcs = tuple(f if isinstance(f, Function) else Function(f)\
                for f in funcs)

    def name(self):
        return self._type._name

    def argc(self):
        """Returns the number of the arguments"""
        return (self._type._flags >> 6 ) & 3
    
    def prec(self):
        """Returns the precedence, ranging 0-7"""
        return (self._type._flags >> 3) & 7

    def assoc(self):
        """Returns the associativity, 0 is left, 1 is right"""
        return (self._type._flags >> 2) & 1

    def fix(self):
        """Returns the fix-style, 0 is prefix, 1 is infix, 2 is postfix"""
        return self._type._flags & 0x3

    def is_const(self):
        return self._type._flags == 0x38

    def is_identity(self):
        return self._type._flags == 0x138

    def __str__(self):

        def put(content, condition):
            return '(' + str(content) + ')' if condition else str(content)

        if self.is_identity():
            return self.name()
        elif self.is_const():
            return str(self())

        f1 = self._funcs[0]
        if self.argc() == 1: 
            cond = self.fix() != 3 and (\
                        (f1.is_const() and f1() < 0)\
                        or f1._type == NEG\
                        or f1.prec() < self.prec()\
                    )
        
            if self.fix() == 0: # pre-fix
                return self.name() + put(f1, cond)
            elif self.fix() == 2: # post-fix
                return put(f1, cond) + self.name()
            elif self.fix() == 3: # both-side
                return put(f1, cond).join(self.name().split())
            else:
                raise ValueError("unary function '%s' has infix property!"
                        % self.name())

        else: # self.argc() == 2:
            f2 = self._funcs[1]
            cond1 = f1.prec() <= self.prec()
            cond2 = (f2.is_const() and f2() < 0)\
                    or f2._type == NEG\
                    or f2.prec() <= self.prec()

            if self.fix() == 0: # pre-fix
                return self.name() + '(' + put(f1, cond1) + ' '\
                        + put(f2, cond2) + ')'
            elif self.fix() == 1: # in-fix
                return put(f1, cond1) + self.name() + put(f2, cond2)
            else: # post-fix
                return '(' + put(f1, cond1) + ' ' + put(f2, cond2) + ')'\
                        + self.name()

    __repr__ = __str__

    def __call__(self, *args, **kw):

        cnt = [0]
        def build_dict(self):
            if self.is_identity():
                if not self.name() in kw:
                    if (cnt[0] < len(args)):
                        kw[self.name()] = args[cnt[0]]
                        cnt[0] += 1
                    else:
                        raise SyntaxError("too few arguments for '%s'"\
                                % self.name())
            if self.argc() >= 1:
                build_dict(self._funcs[0])
            if self.argc() >= 2:
                build_dict(self._funcs[1])

        def value(self):
            if self.is_const():
                return self._type._expr()
            elif self.is_identity():
                if self.name() in kw:
                    return kw[self.name()]
                else:
                    raise ValueError("'%s' needs a value!" % self.name())
            return self._type._expr(*(value(f) for f in self._funcs))

        build_dict(self)
        return value(self)

    def __pos__(self):
        return self

    def __neg__(self):
        return NEG(self)

    def __abs__(self):
        return ABS(self)

    def __add__(self, other):
        return ADD(self, other)

    def __radd__(self, other):
        return Function(ADD, other, self)

    def __sub__(self, other):
        return Function(SUB, self, other)

    def __rsub__(self, other):
        return Function(SUB, other, self)

    def __mul__(self, other):
        return Function(MUL, self, other)

    def __rmul__(self, other):
        return Function(MUL, other, self)

    def __truediv__(self, other):
        return Function(DIV, self, other)

    def __rtruediv__(self, other):
        return Function(DIV, other, self)

    def __pow__(self, other):
        return Function(POW, self, other)

    def __rpow__(self, other):
        return Function(POW, other, self)

def var(*args):
    if all(isinstance(s, str) for s in args):
        return tuple(Function(s) for s in args)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
