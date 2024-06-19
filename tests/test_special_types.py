
from GeekyGadgets.SpecialTypes import LimitedDict, LimitedList, LimitedSet

def test_limited_dict():

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

def test_limited_list():
	
	l1 = LimitedList(limit=100)
	l2 = []
	for i in range(100):
		l1.append(i)
		l2.append(i)
		try:
			assert l1 == l2
		except:
			l1
			assert l1 != l2

	l1.append(100)
	l2.append(100)
	assert l1 != l2
	assert 0 not in l1
	assert 0 in l2

	l1.remove(40)
	l2.remove(40)

	l1.append(101)
	l2.append(101)
	assert 1 in l1
	assert 1 in l2

	assert 1 == l1.pop(0)
	assert 0 == l2.pop(0)
	assert 1 not in l1
	assert 0 not in l2
	assert 1 in l2
	l1.append(102)
	l2.append(102)

	l1.append(103)
	l2.append(103)
	assert 2 not in l1
	assert 2 in l2

	l3 = LimitedList(l2, limit=100)

	assert l1 == l3

	l1.clear()

	assert len(l1) == 0 == l1.size

def test_limited_set():
	
	s1 = LimitedSet(limit=100)
	s2 = set()
	for i in range(100):
		s1.add(i)
		s2.add(i)
		try:
			assert s1 == s2
		except:
			s1
			assert s1 != s2

	s1.add(100)
	s2.add(100)
	assert s1 != s2
	assert 0 not in s1
	assert 0 in s2

	s1.remove(40)
	s2.remove(40)

	s1.add(101)
	s2.add(101)
	assert 1 in s1
	assert 1 in s2

	assert 1 == s1.pop()
	assert 0 == s2.pop()
	assert 1 not in s1
	assert 0 not in s2
	assert 1 in s2

	s1.add(102)
	s2.add(102)

	s1.add(103)
	s2.add(103)
	assert 2 not in s1
	assert 2 in s2

	s3 = LimitedSet(s2, limit=100)

	assert s1 == s3

	s1.clear()

	assert len(s1) == 0 == s1.size

def test_name_space():
	
	from GeekyGadgets.SpecialTypes import NameSpace
	import random

	data = [i for i in range(10)]

	d = {hex(i)[1:]:i for i in data}

	ns = NameSpace(d)

	for key in d:
		assert ns[key] == d[key]
	
	d["ABC"] = 123

	try:
		assert ns["ABC"] is not None
	except:
		pass
	else:
		assert False
	
	ns["ABC"] = 878

	assert d["ABC"] == 123
	assert ns["ABC"] == 878

def test_link_space():
	
	from GeekyGadgets.SpecialTypes import NameSpace, LinkedSpace
	import random

	data = [i for i in range(10)]

	d = {hex(i)[1:]:i for i in data}

	ns = NameSpace(d)
	ls = LinkedSpace(ns)

	for key in d:
		assert ls[key] == d[key]
	
	d["ABC"] = 123

	try:
		assert ls["ABC"] is not None
	except:
		pass
	else:
		assert False
	
	ls["ABC"] = 878
	assert ls.ABC == 878
	ls.XYZ = 935

	assert d["ABC"] == 123
	assert ns["ABC"] == 878 == ls.ABC == ls["ABC"] == ns.ABC
	assert ns["XYZ"] == 935 == ls.XYZ == ls["XYZ"] == ns.XYZ