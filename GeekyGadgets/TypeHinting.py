
from typing import *
from typing import _GenericAlias, Any
from types import (GenericAlias, FunctionType, MethodType, MethodWrapperType, MethodDescriptorType, EllipsisType,
				   NoneType, WrapperDescriptorType, ClassMethodDescriptorType, GetSetDescriptorType,
				   MemberDescriptorType)
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from functools import cache, wraps
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
class mappingproxy: ...
mappingproxy = type(object.__dict__)

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


class Interval(type):
	left : str = "["
	right : str = "]"

	start : Number
	stop : Number
	
	def __class_getitem__(cls : _T, args : _TA) -> "Interval":
		obj = cls("Interval", (cls, ), {})
		obj.start = args[0]
		obj.stop = args[1]
		return obj
	def __str__(self):
		return f"Interval {self.left}{self.stop}, {self.start}{self.right}"

class Interval_LR(type):
	left : str = "["
	right : str = "]"
class Interval_Lr(type):
	left : str = "["
	right : str = ")"
class Interval_lR(type):
	left : str = "("
	right : str = "]"
class Interval_lr(type):
	left : str = "("
	right : str = ")"

class Bytes(Subscriptable): ...

# class Mapping(ABC):

# 	@abstractmethod
# 	def keys(self):
# 		raise NotImplementedError()
	
# 	@abstractmethod
# 	def __getitem__(self):
# 		raise NotImplementedError()
	
Subscriptable.register(list)
Subscriptable.register(tuple)
Subscriptable.register(dict)
Subscriptable.register(str)
Subscriptable.register(bytes)

class Index(ABC): ...
Index.register(int)
Index.register(slice)
Index.register(slice)

class Mode: pass
class ReadMode: pass
class WriteMode: pass
Mode        = Literal["r", "w"]
ReadMode    = Literal["r"]
WriteMode   = Literal["w"]
class Rest(Subscriptable): pass
class All(Subscriptable): pass

import os
class module(type(os), Subscriptable):
	__module__ = None

class HasAttrBase(Subscriptable, ABC):
	ATTRS : tuple[str] = ()
	@classmethod
	def __subclasshook__(cls: ABCMeta, other: type) -> bool:
		for name in cls.ATTRS:
			if getattr(other, name, None) is None:
				return False
		else:
			return True

class HasAttr(HasAttrBase):
	def __class_getitem__(self, names : str|tuple[str]):
		return HasAttrBase.__class__("HasAttrRuntime", (HasAttrBase,), {"ATTRS" : names if isinstance(names, tuple) else (names, )})
