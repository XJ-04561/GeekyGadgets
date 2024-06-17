
from GeekyGadgets.Globals import *

__all__ = ("Default", "ClassProperty", "CachedClassProperty", "threaded")

class Default(property):
	"""Works similarly to `functools.cached_property`, and has a setter and deleter by default like that of 
	`functools.cached_property`. But, it allows to have the default value refreshed when some specific dependencies 
	are changed. THe dependencies can be set either through the `deps` argument to the object constructor, or by 
	indexing the class itself to create an empty `Default` that only has dependencies set, but no callback function 
	yet. But calling the created object will forward the arguments to the `Default.__init__` that sets up the object 
	in full.
	
	### Example
	```python
	class GameConstraint(Exception): pass
	class NotEnoughMana(GameConstraint): pass

	class Character:

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
		#	OR LIKE THIS
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
	
	character = Character()
	
	print(character.MaxHP)
	# 100
	print(character.MaxMP)
	# 100

	character.Intellect *= 2
	print(character.MaxHP)
	# 100
	print(character.MaxMP)
	# 200

	character.addBuff(1.2)
	print(character.MaxHP)
	# 120
	print(character.MaxMP)
	# 240

	```"""

	name : str

	fget : Callable
	fset : Callable
	fdel : Callable
	deps : tuple

	def __init__(self, fget=None, fset=None, fdel=None, doc=None, deps : tuple[str]=()):
		super().__init__(fget, fset, fdel, doc)
		if hasattr(self.fget, "__code__"):
			self.fgetArgnames = self.fget.__code__.co_varnames[:self.fget.__code__.co_argcount+self.fget.__code__.co_kwonlyargcount]
		elif hasattr(getattr(self.fget, "__func__", None), "__code__"):
			self.fgetArgnames = self.fget.__func__.__code__.co_varnames[:self.fget.__code__.co_argcount+self.fget.__code__.co_kwonlyargcount]
		else:
			self.fgetArgnames = ()
		if deps or not hasattr(self, "deps"):
			self.deps = deps
		
	def __call__(self, fget=None, fset=None, fdel=None, doc=None):
		self.__init__(fget, fset, fdel, doc=doc)
		return self
	
	def __class_getitem__(cls, deps):
		"""Calls Default(None) and adds the keys provided as the names of attributes upon which this value depends
		before returning. This is useful for creating attributes which have default values which are meant to be
		dependent on other attributes of the same object. When getting the same attribute repeatedly, new attribute
		value instances will not be created, the first one is returned until one of the dependency attributes are
		changed."""
		return cls(deps=deps if isinstance(deps, tuple) else (deps, ))
	
	def __set_name__(self, owner, name):
		self.name = name
		if "return" in getattr(self.fget, "__annotations__", ()) and self.name not in getattr(owner, "__annotations__", ()):
			owner.__annotations__[name] = self.fget.__annotations__["return"]

	def __get__(self, instance, owner=None):
		from GeekyGadgets.Functions import forceHash, getAttrChain
		if instance is None:
			return self
		if self.name in getattr(instance, "__dict__", ()):
			return instance.__dict__[self.name]
		else:
			values = tuple(getAttrChain(instance, dep) for dep in self.deps)
			currentHash = forceHash(values)
		
		if hasattr(instance, "__dict__") and instance.__dict__.get(f"_default_{self.name}", (currentHash+1,))[0] == currentHash:
			return instance.__dict__[f"_default_{self.name}"][1]
		else:
			ret = self.fget(instance, **{name:value for name, value in zip(self.deps,values) if name.replace(".", "_") in self.fgetArgnames})
			instance.__dict__[f"_default_{self.name}"] = (currentHash, ret)
			return ret
	
	def __set__(self, instance, value):
		if self.fset is None:
			instance.__dict__[self.name] = value
		else:
			self.fset(instance, value)
	
	def __delete__(self, instance):
			if self.fdel is not None:
				self.fdel(instance)
			else:
				if self.name in getattr(instance, "__dict__", ()):
					del instance.__dict__[self.name]
				if f"_default_{self.name}" in getattr(instance, "__dict__", ()):
					del instance.__dict__[f"_default_{self.name}"]
	
	# def getter(self, fget):
	# 	self.fget = fget
	# 	return self
	
	# def setter(self, fset):
	# 	self.fset = fset
	# 	return self
	
	# def deleter(self, fdel):
	# 	self.fdel = fdel
	# 	return self

