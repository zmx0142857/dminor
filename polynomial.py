"""Polynomial.py: deal with polynomials."""

__author__ = "卓铭鑫"

class Poly(object):

	"""
	Doctest:

	>>> Poly(1,2,3)
	x^2 +2x +3
	>>> Poly(1,-1,-1)
	x^2 -x -1
	>>> Poly(1,-4,-10)
	x^2 -4x -10
	>>> Poly(-1,-4,-10)
	-x^2 -4x -10
	>>> Poly(-1,-4,0)
	-x^2 -4x
	>>> Poly(-1,0,-90)
	-x^2 -90

	>>> p = Poly(1,-2,3)
	>>> q = Poly(9,0,-1,3)
	>>> p+q
	9x^3 +x^2 -3x +6
	>>> p-q
	-9x^3 +x^2 -x

	>>> p = Poly(1,1)
	>>> p*p
	x^2 +2x +1
	>>> p
	x +1
	>>> q = Poly(1,-1)
	>>> p*q
	x^2 -1

	>>> p = Poly(1,-3,2)
	>>> p(5)
	12
	>>> p
	x^2 -3x +2
	>>> p(2)
	0
	"""

	def __init__(self, *args, var='x'):
		from collections import Iterable

		self._var = var

		if len(args) == 1 and isinstance(args[0], Poly):
			self._coef = list(args[0]._coef)

		elif len(args) == 1 and isinstance(args[0], Iterable):
			self._coef = list(args[0])

		elif len(args) == 2 and callable(args[0]):
			if not isinstance(args[1], int) or args[1] < 0:
				raise TypeError('The 2nd argument (degree) '
								'must be a non-negative int.')
			self._coef = [args[0](i) for i in range(args[1]+1)]

		else:
			self._coef = list(reversed(args))

		# eliminate extra zeros
		while self._coef[-1] == 0:
			self._coef.pop()

	# specials-------------------------------------------------

	def __len__(self):
		"""
		Returns self.deg() + 1.
		"""
		return len(self._coef)

	def __getitem__(self, key):
		"""
		Returns Cn, the coefficient of item x^n.
		"""
		if not isinstance(key, int):
			raise TypeError('Key must be an int.')
		elif key < -len(self):
			raise IndexError('Index out of range.')
		elif key > self.deg():
			return 0
		else:
			return self._coef[key]

	def __setitem__(self, key, value):
		if not isinstance(key, int):
			raise TypeError('Key must be an int.')
		elif key < -len(self):
			raise IndexError('Index out of range.')

		while key > self.deg():
			self._coef.append(0)
		self._coef[key] = value

	def __str__(self):

		def _item():
			# reversed iter:
			for i in range(len(self)-1, -1, -1):
				if self[i] == 0:
					yield ''
					continue

				if self[i] < 0 and i == len(self)-1:
					sign = '-'
				elif self[i] < 0:
					sign = ' -'
				elif i == len(self)-1:
					sign = '' # omit leading '+'
				else:
					sign = ' +'

				if abs(self[i]) == 1 and i != 0:
					coef = ''
				else:
					coef = str(abs(self[i]))

				if i == 0:
					index = ''
				elif i == 1:
					index = self._var
				else:
					index = self._var + '^' + str(i)

				yield sign + coef + index

		return ''.join(_item())

	__repr__ = __str__

	def __call__(self, v):
		"""
		-> value

		Assign a value to self.
		"""
		ret = self[-1]
		for c in self._coef[-2::-1]:
			ret = ret*v + c
		return ret

	def __eq__(self, other):
		try:
			other = Poly(other)
		except Exception:
			return False
		return self._coef == other._coef

	def __ne__(self, other):
		return not self == other

	def __pos__(self):
		return self

	def __neg__(self):
		return Poly( -c for c in self._coef )

	def __add__(self, other):
		try:
			other = Poly(other)
		except Exception:
			raise NotImplementedError

		sz = max( len(self), len(other) )
		return Poly( self[i] + other[i] for i in range(sz) )

	def __radd__(self, other):
		return self + other

	def __sub__(self, other):
		return self + (-other)

	def __rsub__(self, other):
		return (-self) + other

	def __mul__(self, other):
		try:
			other = Poly(other)
		except Exception:
			raise NotImplementedError

		# 0 <= i < len(self)
		# 0 <= j-i < len(other) -> j-len(other) < i <= j
		# hence max(0, j-len(other)-1) <= i < min(j+1, len(self))
		ls, lo = len(self), len(other)
		return Poly(( sum( self[i] * other[j-i] for i in  range(max(0, j-lo-1), min(j+1, ls)) ) for j in range(ls+lo) ))

	def __rmul__(self, other):
		return self * other

	# other methods--------------------------------------------

	def deg(self):
		"""
		-> non-negative int

		Returns the degree of self.
		"""
		return len(self._coef)-1

	def var(c):
		"""
		-> None
		
		Reset the variable name for self.
		"""
		self._var = c

# class ends---------------------------------------------------

if __name__ == '__main__':
	import doctest
	doctest.testmod()

"""
即将推出：插值公式初始化方式(tuples)，Bernoulli 公式求和方法 p.sum()
"""