
import GeekyGadgets.Globals as _Globals
import GeekyGadgets.Iterators as _Iterators
from math import log, log10, sqrt, exp
import functools as _functools

def product(*X):
	ret = 1
	for x in X:
		ret *= x
	return ret

def floor(x : float):
	return int(x // 1)

def ceil(x : float):
	return int(x // 1) + bool(x % 1)

def sign(x : float):
	return round(x / abs(x))

def minmax(iterable):
	iterator = iter(iterable)
	x = X = next(iterator)
	for v in iterator:
		if x > v:
			x = v
		elif X < v:
			X = v
	return x, X

def span(iterable):
	low, high = minmax(iterable)
	return high - low

def heaviside(c : _Globals.Number) -> _Globals.Callable[[_Globals.Number],_Globals.Literal[0,1]]:
	return lambda x: 1 if x >= c else 0

def pingPong(x : _Globals.Number) -> _Globals.Callable[[_Globals.Number],_Globals.Interval[0,1]]:
	return abs(1 - 2 * ((x+0.5)%1))

def triangle(x : _Globals.Number) -> _Globals.Callable[[_Globals.Number],_Globals.Interval[0,1]]:
	return 1 - abs(2 * x) if -0.5 < x < 0.5 else 0

def limit(low, value, high):
	return low if low > value else high if high < value else value

def lin(k : _Globals.Number, x : _Globals.Number, m : _Globals.Number) -> _Globals.Number:
	return k*x + m

def factors(n : int) -> tuple[int]:
	return tuple(i for i in range(ceil(sqrt(n)), 1, -1) if not n % i)

def nTiles(iterable : _Globals.Iterable, n):
	"""Returns `n+1` values, not `n` values!"""
	
	data = sorted(iterable)
	length = len(data)
	
	return tuple(data[int(i)] if i % 1 == 0 else ((1-i%1)*data[floor(i)]+(i%1)*data[ceil(i)]) for i in _Iterators.Spaced(0, length-1, n+1))

def quantiles(iterable : _Globals.Iterable):
	return nTiles(iterable, 4)
	
def quintiles(iterable : _Globals.Iterable):
	return nTiles(iterable, 5)