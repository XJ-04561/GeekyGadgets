
from GeekyGadgets.Globals import *
from pprint import pformat, pprint

@overload
def callFormat(func : Callable, args : tuple[Any]=(), kwargs : dict[str,Any]={}) -> str: ...
@overload
def callFormat(func : Callable, args : tuple[Any]=(), kwargs : dict[str,Any]={}, *, argLength : int=35) -> str: ...
def callFormat(func, args=(), kwargs={}, *, argLength=35):
	
	inner = []
	for arg in args:
		inner.append(str(arg))
		if len(inner[-1]) > argLength:
			inner[-1] = inner[-1][:argLength-3-1] + "..." + inner[-1][-1]
	for name, value in kwargs.items():
		inner.append(str(name)+"="+str(value))
		if len(inner[-1]) > argLength:
			inner[-1] = inner[-1][:argLength-3-1] + "..." + inner[-1][-1]
	
	return f"{getattr(func, '__qualname__', getattr(func, '__name__', func))}({', '.join(inner)})"

def timeFormat(seconds):
	return f"{seconds//3600:0>2.0f}:{(seconds//60)%60:0>2.0f}:{seconds%60:0>6.3f}"
