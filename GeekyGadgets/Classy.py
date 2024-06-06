
from GeekyGadgets.Globals import *
from GeekyGadgets.Logging import Logged

_NULL_KEY = object()

class UninitializedError(AttributeError):
	def __init__(self, obj=None, name=None, **kwargs):
		if obj is not None:
			objName = repr(type(obj).__name__)
		else:
			objName = "Object"
		if name is not None:
			name = repr(name) + " "
		else:
			name = ""
		super().__init__(f"Attribute {name}of {objName} was accessed, but has yet to be set.", **kwargs)

class InitCheckDescriptor:

	def __init__(cls, className, bases, namespace):
		cls.names = {}

	def __set_name__(self, owner, name):
		object.__getattribute__(self, "names")[id(owner)] = name

	def __set__(self, instance, value):
		instance.__dict__[object.__getattribute__(self, "names")[id(type(instance))]] = value

	def __get__(self, instance : object, owner=None):
		return instance.__dict__.get(object.__getattribute__(self, "names").get(id(owner), id(_NULL_KEY)), self)

	def __delete__(self, instance):
		pass

	def __mult__(self, other): return self
	def __add__(self, other): return self
	def __sub__(self, other): return self
	def __getattribute__(self, name): return self

	def __bool__(self): return False

class NotSet(metaclass=InitCheckDescriptor): pass

class Default:

	deps : tuple = None
	name : str

	fget : Callable = None
	fset : Callable = None
	fdel : Callable = None

	def __init__(self, fget=None, fset=None, fdel=None, doc=None, deps=(), *, limit : int=10000):
		if fget or not self.fget:
			self.fget = fget
		if fset or not self.fset:
			self.fset = fset
		if fdel or not self.fdel:
			self.fdel = fdel
		self.__doc__ = doc or fget.__doc__ or getattr(self, "__doc__", None)
		if deps or not self.deps:
			self.deps = deps
		
	def __call__(self, fget=None, fset=None, fdel=None, doc=None, *, limit : int=10000):
		self.__init__(fget, fset, fdel, doc=doc, limit=limit)
		return self
	
	def __class_getitem__(cls, deps):
		"""Calls Default(None) and adds the keys provided as the names of attributes upon which this value depends
		before returning. This is useful for creating attributes which have default values which are meant to be
		dependent on other attributes of the same object. When getting the same attribute repeatedly, new attribute
		value instances will not be created, the first one is returned until one of the dependency attributes are
		changed."""
		return cls(deps=deps if isinstance(deps, tuple) else (deps, ))
	
	def __set_name__(self, owner, name):
		if hasattr(self.fget, "__annotations__") and hasattr(owner, "__annotations__") and "return" in self.fget.__annotations__:
			owner.__annotations__[name] = self.fget.__annotations__["return"]
		self.name = name

	def __get__(self, instance, owner=None):
		if instance is None:
			return self
		elif self.name in getattr(instance, "__dict__", ()):
			return instance.__dict__[self.name]
		elif "_"+self.name in getattr(instance, "__dict__", ()):
			return instance.__dict__["_"+self.name]
		else:
			instance.__dict__["_"+self.name] = ret = self.fget(instance)
			return ret
	
	def __set__(self, instance, value):
		if self.fset is None:
			instance.__dict__[self.name] = value
		else:
			self.fset(instance, value)
	
	def __delete__(self, instance, owner=None):
			if self.fdel is not None:
				self.fdel(instance)
			else:
				if self.name in instance.__dict__:
					del instance.__dict__[self.name]
				if "_"+self.name in instance.__dict__:
					del instance.__dict__["_"+self.name]
	
	def setter(self, fset):
		self.fset = fset
		return self
	
	def deleter(self, fdel):
		self.fdel = fdel
		return self

class ClassProperty:

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

	def __init__(self, func):
		self.func = func

	def __get__(self, instance, owner=None):
		if instance is None and owner is not None:
			if self.name in owner.__dict__:
				return owner.__dict__[self.name]
			ret = self.func(owner)
			setattr(owner, self.name, ret)
			return ret
		else:
			if self.name in instance.__dict__:
				return instance.__dict__[self.name]
			ret = self.func(instance)
			setattr(instance, self.name, ret)
			return ret
	
	def __set__(self, instance, value):
		instance.__dict__ = value
	
	def __delete__(self, instance):
		del instance.__dict__[self.name]

	def __set_name__(self, owner, name):
		self.name = name
		
	def __repr__(self):
		return f"{object.__repr__(self)[:-1]} name={self.name!r}>"