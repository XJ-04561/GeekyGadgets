
from GeekyGadgets.SpecialTypes import LimitedDict

def test_limited_dict():

	from pprint import pprint

	pprint(vars(LimitedDict))
	assert LimitedDict.__setitem__.shaves

	d1 = LimitedDict(limit=100)
	d2 = {}
	for i in range(100):
		d1[i] = hex(i)
		d2[i] = hex(i)
		try:
			assert d1 == d2
		except:
			d1
			assert d1 != d2

	d1[100] = hex(100)
	d2[100] = hex(100)
	assert d1 != d2
	assert 0 not in d1
	assert 0 in d2

	del d1[40]
	del d2[40]

	d1[101] = hex(101)
	d2[101] = hex(101)
	assert 1 in d1
	assert 1 in d2

	assert hex(1) == d1.pop(next(iter(d1.keys())))
	assert hex(0) == d2.pop(next(iter(d2.keys())))
	assert 1 not in d1
	assert 0 not in d2
	assert 1 in d2
	d1[102] = hex(102)
	d2[102] = hex(102)

	d1[103] = hex(103)
	d2[103] = hex(103)
	assert 2 not in d1
	assert 2 in d2

	d1.setdefault(103, hex(103))
	d2.setdefault(103, hex(103))
	assert 3 in d1
	assert 3 in d2
	d1.setdefault(104, hex(104))
	d2.setdefault(104, hex(104))
	assert 3 not in d1
	assert 3 in d2

	d3 = LimitedDict(d2, limit=100)

	assert d1 == d3

	d1.clear()

	assert len(d1) == 0 == d1.size
	