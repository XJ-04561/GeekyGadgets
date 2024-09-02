
import GeekyGadgets.Globals as _Globals
import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Formatting as _Formatting
import GeekyGadgets.Math as _Math
import GeekyGadgets.Math.Stats.Functions as _MathFuncs
import GeekyGadgets.Functions as _Functions

_T = _Globals.TypeVar("_T")
_T1 = _Globals.TypeVar("_T1")
_T2 = _Globals.TypeVar("_T2")
_Iterable = _Globals.Iterable
_Iterator = _Globals.Iterator
_Number = _Globals.Number

class Matrix:
	
	data : list
	
	def __init__(self : "Matrix[_T]", n : int, m : int) -> "Matrix[_T]":
		self.n, self.m = n, m
		self.data = list(_Iterators.Repeat(0, n*m))

	def setRows(self : "Matrix[_T]", *rows : _Iterable[_T]) -> "Matrix[_T]":
		for i, row in enumerate(rows):
			self.data[i*self.m:(i+1)*self.m] = row
	
	def setCols(self : "Matrix[_T]", *cols : _Iterable[_T]) -> "Matrix[_T]":
		for i, col in enumerate(cols):
			self.data[i::self.m] = col
	
	# def __iter__(self):
	# 	for i in range(self.n):
	# 		yield self[i]

	@property
	def rows(self : "Matrix[_T]") -> _Globals.Generator[_T]:
		for i in _Iterators.Count(self.n):
			yield self.data[i*self.m:(i+1)*self.m]

	@property
	def cols(self : "Matrix[_T]") -> _Globals.Generator[_T]:
		for i in _Iterators.Count(self.m):
			yield self.data[i::self.m]
	
	@property
	def columns(self : "Matrix[_T]") -> _Globals.Generator[_T]:
		return self.cols

	def __str__(self):
		low, high = min(self.data), max(self.data)
		ret = []
		if self.n <= 6:
			for row in self.rows:
				if self.m <= 6:
					ret.append("|".join(f" {_Formatting.floatEmphasize(x, low=low, high=high, length=5)} " for x in row))
				else:
					ret.append(
						"|".join(f" {_Formatting.floatEmphasize(x, low=low, high=high, length=5)} " for x in row[:3])
						+"|  ...  |"
						+"|".join(f" {_Formatting.floatEmphasize(x, low=low, high=high, length=5)} " for x in row[-3:])
					)
				
		else:
			for i, row in enumerate(self.rows):
				if 3 <= i < self.n - 3:
					continue
				if self.m <= 6:
					ret.append("|".join(f" {_Formatting.floatEmphasize(x, low=low, high=high, length=5)} " for x in row))
				else:
					ret.append(
						"|".join(f" {_Formatting.floatEmphasize(x, low=low, high=high, length=5)} " for x in row[:3])
						+"|  ...  |"
						+"|".join(f" {_Formatting.floatEmphasize(x, low=low, high=high, length=5)} " for x in row[-3:])
					)
				if i == 2:
					ret.append("|"+"|".join(_Iterators.Repeat("  ...  ", 7))+"|")
		
		return "\n".join(ret)

	def __repr__(self):
		return f"<{self.__class__.__name__} object rows={self.n} cols={self.m} at {id(self):#x}>"

	def __call__(self : "Matrix[_T]", index : _Globals.SupportsIndex) -> _T:
		return self.data[index]

	@_Globals.overload
	def __getitem__(self, index : _Globals.Index, /) -> "Vector": ...
	@_Globals.overload
	def __getitem__(self, index : tuple[_Globals.Index,_Globals.Index], /) -> _T: ...
	def __getitem__(self, index : _Globals.Index|tuple[_Globals.Index,_Globals.Index], /) -> "Vector|_T":
		if not isinstance(index, tuple):
			index = index.__index__()
			return Vector(self.data(slice(index*self.m, (index+1)*self.m)))
		
		i, j = index
		
		if isinstance(i, slice) and isinstance(j, slice):
			return Matrix(
				self(slice(
					j.start+i*self.m,
					j.stop+i*self.m,
					j.step
				))
				for i in range(
					0 if i.start is None else i.start,
					self.n if i.stop is None else i.stop,
					1 if i.step is None else i.step
			))
		elif isinstance(i, slice):
			return Vector(
				self(
					slice(
						j if i.start is None else i.start*self.m+j,
						None if i.stop is None else i.stop*self.m+j,
						self.m if i.step is None else i.step*self.m
			)))
		elif isinstance(j, slice):
			return Vector(
				self(
					slice(
						self.m*(i) if j.start is None else j.start+self.m*i,
						self.m*(i+1) if j.stop is None else j.stop+self.m*i,
						j.step
			)))
		else:
			return self(j+i*self.m)
		
	def __setitem__(self : "Matrix[_T]", index : tuple[_Globals.SupportsIndex,_Globals.SupportsIndex], value : _T) -> None:
		self.data[index[0]*self.m+index[1]] = value

