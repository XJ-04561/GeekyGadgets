
from GeekyGadgets.Globals import *


__all__ = ("Default", "CachedDefault", "ClassProperty", "CachedClassProperty", "threaded")

_NOT_SET = object()
LOGGER = ROOT_LOGGER.getChild(__name__)

class CachedDefaultCodependent(AttributeError):
	
	offender : str

	def __init__(self, offender : str, trace : Iterable[str], **kwargs) -> None:
		self.offender = offender
		super().__init__(f"Couldn't get default value for {offender!r} because its dependencies are dependent on itself. Path of attributes that caused the loop: {' > '.join(map(repr, trace))}", **kwargs)

_INSTANCE = TypeVar("_INSTANCE")
_NAME = TypeVar("_NAME")
_VALUE = TypeVar("_VALUE")
_PROP_VALUE = TypeVar("_PROP_VALUE")

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

	TRACE : "dict[_Thread.Thread,set]" = {}

	name : str

	fget : Callable[[_INSTANCE],_PROP_VALUE] | None = None
	fset : Callable[[_INSTANCE,_VALUE],None] | None = None
	fdel : Callable[[_INSTANCE],None] | None = None
	deps : tuple[str] = ()
	default : Any = _NOT_SET

	locks : "_Synch.LockedDict[int,_Synch.RLock]"

	def __init__(self, fget : Callable[[_INSTANCE],_PROP_VALUE]|None=None, fset : Callable[[_INSTANCE,_VALUE],None]|None=None, fdel : Callable[[_INSTANCE],None]|None=None, doc : str|None=None, deps : tuple[str]|None=None, *, default : Any=_NOT_SET):
		
		import GeekyGadgets.Threads.Synch as _Synch
		import GeekyGadgets.Threads.Thread as _Thread
		import GeekyGadgets.Threads.Groups as _Groups
		self.deps = deps or self.deps
		self.default = default
		if not hasattr(self, "locks"):
			self.locks = _Synch.LockedDict(factory=_Synch.RLock)
		
		super().__init__(fget or self.fget, fset or self.fset, fdel or self.fdel, doc or self.__doc__)
		if fget is not None:
			self.fget = fget
		if fset is not None:
			self.fset = fset
		if fdel is not None:
			self.fdel = fdel
		if doc is not None:
			self.__doc__ = doc
		if default is not _NOT_SET:
			self.default = default
		
		# if hasattr(self.fget, "__code__"):
		# 	self.fgetArgnames = self.fget.__code__.co_varnames[:self.fget.__code__.co_argcount+self.fget.__code__.co_kwonlyargcount]
		# elif hasattr(getattr(self.fget, "__func__", None), "__code__"):
		# 	self.fgetArgnames = self.fget.__func__.__code__.co_varnames[:self.fget.__code__.co_argcount+self.fget.__code__.co_kwonlyargcount]
		# else:
		# 	self.fgetArgnames = ()
		
	def __call__(self, fget=None, fset=None, fdel=None, doc=None, default=_NOT_SET):
		self.__init__(fget, fset, fdel, doc=doc, default=default)
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
		
	def __get__(self, instance : _INSTANCE, owner : type[_INSTANCE]|None=None) -> _PROP_VALUE:
		with self.locks[id(self)]:
			from GeekyGadgets.Threads import current_thread
			if instance is None:
				return self
			elif self.name in instance.__dict__:
				return instance.__dict__[self.name]
			
			if current_thread() not in self.TRACE:
				self.TRACE[current_thread()] = set()
			
			if self.name in self.TRACE[current_thread()]:
				if self.default is _NOT_SET:
					raise CachedDefaultCodependent(self.name, self.TRACE[current_thread()])
				else:
					return self.default
			
			self.TRACE[current_thread()].add(self.name)
			try:
				ret = self.fget(instance)
			except:
				self.TRACE[current_thread()].discard(self.name)
				raise
			else:
				self.TRACE[current_thread()].discard(self.name)
			
			return ret
	
	def __set__(self, instance, value):
		with self.locks[id(self)]:
			instance.__dict__[self.name] = value
			if self.fset:
				self.fset(instance, value)
	
	def __delete__(self, instance):
		with self.locks[id(self)]:
			if self.fdel:
				self.fdel(instance)
			if self.name in getattr(instance, "__dict__", ()):
				del instance.__dict__[self.name]

	@classmethod
	def isDefault(cls, instance, name):
		return not Default.isSet(instance, name)
	
	@classmethod
	def isSet(cls, instance, name):
		return name in instance.__dict__

