
from GeekyGadgets.Globals import *
from abc import ABC, abstractmethod

class NewFunctionType(ABC):
	
	def __call__(self, *args, **kwargs):
		return self.func(*args, **kwargs)
NewFunctionType.register(FunctionType)

class NewMethodType(NewFunctionType):
	__self__ : Any
NewMethodType.register(MethodType)

class WrapsFunc(NewFunctionType):
	
	func : tuple[FunctionType]
	MethodClass : type[NewMethodType]

	def __init__(self, func):
		self.func = staticmethod(func)
		self._orig_func_container = (func, )
		update_wrapper(self, self._orig_func_container[0])
	
	def __init_subclass__(cls) -> None:
		cls.__name__ = "function"
		cls.MethodClass = type(cls.__name__+"Method", (WrapsMethod,), {})
		return super().__init_subclass__()
	
	def __get__(self, instance, owner=None):
		return self.MethodClass(self._orig_func_container[0].__get__(instance, owner))

class WrapsMethod(NewMethodType):
	
	func : tuple[MethodType]

	def __init_subclass__(cls) -> None:
		cls.__name__ = "method"
		return super().__init_subclass__()

	def __init__(self, func : MethodType):
		self.func = func
		update_wrapper(self, func.__func__)