
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
	
	_orig_func_container : tuple[FunctionType]

	func : tuple[FunctionType]
	MethodClass : type[NewMethodType]

	def __init__(self, func):
		self.func = staticmethod(func)
		self._orig_func_container = (func, )
		print(repr(func.__name__))
		print(repr(func.__qualname__))
		update_wrapper(self, func)
		self.__name__ = func.__name__ or func.__qualname__
		self.__qualname__ = func.__name__ or func.__qualname__
	
	def __init_subclass__(cls) -> None:
		cls.MethodClass = type(cls.__name__+"Method", (WrapsMethod,), {})
		cls.__name__ = "function"
		return super().__init_subclass__()
	
	def __get__(self, instance, owner=None):
		return self.MethodClass(self._orig_func_container[0].__get__(instance, owner))

class WrapsMethod(NewMethodType):
	
	_orig_func_container : tuple[MethodType]
	
	func : tuple[MethodType]

	def __init_subclass__(cls) -> None:
		cls.__name__ = "method"
		return super().__init_subclass__()

	def __init__(self, func : MethodType):
		self.func = func
		update_wrapper(self, func.__func__)
		self.__name__ = func.__func__.__name__ or func.__func__.__qualname__
		self.__qualname__ = func.__func__.__name__ or func.__func__.__qualname__