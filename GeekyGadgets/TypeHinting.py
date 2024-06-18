
from typing import *
from types import (GenericAlias, FunctionType, MethodType, MethodWrapperType, MethodDescriptorType, EllipsisType,
				   NoneType, WrapperDescriptorType, ClassMethodDescriptorType, GetSetDescriptorType,
				   MemberDescriptorType)
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Mapping
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

class Number(ABC):
	real : "Number"
	imag : "Number"
	conjugate : "Number"
	@abstractmethod
	def conjugate(self):
		raise NotImplementedError()
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