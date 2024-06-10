
from GeekyGadgets.Globals import *

_NOT_SET = object()

__all__ = ("first", "forceHash", "getAttrChain", "getReadyAttr", "hasReadyAttr", "isThing", "isType")

def first(iterator):
	for item in iterator:
		return item
	return None

def forceHash(obj):
	if hasattr(obj, "__hash__"):
		try:
			return hash(obj)
		except TypeError:
			pass
	if isinstance(obj, Iterable):
		return sum(forceHash(el) for el in obj)
	else:
		return id(obj)

def getAttrChain(obj, key, default=_NOT_SET):
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
	
	try:
		from typing import GenericAlias
	except:
		from types import GenericAlias
	if isinstance(instance, type):
		if not isinstance(cls, Generic|GenericAlias):
			return isRelated(instance, cls)
		if not hasattr(instance, "__iter__"):
			return False
		if not isRelated(instance, get_origin(cls)):
			return False
		
		args = get_args(cls)
		if isinstance(args[0], Generic|GenericAlias) and get_origin(args[0]) is All:
			args = itertools.repeat(Union[get_args(args[0])])
		elif sum(1 for _ in instance) < len(args)-1:
			return False
		elif isinstance(args[-1], Generic|GenericAlias) and get_origin(args[-1]) is Rest:
			args = itertools.chain(args[:-1], itertools.repeat(Union[get_args(args[-1])]))
		elif sum(1 for _ in instance) != len(args):
			return False
		
		for item, tp in zip(instance, get_args(cls), strict=True):
			if not isType(item, tp):
				return False
		return True
	elif isinstance(cls, Generic|GenericAlias):
		if isinstance(instance, type):
			return isRelated(instance, cls)
		if not isType(instance, get_origin(cls)):
			return False
		if isType(instance, dict):
			keys, values = get_args(cls)
			return all(isinstance(key, keys) for key in instance) and all(isinstance(value, values) for value in instance.values())
		
		args = get_args(cls)
		if get_origin(args[0]) is All:
			args = itertools.repeat(Union[get_args(args[0])])
		elif get_origin(args[-1]) is Rest:
			args = itertools.chain(args[:-1], itertools.repeat(Union[get_args(args[-1])]))
		
		for v, tp in zip(instance, args):
			if not isType(v, tp):
				return False
		return True
	else:
		return isinstance(instance, cls)