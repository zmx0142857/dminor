#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A Function class representing mathematical functions"""
"""
Operator precedence in python and 'function.py':

0. lambda                       if - else
1. expr1 if cond else expr2     or
2. or                           and
3. and                          not
4. not                          in, not in, is, is not,
                                <, <=, >, >=, !=, ==
5. in, not in, is, is not,      |
   <, <=, >, >=, !=, ==
6. |                            ^
7. ^                            &
8. &                            << >>
9. << >>                        binary + -
10. binary + -                  * @ / // %
11. * @ / // %                  +x, -x, ~x
12. +x, -x, ~x                  sin... atanh, log
13. **                          **, !
14. await                       [], [:], call(), obj.attr
15. [], [:], call(), obj.attr   (), ||, |_ _|, |~ ~|
16. (expr)
"""


__author__ = 'Clarence'

import math, basic

class FuncNode(object):
    def __init__(self, name, expr, flags):
        self._name = name
        self._expr = expr
        self._flags = flags

    def __eq__(self, other):
        return self._name == other._name and self._flags == other._flags

    def __call__(self, *args):
        return Function(self, *args)

    """ ABOUT 'FLAGS'
            argument-count  precedence  associativity   fix-style
    bits:   xx              xxx         x               xx
    note:   0-2             0-7         0 for left      0 for prefix
                                        1 for right     1 for infix
                                                        2 for postfix
                                                        3 for bothside

    * FuncNode with flags == 0x138 is an identity function, like x, y, ...
    * FuncNode with flags == 0x038 is a const number, like 1, 3.14, ...
    """

def Const(val):
    return FuncNode('const', lambda: val, 0x38)

def Identity(s):
    return FuncNode(s, None, 0x138)

NEG   = FuncNode('-',     lambda x: -x,              0x58) # 001011000, 0130
ABS   = FuncNode('| |',   abs,                       0x7b) # 001111011, 0173
ceil  = FuncNode('|~ ~|', math.ceil,                 0x7b)
floor = FuncNode('|_ _|', math.floor,                0x7b)
sin   = FuncNode('sin',   math.sin,                  0x68) # 001101000, 0150
cos   = FuncNode('cos',   math.cos,                  0x68)
tan   = FuncNode('tan',   math.tan,                  0x68)
sinh  = FuncNode('sinh',  math.sinh,                 0x68)
cosh  = FuncNode('cosh',  math.cosh,                 0x68)
tanh  = FuncNode('tanh',  math.tanh,                 0x68)
asin  = FuncNode('asin',  math.asin,                 0x68)
acos  = FuncNode('acos',  math.acos,                 0x68)
atan  = FuncNode('atan',  math.atan,                 0x68)
asinh = FuncNode('asinh', math.asinh,                0x68)
acosh = FuncNode('acosh', math.acosh,                0x68)
atanh = FuncNode('atanh', math.atanh,                0x68)
fac   = FuncNode('!',     lambda n: math.gamma(n+1), 0x72) # 001110010, 0162
ADD   = FuncNode(' + ',   lambda x, y: x+y,          0x89) # 010001001, 0211
SUB   = FuncNode(' - ',   lambda x, y: x-y,          0x89)
MUL   = FuncNode(' * ',   lambda x, y: x*y,          0x91) # 010010001, 0221
DIV   = FuncNode(' / ',   lambda x, y: x/y,          0x91)
LOG   = FuncNode('log',   math.log,                  0xa0) # 010100000, 0240
POW   = FuncNode('^',     lambda x, y: x**y,         0xb5) # 010110101, 0265

class Function(object):
    """
    Doctest:
    >>> Function(3.14)
    3.14
    >>> var()
    x
    >>> var('v')
    v
    >>> x, y = var('x', 'y')
    >>> sin(x)
    sin x
    >>> x(42)
    42
    >>> atan(x + abs(1+x**2))
    atan(x + |1 + x^2|)
    >>> z = x**2 + 3 * y + x*y
    >>> z
    x^2 + 3y + xy
    >>> z(0.5, 2)
    7.25
    >>> y = sin(x)
    >>> y.numint(0, 3.14159)
    1.9999999831300628

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

        def pad(condition):
            return ' ' if condition else ''

        if self.is_identity():
            return self.name()
        elif self.is_const():
            return str(self())

        f1 = self._funcs[0]
        if self.argc() == 1:
            # par: parenthesis
            par = self.fix() != 3 and (\
                        (f1.is_const() and f1() < 0) or f1._type == NEG\
                        or f1.prec() < self.prec()\
                    )
        
            if self.fix() == 0: # pre-fix
                return self.name() + pad(self.name().isalpha() and not par) + put(f1, par)
            elif self.fix() == 2: # post-fix
                return put(f1, par) + self.name()
            elif self.fix() == 3: # both-side
                return put(f1, par).join(self.name().split())
            else:
                raise ValueError("unary function '%s' has infix property!" % self.name())

        elif self.argc() == 2:
            f2 = self._funcs[1]
            par1 = (f1.prec() <= self.prec()) if self.assoc() else (f1.prec() < self.prec())
            par2 = (f2.is_const() and f2() < 0) or f2._type == NEG\
                    or ((f2.prec() < self.prec()) if self.assoc() else (f2.prec() <= self.prec()))

            if self.fix() == 0: # pre-fix
                return self.name() + '(' + put(f1, par1) + ', ' + put(f2, par2) + ')'
            elif self.fix() == 1: # in-fix
                if self._type == MUL: # specials for multiply
                    show_mul_op = f2.is_const()\
                            or f1.is_identity() and len(f1.name()) > 1\
                            or f2.is_identity() and len(f2.name()) > 1
                    if not show_mul_op:
                        return put(f1, par1) + put(f2, par2)
                return put(f1, par1) + self.name() + put(f2, par2)
            else: # post-fix
                return '(' + put(f1, par1) + ', ' + put(f2, par2) + ')' + self.name()
        else:
            return self.name() + '(' + ', '.join(str(self._funcs)) + ')'

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
        return ADD(other, self)

    def __sub__(self, other):
        return SUB(self, other)

    def __rsub__(self, other):
        return SUB(other, self)

    def __mul__(self, other):
        return MUL(self, other)

    def __rmul__(self, other):
        return MUL(other, self)

    def __truediv__(self, other):
        return DIV(self, other)

    def __rtruediv__(self, other):
        return DIV(other, self)

    def __pow__(self, other):
        return POW(self, other)

    def __rpow__(self, other):
        return POW(other, self)

    def numint(self, a, b, partitions=1e4):
        ret = 0
        dx = (b-a) / partitions
        x = a
        while x <= b:
            ret += self(x)
            x += dx
        return ret * dx

def var(*args):
    if all(isinstance(s, str) for s in args):
        if len(args) < 2:
            return Function(*args)
        else:
            return tuple(Function(s) for s in args)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
