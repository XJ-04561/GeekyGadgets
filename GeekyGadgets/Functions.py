
from GeekyGadgets.Globals import *

_NOT_SET = object()

__all__ = ("first", "forceHash", "getAttrChain", "getReadyAttr", "hasReadyAttr", "isThing", "isType")
_T = TypeVar("_T")

def first(iterable):
	return next(iter(iterable), None)
def last(iterable, default=_NOT_SET, /):
	x = _NOT_SET
	for x in iterable:
		pass
	if x is _NOT_SET:
		return None
	else:
		return x

_N = TypeVar("_N")
_O = TypeVar("_O")

@overload
def swapAttr(obj : object, attrName : str, new : _N, /) -> _N|Any|None: ...
@overload
def swapAttr(obj : object, attrName : str, new : _N, default : _O, /) -> _N|_O: ...
def swapAttr(obj : object, attrName : str, new : _N, default : _O=None, /) -> _N|_O:
	old = getattr(obj, attrName, default)
	setattr(obj, attrName, new)
	return old

def forceHash(obj):
	if hasattr(obj, "__hash__"):
		try:
			return hash(obj)
		except TypeError:
			pass
	if isinstance(obj, (Iterable, Iterator)):
		return sum(forceHash(el) for el in obj)
	else:
		return id(obj)

_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")
@overload
def getitem(d : Mapping[_K,_V], key : _K) -> _V: ...
@overload
def getitem(d : Mapping[_K,_V], key : _K, default : _D) -> _D|_V: ...
def getitem(d, key, default=_NOT_SET):
	if default is _NOT_SET:
		return d[key]
	else:
		try:
			return d[key]
		except KeyError:
			return default
	

@overload
def getAttrChain(obj, key : str, /): ...
@overload
def getAttrChain(obj, key : str, default, /): ...
def getAttrChain(obj, key : str, default=_NOT_SET, /):
	if default is _NOT_SET:
		for name in key.split("."):
			obj = getattr(obj, name)
	else:
		for name in key.split("."):
			obj = getattr(obj, name, default)
	return obj


@overload
def getReadyAttr(obj, attrName) -> Any: ...
@overload
def getReadyAttr(obj, attrName, default : _T) -> Any|_T: ...
def getReadyAttr(obj, attrName, default=_NOT_SET):
	if default is _NOT_SET:
		if isinstance((value := getattr(obj, attrName)), (property, cached_property)):
			raise AttributeError(f"{type(obj)!r} object has a un-determined attribute {attrName!r} value ({value})")
	elif isinstance((value := getattr(obj, attrName, default)), (property, cached_property)):
		return default
	return value

def hasReadyAttr(obj, attrName) -> bool:
	try:
		if isinstance(getattr(obj, attrName), (property, cached_property)):
			raise AttributeError()
	except AttributeError:
		return False
	return True

def isThing(thing, cls):
	return isRelated(thing, cls) or isinstance(thing, cls)

def isRelated(cls1 : type|object, cls2 : type) -> bool:
	"""Convenience function which returns True if cls1 is both a type and a subclass of cls2. This is useful because
	attempting issubclass() on an object as first argument raises an exception,  so this can be used instead of
	explicitly typing isinstance(cls1, type) and issubclass(cl1, cls2)"""
	return isinstance(cls1, type) and issubclass(cls1, cls2)

def isType(instance, cls):
	"""Performs `isinstance(instance, cls)` but in the case where `cls` is a `GenericAlias` like `tuple[int,str]`, the 
	typing occurs more recursively. If the origin of `cls` is not a an `Iterable`, then the return value is that 
	of `isinstance(instance, get_origgin(cls))`. When the `GenericAlias` has only one arg, it is assumed that all of 
	the instance's elements are of that type, and returns `False` if not."""
	from GeekyGadgets.TypeHinting import GenericAlias, Generic

	if isinstance(cls, Generic|GenericAlias):
		if not isinstance(instance, get_origin(cls)):
			return False
		elif issubclass(get_origin(cls), dict):
			if len(get_args(cls)) > 1:
				return all(isType(key, get_args(cls)[0]) and isType(value, get_args(cls)[1]) for key, value in instance.items())
			else:
				return all(isType(value, get_args(cls)[0]) for value in instance.values())
		elif isinstance(get_origin(cls), Iterable):
			if len(get_args(cls)) == 1:
				return all(isType(el, get_args(cls)[0]) for el in instance)
			else:
				return all(isType(el, innerType) for el, innerType in zip(instance, get_args(cls)))
		else:
			return True
	else:
		return isinstance(instance, cls)