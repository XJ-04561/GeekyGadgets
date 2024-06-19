
from GeekyGadgets.Iterators import *
from GeekyGadgets.Formatting import *

import pytest

def test_alternate():

	iterable = list(range(50))
	data = [c for i in iterable for c in (i, alphabetize(i))]
	iterator = Alternate((i for i in iterable), (alphabetize(i) for i in iterable))

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_alpha_range():

	iterable = list(range(50))
	data = list(map(alphabetize, iterable))
	iterator = AlphaRange(50)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected
	
	iterator = AlphaRange(0, 50)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected
	
	iterator = AlphaRange(0, 50, 1)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_batched():

	for N in [1, 2, 3, 4, 5]:
		iterable = tuple(range(50))
		data = [iterable[i:i+N] for i in range(0, 50, N)]
		iterator = Batched(iterable, N)

		for item, expected in zip(iterator, data):
			print(item, expected)
			assert item == expected

def test_branches_walker():

	def createTree(N):
		if N < 5:
			return [i for i in range(N)]
		else:
			return [createTree(N-1) for i in range(N)]
	iterable = createTree(7)
	data = []
	for x in range(7):
		data.append(createTree(6))
		for y in range(6):
			data.append(createTree(5))
			for z in range(5):
				data.append(createTree(4))
	iterator = BranchesWalker(iterable)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_chain():

	iterable = list(range(50))
	data = iterable + iterable
	iterator = Chain(iterable, iterable)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_chain_chain():

	iterable = list(range(50))
	data = iterable + iterable + iterable + iterable
	iterator = ChainChain([iterable, iterable], [iterable, iterable])

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

@pytest.mark.skip
def test_config_walker():

	iterable = list(range(50))
	data = []
	iterator = ConfigWalker()

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_drop_then_take_while():

	iterable = list(range(50))
	data = list(range(10, 37))
	iterator = DropThenTakeWhile(iterable, lambda x:x < 10, lambda x:x >= 37)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_drop_while():

	iterable = list(range(50))
	data = list(range(10, 50))
	iterator = DropWhile(lambda x:x < 10, iterable)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_grouper():

	iterable = list(range(50))
	data = [tuple(range(i*10, i*10+10)) for i in range(5)]
	iterator = Grouper(iterable, lambda x: x//10)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_leaves_walker():

	
	def createTree(N):
		if N < 5:
			return [i for i in range(N)]
		else:
			return [createTree(N-1) for i in range(N)]
	iterable = createTree(7)
	data = [i for _ in range(7) for _ in range(6) for _ in range(5) for i in range(4)]
	iterator = LeavesWalker(iterable)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

@pytest.mark.skip
def test_repeat():

	iterable = list(range(50))
	data = []
	iterator = Repeat()

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_take_while():

	iterable = list(range(50))
	data = list(range(37))
	iterator = TakeWhile(lambda x:x >= 37, iterable)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

def test_walker():

	def createTree(N):
		if N < 5:
			return [i for i in range(N)]
		else:
			return [createTree(N-1) for i in range(N)]
	iterable = createTree(7)
	data = []
	for x in range(7):
		data.append(createTree(6))
		for y in range(6):
			data.append(createTree(5))
			for z in range(5):
				data.append(createTree(4))
				for i in range(4):
					data.append(i)
	iterator = Walker(iterable)

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected

@pytest.mark.skip
def test_zip_longest():

	iterable = list(range(50))
	data = []
	iterator = ZipLongest()

	for item, expected in zip(iterator, data):
		print(item, expected)
		assert item == expected
