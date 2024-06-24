
from typing import *
from types import (GenericAlias, FunctionType, MethodType, MethodWrapperType, MethodDescriptorType, EllipsisType,
				   NoneType, WrapperDescriptorType, ClassMethodDescriptorType, GetSetDescriptorType,
				   MemberDescriptorType)
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from functools import cache
try:
	from builtins import function
except:
	class function: pass
	def f(): ...
	function = type(f)


_T = TypeVar("_T")
_TA = TypeVar("_TA")

class method:
	def __call__(self): ...
method = type(method().__call__)

class MetaTyping(ABCMeta):
	def __repr__(cls):
		return str(cls)
	def __str__(cls):
		return cls.__name__

class MetaType(ABC):
	subclasscheck : Callable[[type|tuple[type]],classmethod|Callable[[type,type],bool]]
	@classmethod
	@cache
	def __class_getitem__(cls, types : tuple[type]|type):
		return MetaTyping(f"{cls.__name__}[{','.join(tp.__name__ for tp in types) if isinstance(types, tuple) else types.__name__}]", (), {"__subclasshook__" : cls.subclasscheck(types)})
	@classmethod
	def __subclasshook__(cls, subClass: type) -> bool:
		return NotImplemented

class Not(MetaType):
	subclasscheck = lambda types: classmethod(lambda cls, subClass: not issubclass(subClass, types))

class All(MetaType):
	subclasscheck = lambda types: classmethod(lambda cls, subClass: all(issubclass(subClass, tp) for tp in types))

class Both(All):
	subclasscheck = lambda types: classmethod(lambda cls, subClass: issubclass(subClass, types[0]) and issubclass(subClass, types[1]))
	@classmethod
	@cache
	def __class_getitem__(cls, types : tuple[type, type]):
		if isinstance(types, tuple) and len(types) == 2:
			return super().__class_getitem__(types)
		else:
			raise ValueError(f"`Both` requires two classes to type check against (`Both[cls1,cls2]`)")
		

class Number(ABC): ...
Number.register(int)
Number.register(float)
Number.register(complex)

class Subscriptable(ABC):
	def __class_getitem__(cls : _T, args : _TA) -> GenericAlias:
		return GenericAlias(cls, args)

class SupportsKeysAndGetItem(ABC):

	@abstractmethod
	def keys(self):
		raise NotImplementedError()
	
	@abstractmethod
	def __getitem__(self):
		raise NotImplementedError()
	
Subscriptable.register(list)
Subscriptable.register(tuple)
Subscriptable.register(dict)
Subscriptable.register(str)
Subscriptable.register(bytes)

class Mode: pass
class ReadMode: pass
class WriteMode: pass
Mode        = Literal["r", "w"]
ReadMode    = Literal["r"]
WriteMode   = Literal["w"]
class Rest(Subscriptable): pass
class All(Subscriptable): pass