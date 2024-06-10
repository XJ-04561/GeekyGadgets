from GeekyGadgets.TypeHinting import *

def test_isinstance():
	
	assert isinstance(1, Number)
	assert isinstance(1., Number)
	assert isinstance(1j, Number)

	assert isinstance([], Subscriptable)
	assert isinstance((), Subscriptable)
	assert isinstance({}, Subscriptable)

	class myList(list, Subscriptable): pass
	class myThing(Subscriptable):
		iterable : myList[int]
		def __init__(self, iterable):
			self.iterable = myList(iterable)
	
	assert isinstance(myList(), Subscriptable)
	assert isinstance(myThing([1,2,3]).iterable, myList)
	assert isinstance(myThing([1,2,3]), Subscriptable)