class ClassProperty:
	"""Similar to `builtins.property` but will generate the callback-returned value when accessed through the class 
	itself, and not only through an instance of the class.
	
	### Example
	```python
	import time
	from timeit import default_timer as timer
	start = timer()

	class MyClass:
		@ClassProperty
		def now(self) -> float:
			global start
			diff = timer() - start
			start = timer()
			return diff
		
	obj = MyClass()
	print(round(obj.now, 1))
	# 0.0

	time.sleep(1)
	print(round(MyClass.now, 1))
	# 1.0

	time.sleep(1)
	print(round(obj.now, 1))
	# 1.0
	```"""

	owner : type
	name : str
	fget : Callable
	fset : Callable
	fdel : Callable

	def __init__(self, fget, fset=None, fdel=None, doc=None):
		self.fget = fget
		self.fset = fset
		self.fdel = fdel
		
		self.__doc__ = doc if doc else fget.__doc__
	
	def __get__(self, instance, owner=None):
		return self.fget(instance or owner)
	
	def __set__(self, instance, value):
		self.fset(instance, value)
	
	def __delete__(self, instance):
		self.fdel(instance)
	
	def __set_name__(self, owner, name):
		self.owner = owner
		self.name = name
	
	def __repr__(self):
		return f"{object.__repr__(self)[:-1]} name={self.name!r}>"

class CachedClassProperty:
	"""A cached-value version of `ClassProperty`.

	## From `ClassProperty` docstring:

	Similar to `builtins.property` but will generate the callback-returned value when accessed through the class 
	itself, and not only through an instance of the class.
	
	### Example
	```python
	import time
	from timeit import default_timer as timer
	start = timer()

	class MyClass:
		@ClassProperty
		def now(self) -> float:
			global start
			diff = timer() - start
			start = timer()
			return diff
		
	obj = MyClass()
	print(round(obj.now, 1))
	# 0.0

	time.sleep(1)
	print(round(MyClass.now, 1))
	# 1.0

	time.sleep(1)
	print(round(obj.now, 1))
	# 1.0
	```"""

	def __init__(self, func):
		self.func = func
		self.classes = {}

	def __get__(self, instance, owner=None):
		if instance is not None:
			if self.name in getattr(instance, "__dict__", ()):
				return instance.__dict__[self.name]
			instance.__dict__[self.name] = self.func(instance)
			return instance.__dict__[self.name]
		else:
			if id(owner) in self.classes:
				return self.classes[id(owner)]
			self.classes[id(owner)] = self.func(owner)
			return self.classes[id(owner)]
	
	def __set__(self, instance, value):
		instance.__dict__ = value
	
	def __delete__(self, instance):
		del instance.__dict__[self.name]

	def __set_name__(self, owner, name):
		self.name = name
		
	def __repr__(self):
		return f"{object.__repr__(self)[:-1]} name={self.name!r}>"

try:
	from GeekyGadgets.Threads import Thread, ThreadGroup, Future
except ImportError:
	pass

def threaded(func, threadGroup : type["ThreadGroup"]=ThreadGroup):
	"""Creates a wrapper function for `func` that instead starts `func` in another `Thread` object, and returns the 
	`Future` of that created `Thread` object. If wrapper is called as a method, the threads will all belong to a 
	collective but instance unique `ThreadGroup` object, or another threadgroup implementation specified by the 
	keyword argument `threadGroup`. If function is not called as a method, all the threads will be added to a common 
	threadgroup that does not contain any instance unique threads."""
	groups = {}
	groups[0] = threadGroup()
	if "." in func.__qualname__:
		ownerName = func.__qualname__.split(".")[-2]
	else:
		ownerName = None
	def _thread_launcher_wrapper(*args, **kwargs):
		if args and type(args[0]).__name__.split(".")[-1] == ownerName:
			group = groups.get(id(args[0]))
			if group is None:
				groups[id(args[0])] = group = threadGroup()
		else:
			group = groups[0]
		print(groups)
		t = Thread(target=func, args=args, kwargs=kwargs, group=group)
		t.start()
		return t.future
	update_wrapper(_thread_launcher_wrapper, func)
	_thread_launcher_wrapper.__annotations__["return"] = Future
	return _thread_launcher_wrapper
