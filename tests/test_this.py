

def test_use():
	from GeekyGadgets.This import this

	class Test:
		def __init__(self, i):
			self._d = {"*":i}
		def wow(self, x):
			return {key:value*x for key,value in self._d.items()}
	
	class CustomClass:
		a : int
		b : str
		def __init__(self, a, b):
			self.a, self.b = a, b
		def __index__(self):
			return self.a
		def __hash__(self):
			return hash(self.b)
	
	assert str(this) == "<class 'GeekyGadgets.This.this'>"
	assert str(this.att) .startswith("<this.att at ")
	assert str(this(1,2,h=8)) .startswith("<this(1, 2, h=8) at ")
	assert str(this[1,3]) .startswith("<this[(1, 3)] at ")
	assert str(this.att(1,2,h=8)[1,3]) .startswith("<this.att(1, 2, h=8)[(1, 3)] at ")
	assert str(next(this.att(1,2,h=8)[1,3])) .startswith("<This.Function (this): return this.att(1, 2, h=8)[(1, 3)] at ")

	#      tuple(map(lambda x : x.wow(2)["*"], [Test(i) for i in range(4)]))
	assert tuple(map(*this.wow(2)["*"], [Test(i) for i in range(4)])) == (0, 2, 4, 6)
	#      tuple(map(lambda x : x[CustomClass(1,"*")], [("b","a"), ("d","c")]))
	assert tuple(map(*this[CustomClass(1,"*")], [("b","a"), ("d","c")])) == ("a", "c")

	myList = ("Apple", "Lion", "Tennis")

	results = tuple(map(*this.lower(), myList))
	
	assert results == ("apple", "lion", "tennis")

	myMixedList = ("Apple", 12, b"\x03Oo")

	results = tuple(map(*this.lower(), filter(*this.__class__ == str, myMixedList)))

	assert results == ("apple",)