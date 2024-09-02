
import GeekyGadgets.Globals as _Globals

_NOT_SET = object()
_T = _Globals.TypeVar("_T")

def first(iterable, default=_NOT_SET, /):
	if default is _NOT_SET:
		return next(iter(iterable))
	else:
		return next(iter(iterable), default)
def second(iterable, default=_NOT_SET, /):
	if default is _NOT_SET:
		next(_iter := iter(iterable))
		return next(_iter)
	else:
		next(_iter := iter(iterable))
		return next(_iter, default)
def last(iterable, default=_NOT_SET, /):
	x = _NOT_SET
	for x in iterable:
		pass
	return None if x is _NOT_SET else x

_N = _Globals.TypeVar("_N")
_O = _Globals.TypeVar("_O")

@_Globals.overload
def swapAttr(obj : object, attrName : str, new : _N, /) -> _N|_Globals.Any|None: ...
@_Globals.overload
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
	if isinstance(obj, (_Globals.Iterable, _Globals.Iterator)):
		return sum(forceHash(el) for el in obj)
	else:
		return id(obj)

_K = _Globals.TypeVar("_K")
_V = _Globals.TypeVar("_V")
_D = _Globals.TypeVar("_D")
@_Globals.overload
def getitem(d : _Globals.Mapping[_K,_V], key : _K) -> _V: ...
@_Globals.overload
def getitem(d : _Globals.Mapping[_K,_V], key : _K, default : _D) -> _D|_V: ...
def getitem(d, key, default=_NOT_SET):
	if default is _NOT_SET:
		return d[key]
	else:
		try:
			return d[key]
		except KeyError:
			return default

@_Globals.overload
def getAttrChain(obj, key : str, /): ...
@_Globals.overload
def getAttrChain(obj, key : str, default, /): ...
def getAttrChain(obj, key : str, default=_NOT_SET, /):
	if default is _NOT_SET:
		for name in key.split("."):
			obj = getattr(obj, name)
	else:
		for name in key.split("."):
			obj = getattr(obj, name, _NOT_SET)
			if obj is _NOT_SET:
				return default
	return obj

@_Globals.overload
def getReadyAttr(obj, attrName) -> _Globals.Any: ...
@_Globals.overload
def getReadyAttr(obj, attrName, default : _T) -> _Globals.Any|_T: ...
def getReadyAttr(obj, attrName, default=_NOT_SET):
	if default is _NOT_SET:
		if isinstance((value := getattr(obj, attrName)), (property, _Globals.cached_property)):
			raise AttributeError(f"{type(obj)!r} object has a un-determined attribute {attrName!r} value ({value})")
	elif isinstance((value := getattr(obj, attrName, default)), (property, _Globals.cached_property)):
		return default
	return value

def hasReadyAttr(obj, attrName) -> bool:
	try:
		if isinstance(getattr(obj, attrName), (property, _Globals.cached_property)):
			raise AttributeError()
	except AttributeError:
		return False
	return True

def getTypeName(cls : object):
	return object.__getattribute__(object.__getattribute__(cls, "__class__"), "__name__")

def getName(cls : type):
	return object.__getattribute__(cls, "__name__")

def getSubClasses(instance : object|type):
	return instance.__subclasses__ if isinstance(instance, type) else instance.__class__.__subclasses__

def getDescendedClasses(instance : object|type):
	for item in getSubClasses(instance):
		yield item
		yield from getDescendedClasses(item)

from typing import Callable, TypeVar, Any
_R = TypeVar("_R")
def tryExcept(func : Callable[[Any],_R], *args, **kwargs) -> _R|None:
	try:
		return func(*args, **kwargs)
	except:
		return None

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
	if isinstance(cls, tuple):
		return any(isType(instance, part) for part in cls)
	from GeekyGadgets.TypeHinting import GenericAlias, Generic, _GenericAlias

	try:
		return isinstance(instance, cls)
	except TypeError:
		pass
	args, origin = _Globals.get_args(cls), _Globals.get_origin(cls)
	if origin is None:
		return False
	
	if not isinstance(instance, origin):
		return False
	elif issubclass(origin, dict):
		if len(_Globals.get_args(cls)) > 1:
			return all(isType(key, args[0]) and isType(value, args[1]) for key, value in instance.items())
		else:
			return all(isType(value, args[0]) for value in instance.values())
	elif issubclass(origin, _Globals.Iterable):
		if len(args) == 1:
			return all(isType(el, args[0]) for el in instance)
		else:
			return all(isType(el, innerType) for el, innerType in zip(instance, args))
	else:
		return True

def operate(l : Any, o : str, r : Any):
	ret = getattr(l, _Globals.OPERATOR_DUNDER[o], NotImplemented)
	if ret is not NotImplemented:
		ret = ret(r)
	if ret is NotImplemented:
		ret = getattr(r, _Globals.OPERATOR_DUNDER[_Globals.OPERATOR_INVERSE[o]], NotImplemented)
		if ret is not NotImplemented:
			ret = ret(l)
	if ret is NotImplemented:
		raise TypeError(f"unsupported operand type(s) for {o}: '{type(l).__name__}' and '{type(r).__name__}'")
	return ret

def operate(l : Any, o : str, r : Any, strict=True):
	ret = getattr(l, _Globals.OPERATOR_DUNDER[o], NotImplemented)
	if ret is not NotImplemented:
		ret = ret(r)
	if ret is NotImplemented:
		ret = getattr(r, _Globals.OPERATOR_DUNDER[_Globals.OPERATOR_INVERSE[o]], NotImplemented)
		if ret is not NotImplemented:
			ret = ret(l)
	if strict and ret is NotImplemented:
		raise TypeError(f"unsupported operand type(s) for {o}: '{type(l).__name__}' and '{type(r).__name__}'")
	return ret

def parseInt(string : str, _default=None, /):
	try:
		return int(string)
	except:
		return _default

def parseFloat(string : str, _default=None, /):
	try:
		return float(string)
	except:
		return _default

def parseComplex(string : str, _default=None, /):
	try:
		return complex(string)
	except:
		return _default

_FAILURE = object()
def parseNum(string : str, _default=None, /):
	val = parseInt(string, _FAILURE)
	if val is not _FAILURE:
		return val
	val = parseFloat(string, _FAILURE)
	if val is not _FAILURE:
		return val
	val = parseComplex(string, _FAILURE)
	if val is not _FAILURE:
		return val
	return _default

def randomAlpha(length : int=6):
	import GeekyGadgets.Formatting as _Formatting
	return _Formatting.alphabetize(_Globals.random.randint(10**length, 10**(length+1) - 1))

def unzip(iterable : _Globals.Iterable[_T], n : int=2) -> list[list[_T]]:
	iterator = iter(iterable)
	first = next(iterator, None)
	if isinstance(first, _Globals.Iterable):
		ret : list[list[_T]] = []
		for item in first:
			ret.append([item])
		for row in iterator:
			for i, item in enumerate(row):
				ret[i].append(item)
		return ret
	else:
		return [()]*n