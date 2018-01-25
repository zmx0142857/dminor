"""Do differential and integral.

"""

def Reman_int(func, a, b):
    ret = 0
    dx = (b-a)/1e4
    x = a
    while x <= b:
        ret += func(x) * dx
        x += dx
    return ret

def diff(func, x0):
	pass