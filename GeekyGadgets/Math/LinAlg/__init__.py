
# from GeekyGadgets.Math.LinAlg.Globals import Matrix, Vector
import GeekyGadgets.Globals as _Globals
import GeekyGadgets.Iterators as _Iterators

_X = _Globals.TypeVar("_X", bound=_Globals.Number)
_Y = _Globals.TypeVar("_Y", bound=_Globals.Number)

def rotate(x : _X|tuple[_X,_Y], y : _Y|None=None, /, *, deg : _Globals.Number|None=None, rad : _Globals.Number|None=None):
	from GeekyGadgets.Math import cos, sin
	if y is None:
		x, y = x
	if rad is None:
		from GeekyGadgets.Math import radians
		rad = radians(deg)
	return (
		(cos(rad)*x+sin(rad)*y),
		(-sin(rad)*x+cos(rad)*y)
	)

def translate(a : tuple[_X,_Y]|tuple[tuple[_X,_Y]], /, *, delta : tuple[_X,_Y]|None=None, xD : _X|None=None, yD : _Y|None=None):
	if delta is not None:
		shiftX, shiftY = delta
	else:
		shiftX, shiftY = 0, 0
	if xD is not None:
		shiftX = shiftX + xD
	if yD is not None:
		shiftY = shiftY + yD
	
	if shiftX == shiftY == 0:
		return a
	elif shiftX == 0:
		return tuple((row[0], row[1]+shiftY) for row in a) if a and isinstance(a[0], _Globals.Iterable) else (a[0], a[1]+shiftY)
	elif shiftY == 0:
		return tuple((row[0]+shiftX, row[1]) for row in a) if a and isinstance(a[0], _Globals.Iterable) else (a[0]+shiftX, a[1])
	else:
		return tuple((row[0]+shiftX, row[1]+shiftY) for row in a) if a and isinstance(a[0], _Globals.Iterable) else (a[0]+shiftX, a[1]+shiftY)

@_Globals.overload
def dot(A : tuple[_X]|tuple[tuple[_X]], B : tuple[_X]|tuple[tuple[_X]], /) -> tuple[tuple[_X]]: ...
@_Globals.overload
def dot(v : tuple[_X], T : tuple[tuple[_X]], /) -> tuple[_X]: ...
@_Globals.overload
def dot(T : tuple[tuple[_X]], v : tuple[_X], /) -> tuple[_X]: ...
def dot(*AB : tuple[_X]|tuple[tuple[_X]]) -> tuple[_X]:
	
	A, B = AB
	
	if A and isinstance(A[0], _Globals.Iterable) and B and isinstance(B[0], _Globals.Iterable):
		assert (n := len(A[0])) == len(B)
		return [
			[
				sum(x1*x2 for x1, x2 in zip(map(lambda x:x[i], B), row))
				for i in range(n)
			]
			for row in A
		]
	elif A and isinstance(A[0], _Globals.Iterable):
		assert len(A[0]) == len(B)
		return [
			sum(x1*x2 for x1, x2 in zip(B, row))
			for row in A
		]
	elif B and isinstance(B[0], _Globals.Iterable):
		assert len(A) == len(B)
		return [
			sum(x1*x2 for x1, x2 in zip(A, row))
			for row in B
		]
	else:
		return sum(x1*x2 for x1, x2 in zip(A, B))