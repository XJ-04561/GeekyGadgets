
from typing import Any
from GeekyGadgets.Globals import *
from abc import ABC, ABCMeta

class FunctionMeta(ABCMeta):

	def __new__(mcls: type[Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwargs: Any) -> Self:
		"""Makes sure that the new classes have the same name as the function/method that is set through 
		the `__base__` attribute."""
		if "__base__" in namespace:
			if not hasattr(namespace["__base__"], "__name__"):
				raise TypeError(f"Can't create {name!r} type as its `__base__` attribute does not have a `__name__` attribute.")
			return super().__new__(mcls, namespace["__base__"].__name__, bases, namespace, **kwargs)
		elif any(hasattr(base, "__base__") for base in bases):
			for base in bases:
				if hasattr(base, "__base__"):
					if not hasattr(base.__base__, "__name__"):
						raise TypeError(f"Can't create {name!r} type as the inherited `__base__` attribute inherited from `{base}` does not have a `__name__` attribute.")
					return super().__new__(mcls, base.__base__.__name__, bases, namespace, **kwargs)
		else:
			raise ValueError(f"Can't create {name!r} type as it does not have a `__base__` attribute set to a type object.")

class Function(ABC, metaclass=FunctionMeta):
	
	__method_class__ : type["Method"]
	__base__ = function
	__func__ : function

	@overload
	def __init__(self : "Function", func : function): ...
	@overload
	def __init__(self : "Method", func : method): ...
	def __init__(self : "Function|Method", func : function|method):
		self.__func__ = func
		update_wrapper(self, func)

	def __call__(self, *args, **kwargs):
		return self.__func__(*args, **kwargs)
	
	def __init_subclass__(cls, *args, **kwargs) -> None:
		if cls.__method_class__ is not None and "__method_class__" not in cls.__dict__:
			cls.__method_class__ = FunctionMeta(cls.__qualname__.split(".")[-1]+"Method", (cls,), {"__base__" : method, "__method_class__" : None})
		return super().__init_subclass__(*args, **kwargs)
	
	def __subclasshook__(cls : type, other : type) -> bool:
		return issubclass(other, cls.__base__)
	
	def __get__(self, instance, owner=None):
		try:
			return self.__method_class__(self.__func__.__get__(instance, owner))
		except:
			return self.__method_class__(self.__func__.__get__(instance))

class Method(Function):

	__method_class__ = None
	__base__ = method
	__func__ : method
Function.__method_class__ = Method