
from GeekyGadgets.Globals import *

_NOT_SET = object()

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