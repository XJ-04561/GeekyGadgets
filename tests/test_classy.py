
from GeekyGadgets.Classy import *
import random

def test_default():
	class GameConstraint(Exception): pass
	class NotEnoughMana(GameConstraint): pass

	class CharacterA:

		Strength : int
		Agility : int
		Stamina : int
		Intellect : int
		Spirit : int

		HP : int = property(lambda self:self._HP, lambda self, value:setattr(self, "_HP", min(value, self.MaxHP)))
		MP : int = property(lambda self:self._MP, lambda self, value:setattr(self, "_MP", min(value, self.MaxMP)))

		BaseHP = property(lambda self: 5 * self.Stamina)
		BaseMP = property(lambda self: 5 * self.Intellect)

		MaxHP = Default["Buffs", "BaseHP"](lambda self: self.BaseHP + sum(self.BaseHP * buff for buff in self.Buffs))
		MaxMP = Default["Buffs", "BaseMP"](lambda self: self.BaseMP + sum(self.BaseMP * buff for buff in self.Buffs))

		Buffs : list[float|int]

		def __init__(self, strength=20, agility=20, stamina=20, intellect=20, spirit=20):
			self.Strength = strength
			self.Agility = agility
			self.Stamina = stamina
			self.Intellect = intellect
			self.Spirit = spirit
			self.Buffs = []

		def addBuff(self, buff : float|int):
			self.Buffs.append(buff)
		def addDeBuff(self, buff : float|int):
			self.Buffs.append(-buff)
	
	class CharacterB:

		Strength : int
		Agility : int
		Stamina : int
		Intellect : int
		Spirit : int

		HP : int = property(lambda self:self._HP, lambda self, value:setattr(self, "_HP", min(value, self.MaxHP)))
		MP : int = property(lambda self:self._MP, lambda self, value:setattr(self, "_MP", min(value, self.MaxMP)))

		BaseHP = property(lambda self: 5 * self.Stamina)
		BaseMP = property(lambda self: 5 * self.Intellect)

		@Default["Buffs", "BaseHP"]
		def MaxHP(self):
			return self.BaseHP + sum(self.BaseHP * buff for buff in self.Buffs)
		
		@Default["Buffs", "BaseMP"]
		def MaxMP(self):
			return self.BaseMP + sum(self.BaseMP * buff for buff in self.Buffs)

		Buffs : list[float|int]

		def __init__(self, strength=20, agility=20, stamina=20, intellect=20, spirit=20):
			self.Strength = strength
			self.Agility = agility
			self.Stamina = stamina
			self.Intellect = intellect
			self.Spirit = spirit
			self.Buffs = []

		def addBuff(self, buff : float|int):
			self.Buffs.append(buff)
		def addDeBuff(self, buff : float|int):
			self.Buffs.append(-buff)
	
	characterA = CharacterA()
	characterB = CharacterB()
	
	assert characterA.BaseHP == 100
	assert characterA.BaseMP == 100
	assert characterA.MaxHP == 100
	assert characterA.MaxMP == 100

	characterA.Intellect *= 2
	assert characterA.BaseHP == 100
	assert characterA.BaseMP == 200
	assert characterA.MaxHP == 100
	assert characterA.MaxMP == 200

	characterA.addBuff(0.2)
	assert characterA.BaseHP == 100
	assert characterA.BaseMP == 200
	assert characterA.MaxHP == 120
	assert characterA.MaxMP == 240


	assert characterB.BaseHP == 100
	assert characterB.BaseMP == 100
	assert characterB.MaxHP == 100
	assert characterB.MaxMP == 100

	characterB.Intellect *= 2
	assert characterB.BaseHP == 100
	assert characterB.BaseMP == 200
	assert characterB.MaxHP == 100
	assert characterB.MaxMP == 200

	characterB.addDeBuff(0.2)
	assert characterB.BaseHP == 100
	assert characterB.BaseMP == 200
	assert characterB.MaxHP == 80
	assert characterB.MaxMP == 160

def test_class_property():
	
	class ParentClass:
		
		subclasses = ClassProperty(lambda cls:cls.__subclasses__() if cls is ParentClass else type(cls).__subclasses__())
	
	class ChildClass(ParentClass): pass

	obj = ParentClass()
	assert ParentClass.subclasses == [ChildClass]
	assert obj.subclasses == [ChildClass]

def test_cached_class_property():
	
	class ParentClass:
		
		subclasses = CachedClassProperty(lambda cls:cls.__subclasses__() if cls is ParentClass else type(cls).__subclasses__())
	
	class ChildClass(ParentClass): pass

	obj = ParentClass()
	assert ParentClass.subclasses == [ChildClass]
	assert obj.subclasses == [ChildClass]

	class OtherChildClass(ParentClass): pass

	assert ParentClass.subclasses != [ChildClass, OtherChildClass]
	assert obj.subclasses != [ChildClass, OtherChildClass]

	assert ParentClass.subclasses == [ChildClass]
	assert obj.subclasses == [ChildClass]

def test_threaded():
	
	from GeekyGadgets.Threads import Future
	globalList = []
	
	@threaded
	def func(a : int, b):
		import time
		time.sleep(a / 4)
		globalList.append(a * b)
		return a * b
	
	futures = []
	for i in range(1, 8):
		futures.append( func(i/4, 1.2))
	
	for i in range(1, 8):
		assert futures[i-1].call() == (i/4) * 1.2
	assert globalList == list(map(Future.call, futures))

	class Worker:
		
		def __init__(self, N : float):
			self.N = N
			self.results = {}
		
		@threaded
		def work(self, M : float):
			import time
			time.sleep(M / 4)
			self.results[M] = self.N*M
			return self.N*M
	
	worker1 = Worker(1)
	worker2 = Worker(2)
	for i in range(1, 4):
		future1 = worker1.work(i/2)
	
	for i in range(8, 12):
		future2 = worker2.work(i/2)
	
	assert future1.group is not future2.group

	assert future1.group.allAlive
	assert future2.group.allAlive
	future1.group.wait()
	
	assert not future1.group.anyAlive
	assert future2.group.allAlive

	future2.group.wait()

	assert not future1.group.anyAlive
	assert not future2.group.anyAlive

	assert future1.group.results == (1/2, 2/2, 3/2) == tuple(worker1.results.values())
	assert future2.group.results == (2*(8/2), 2*(9/2), 2*(10/2), 2*(11/2)) == tuple(worker2.results.values())