class ClassDefault(Default):
	def __get__(self, instance: _INSTANCE, owner: type[_INSTANCE] | None = None) -> _PROP_VALUE:
		if instance is None:
			return self.fget(owner)
		else:
			return super().__get__(instance, owner=owner)

class CachedDefault(Default):
	
	@property
	def fget(self):
		return self._fget_wrapper
	
	@fget.setter
	def fget(self, value):
		self._fget = value
	
	def __delete__(self, instance):
		with self.locks[id(self)]:
			super().__delete__(instance)
			if f"_default_{self.name}" in getattr(instance, "__dict__", ()):
				del instance.__dict__[f"_default_{self.name}"]

	def _fget_wrapper(self, instance):
		with self.locks[id(self)]:
			from GeekyGadgets.Functions import forceHash, getAttrChain
			from GeekyGadgets.Threads import current_thread

			if not self.deps:
				if self.name in instance.__dict__:
					return instance.__dict__[self.name]
				elif f"_default_{self.name}" not in instance.__dict__:
					instance.__dict__[f"_default_{self.name}"] = self._fget(instance)
				return instance.__dict__[f"_default_{self.name}"]
			elif f"_default_{self.name}" in instance.__dict__:
				prevHash, value = instance.__dict__[f"_default_{self.name}"]
				if prevHash is None:
					try:
						instance.__dict__[f"_default_{self.name}"] = (forceHash(tuple(getAttrChain(instance, dep) for dep in self.deps)), value)
					except CachedDefaultCodependent:
						pass
					finally:
						ret = value
				elif prevHash == (currentHash := forceHash(tuple(getAttrChain(instance, dep) for dep in self.deps))):
					ret = value
				else:
					try:
						ret = self._fget(instance)
					except Exception as e:
						getattr(instance, "LOG", LOGGER).exception(e)
						self.TRACE[current_thread()].discard(self.name)
						raise e
					instance.__dict__[f"_default_{self.name}"] = (currentHash, ret)
			else:
				try:
					ret = self._fget(instance)
				except Exception as e:
					getattr(instance, "LOG", LOGGER).exception(e)
					self.TRACE[current_thread()].discard(self.name)
					raise e
				try:
					currentHash = forceHash(tuple(getAttrChain(instance, dep) for dep in self.deps))
				except CachedDefaultCodependent:
					currentHash = None
				instance.__dict__[f"_default_{self.name}"] = (currentHash, ret)
			
			return ret

	@classmethod
	def willDefault(cls : "type[CachedDefault]", instance, name):
		return not cls.isSet(instance, name) and f"_default_{name}" not in instance.__dict__

	@classmethod
	def hasDefaulted(cls : "type[CachedDefault]", instance, name):
		return not cls.isSet(instance, name) and f"_default_{name}" in instance.__dict__

class CachedClassDefault(ClassDefault, CachedDefault): ...

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
		return self.fget(instance if instance is not None else owner)
	
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

def threaded(func : function, groupCls : "type[_Groups.ThreadGroup]"=None):

	from GeekyGadgets.Threads import Thread, Future
	groupCls = groupCls or _Groups.ThreadGroup
	if "." in func.__qualname__:
		ownerName = func.__qualname__.split(".")[-2]
	else:
		ownerName = None

	beforeAndAfter = [
		lambda *args, **kwargs:None,
		lambda *args, **kwargs:None
	]
	@staticmethod
	def before(*args, **kwargs):
		beforeAndAfter[0](*args, **kwargs)
	@staticmethod
	def after(*args, **kwargs):
		beforeAndAfter[1](*args, **kwargs)
	
	@wraps(func)
	def _thread_launcher_wrapper(*args, **kwargs):
		t = Thread(
			pre=before,
			target=func,
			post=after,
			args=args,
			kwargs=kwargs,
			group=(
				groupCls(name=id(args[0]))
				if args and type(args[0]).__qualname__.split(".")[-1] == ownerName
				else None
			)
		)
		t.start()
		return t.future
	
	update_wrapper(_thread_launcher_wrapper, func)
	_thread_launcher_wrapper.__annotations__["return"] = Future
	
	_thread_launcher_wrapper.before = partial(beforeAndAfter.__setitem__, 0)
	_thread_launcher_wrapper.after = partial(beforeAndAfter.__setitem__, 1)
	
	return _thread_launcher_wrapper

try:
	import GeekyGadgets.Threads.Synch as _Synch
	import GeekyGadgets.Threads.Thread as _Thread
	import GeekyGadgets.Threads.Groups as _Groups
except ImportError:
	pass