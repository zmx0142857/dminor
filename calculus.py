#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Functions for numerical integration and differentiation."""

__author__ = 'Clarence Zhuo'

def trapezoid(f, a, b, n):
    """
    int_a^b f(x) dx ~= h/2 * (f(a) + 2 sum_(k=1)^(n-1) f(x_k) + f(b));
    h = (b-a)/n;
    x_k = a + kh.
    """
    h = (b - a) / n
    x = lambda k: a + k * h
    return h / 2 * (f(a) + 2 * sum(f(x(k)) for k in range(1, n)) + f(b))

def simpson(f, a, b, n):
    """
    int_a^b f(x) dx ~= h/6 * (f(a) + 4 sum_(k=0)^(n-1) f(x_(k+1/2)) +
                       2 sum_(k=1)^(n-1) f(x_k) + f(b));
    h = (b-a)/n;
    x_k = a + kh.
    """
    h = (b - a) / (2 * n)
    x = lambda k: a + k * h
    return h / 3 * (f(a) - f(b)\
            + sum(4 * f(x(2*k-1)) + 2 * f(x(2*k)) for k in range(1, n+1)))

def romberg(f, a, b, tol=1e-15):
    """
    compute
    I[0][0]
    I[0][1] I[1][0]
    I[0][2] I[1][1] I[2][0]
    I[0][3] I[1][2] I[2][1] I[3][0]
    ...
    by row, output I[i][1] if |I[i][0] - I[i][1]| < tol.
    """
    n = 1
    h = (b - a)/2
    I = [[ h * (f(a) + f(b)) ]]
    x = lambda k: a + k * h
    I[0].append(I[0][-1]/2 + h * f((a+b)/2))

    i = 0
    c = 1
    while abs(I[i][0] - I[i][1]) >= tol:
        n *= 2
        h /= 2
        i += 1
        c *= 4 # c == 4**i
        I.append([ (c*I[i-1][1] - I[i-1][0]) / (c-1) ])
        I[0].append(I[0][-1]/2 + h * sum(f(x(2*k + 1)) for k in range(n)))
        cc = 4
        for j in range(i, 0, -1):
            I[i-j+1].append((cc * I[i-j][j+1] - I[i-j][j]) / (cc-1))
            cc *= 4
    return I[-1][-1]

if __name__ == '__main__':
    from math import sin, sqrt, exp, log
    f1 = lambda x: sqrt(4 - (sin(x))**2)
    f2 = lambda x: 1 if x == 0 else sin(x) / x
    f3 = lambda x: exp(x) / (4 + x**2)
    f4 = lambda x: log(1 + x) / (1 + x**2)
    print(trapezoid(f1, 0, 0.25, n=80))
    print(trapezoid(f1, 0, 0.25, n=90))
    print(trapezoid(f1, 0, 0.25, n=100))
    print(simpson(f1, 0, 0.25, n=80))
    print(simpson(f1, 0, 0.25, n=90))
    print(simpson(f1, 0, 0.25, n=100))
    print(romberg(f1, 0, 0.25))

    print(trapezoid(f2, 0, 1, n=80))
    print(trapezoid(f2, 0, 1, n=90))
    print(trapezoid(f2, 0, 1, n=100))
    print(simpson(f2, 0, 1, n=80))
    print(simpson(f2, 0, 1, n=90))
    print(simpson(f2, 0, 1, n=100))
    print(romberg(f2, 0, 1))

    print(trapezoid(f3, 0, 1, n=80))
    print(trapezoid(f3, 0, 1, n=90))
    print(trapezoid(f3, 0, 1, n=100))
    print(simpson(f3, 0, 1, n=80))
    print(simpson(f3, 0, 1, n=90))
    print(simpson(f3, 0, 1, n=100))
    print(romberg(f3, 0, 1))

    print(trapezoid(f4, 0, 1, n=80))
    print(trapezoid(f4, 0, 1, n=90))
    print(trapezoid(f4, 0, 1, n=100))
    print(simpson(f4, 0, 1, n=80))
    print(simpson(f4, 0, 1, n=90))
    print(simpson(f4, 0, 1, n=100))
    print(romberg(f4, 0, 1))