class Vector:
	
	data : list
	n : int
	m : int

	def __init__(self : "Vector[_T]", n : int, m : int, *, data : _Iterable[_T]|None=None) -> _Globals.NoneType:
		self.n = n
		self.m = m
		assert self.n == 1 or self.m == 1
		if data is None:
			self.data = list(_Iterators.Repeat(0, self.n * self.m))
		else:
			self.data = list(data)
		assert len(self.data) == self.n or len(self.data) == self.m
	
	def __iter__(self):
		return iter(self.data)

	def __setitem__(self : "Vector[_T]", index : _Globals.SupportsIndex, value : _T) -> None:
		self.data[index] = value

	def __getitem__(self, index : int, /) -> _T:
		return self.data[index]
	
	def __mul__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1*x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be multiplied!")
		else:
			return Vector(x*value for x in self)
	
	def __rmul__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1*x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be multiplied!")
		else:
			return Vector(value*x for x in self)
	
	def __add__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1+x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be added!")
		else:
			return Vector(x+value for x in self)
	
	def __radd__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1+x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be added!")
		else:
			return Vector(value+x for x in self)
	
	def __sub__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1-x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be subtracted!")
		else:
			return Vector(x-value for x in self)
	
	def __rsub__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1-x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be subtracted!")
		else:
			return Vector(value-x for x in self)
	
	def __truediv__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1/x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be divided!")
		else:
			return Vector(x/value for x in self)
	
	def __rtruediv__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1/x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be divided!")
		else:
			return Vector(value/x for x in self)
	
	def __floordiv__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1//x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be integer-divided!")
		else:
			return Vector(x//value for x in self)
	
	def __rfloordiv__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1//x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be integer-divided!")
		else:
			return Vector(value//x for x in self)
		
	def __mod__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1%x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be used for modulus!")
		else:
			return Vector(x%value for x in self)
	
	def __rmod__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1%x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be used for modulus!")
		else:
			return Vector(value%x for x in self)
		
	def __pow__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1**x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be used for x^y!")
		else:
			return Vector(x**value for x in self)
	
	def __rpow__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1**x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be used for x^y!")
		else:
			return Vector(value**x for x in self)
		
	def __or__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1|x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be used for bitwise or!")
		else:
			return Vector(x|value for x in self)
	
	def __ror__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1|x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be used for bitwise or!")
		else:
			return Vector(value|x for x in self)
		
	def __and__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1&x2 for x1, x2 in zip(self, value))
			else:
				ValueError(f"Only same-length vectors can be used for x^y!")
		else:
			return Vector(x&value for x in self)
	
	def __rand__(self, value: _Globals.SupportsIndex) -> "Vector":
		if isinstance(value, Matrix):
			return NotImplemented
		elif isinstance(value, Vector):
			if self.n == value.n:
				return Vector(x1&x2 for x1, x2 in zip(value, self))
			else:
				ValueError(f"Only same-length vectors can be used for x^y!")
		else:
			return Vector(value&x for x in self)
		
	def __not__(self) -> "Vector":
		return Vector(~x for x in self)
	def __pos__(self) -> "Vector":
		return Vector(+x for x in self)
	def __neg__(self) -> "Vector":
		return Vector(-x for x in self)
	def __abs__(self) -> "Vector":
		return _Math.sqrt(sum(x**2 for x in self))
	
	def forEach(self : "Vector[_T1]", func : _Globals.Callable[[_T1],_T2]) -> "Vector[_T2]":
		return Vector(map(func, self))

def vectorOperation(self : Vector[_T], operator, value: Matrix[_T]|Vector[_T]|_T) -> "Vector":
	if isinstance(value, Matrix):
		return NotImplemented
	elif isinstance(value, Vector):
		if self.n == value.m:
			return Vector(_Functions.operate(x1, operator, x2) for x1, x2 in zip(self, value))
		elif self.m == value.n:
			return sum(_Functions.operate(x1, operator, x2) for x1, x2 in zip(self, value))
		else:
			ValueError(f"Only same-length vectors can be multiplied!")
	else:
		return Vector(_Functions.operate(x, operator, value) for x in self)

def rVectorOperation(self : Vector[_T], operator, value: Matrix[_T]|Vector[_T]|_T) -> "Vector":
	if isinstance(value, Matrix):
		return NotImplemented
	elif isinstance(value, Vector):
		if self.n == value.n:
			return Vector(self.n, self.m, data=(_Functions.operate(x1, operator, x2) for x1, x2 in zip(value, self)))
		else:
			ValueError(f"Only same-length vectors can be multiplied!")
	else:
		return Vector(self.n, self.m, data=(_Functions.operate(value, operator, x) for x in self))