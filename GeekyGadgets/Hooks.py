
from GeekyGadgets.Globals import *
from GeekyGadgets.Logging import Logged
from GeekyGadgets.Functions import forceHash
from GeekyGadgets.Iterators import TakeWhile
import itertools
from GeekyGadgets.Threads import Thread, current_thread
from queue import Queue, Empty as EmptyQueueException

__all__ = ("HookBaitingException", "Hook", "DummyHooks", "Hooks", "Bait", "GlobalHooks")

class HookBaitingException(Exception): pass

class Hook:

	target : Callable
	args : tuple
	kwargs : dict

	def __init__(self, target, args=(), kwargs={}):
		self.target = target
		self.args = args
		self.kwargs = kwargs
	
	def __call__(self, eventInfo : dict):
		self.target(eventInfo, *self.args, **self.kwargs)
	
	def __hash__(self):
		return forceHash((self.target, self.args, self.kwargs))
	
	def __eq__(self, other):
		return hash(self) == hash(other)

class DummyHooks:

	_eventQueue : Queue[tuple[str,dict]]
	_hooks : dict[str, set[Hook]]
	_worker : Thread
	RUNNING : bool

	def addHook(self, category : str, /, target : Callable, args : tuple=(), kwargs : dict={}) -> Hook:
		return Hook(lambda *args, **kwargs : None, args=args if hasattr(args, "__hash__") else tuple(args), kwargs=kwargs)
	
	def removeHook(self, category : str, /, hook : Hook) -> bool:
		return True

	def trigger(self, category : str, /, eventInfo : dict):
		pass

class Hooks(Logged):
	"""
	eventInfo should look like:
		*name* - This can be any string. But is used together with the identity of the 'instance' to make the trigger precise in its targeting.
		
		*instance* - The instance which triggered the event, or the instance relevant to the event.
		
		*owner* - The class type of the 'instance'.
		
		*value* - The value which the event is reporting.
		
		_ - All other keywords are available for use, but should not be on relied on for identification or value-passing when the 'value' key is available.
	"""

	_eventQueue : Queue[tuple[str,dict]]
	_hooks : dict[str, set[Hook]]
	_worker : Thread
	RUNNING : bool

	def __init__(self):
		self._hooks = {}
		self._eventQueue = Queue()
		self.RUNNING = True
		self._worker = Thread(target=self.mainLoop, daemon=True)
		self._worker.start()
	
	def __del__(self):
		self.RUNNING = False
	@overload
	def addHook(self, category : str, /, hook : Hook) -> Hook: ...
	@overload
	def addHook(self, category : str, /, target : Callable, args : tuple=(), kwargs : dict={}) -> Hook: ...
	def addHook(self, category : str, /, target : Callable, args : tuple=(), kwargs : dict={}) -> Hook:
		
		if isinstance(target, Hook):
			hook = target
		else:
			args = args if hasattr(args, "__hash__") else tuple(args)
			self.LOG.debug(f"Adding Hook to {self}. Hook has: {category=}, {target=}, {args=}, {kwargs=}")
			
			hook = Hook(target, args, kwargs)
		
		if category not in self._hooks:
			self._hooks[category] = set()
		self._hooks[category].add(hook)
		
		return hook
	
	def removeHook(self, category : str, /, hook : Hook) -> bool:
		"""Removes all occurances of the hook in the list of hooks associated with the category"""
		# Essentially a while True: but limited to at least iterations as long as the hooks list.
		if hook in self._hooks.get(category, set()):
			self._hooks[category].remove(hook)
			return True
		else:
			return False
	
	def trigger(self, category : str|tuple, eventInfo : dict):
		
		if isinstance(category, str):
			self.LOG.debug(f"Event triggered: {category=}, {eventInfo=}")
			self._eventQueue.put((category, eventInfo))
		elif isinstance(category, tuple):
			for name in category:
				self.LOG.debug(f"Event triggered: {name=}, {eventInfo=}")
				self._eventQueue.put((name, eventInfo))
		else:
			self.LOG.exception(TypeError(f"category must be either a str or a tuple of str. not {category!r}\n{eventInfo=}"))
			raise TypeError(f"category must be either a str or a tuple of str. not {category!r}\n{eventInfo=}")
	
	def mainLoop(self):
		
		while self.RUNNING:
			try:
				category, eventInfo = self._eventQueue.get(timeout=2)
				if self._hooks.get(category): 
					for hook in TakeWhile(lambda x:self.RUNNING, self._hooks.get(category, [])):
						try:
							hook(eventInfo)
						except Exception as e:
							e.add_note(f"This occurred while calling the hook {hook!r} tied to {category=} with {eventInfo=}")
							self.LOG.exception(e)
				else:
					self.LOG.info(f"{category=} triggered, but no hooks registered in {self!r}")
			except EmptyQueueException:
				pass
			except Exception as e:
				e.add_note(f"This exception occurred in hooks thread '{getattr(current_thread(), 'name', 'N/A')}'")
				self.LOG.exception(e)
		self.LOG.info(f"Hooks thread {getattr(current_thread(), 'name', 'N/A')} stopped running")


class Bait(Logged):
	"""

	"""

	name : str = None
	category : str|tuple[str] = None
	eventInfo : dict = None
	owner : type = None
	attributeName : str = None
	_property : property = None

	def __init__(self, *, name : str=None, category : str=None, eventInfo : dict=None):
		
		self.category = category or self.category
		self.eventInfo = eventInfo or self.eventInfo or {}
		self.name = name or self.name
		self.eventInfo.setdefault("name", self.name)
	
	def __class_getitem__(cls, name : str):
		
		return cls(name=name)
	
	def __getitem__(self, categories : str|tuple[str]):
		
		return type(self)(name=self.name, category=categories)
	
	def __call__(self, fget=None, fset=None, fdel=None, doc=None):
		
		if isinstance(fget, property):
			self._property = fget
		else:
			self._property = property(fget=fget, fset=fset, fdel=fdel, doc=doc)
	
	def __get__(self, instance):
		
		if self.name in instance.__dict__:
			return instance.__dict__[self.name]
		else:
			raise AttributeError(f"{type(instance).__name__!r} object has no attribute {self.name!r}")

	def __set__(self, instance, value):
		
		instance.__dict__[self.name] = value
		getattr(instance, "hooks").trigger(self.category, self.eventInfo | {"value" : value, "instance" : instance})
	
	def __set_name__(self, owner : type, name : str):
		
		if not hasattr(owner, "hooks") and "hooks" not in owner.__annotations__ and "hooks" not in owner.__init__.__code__.co_varnames[:owner.__init__.__code__.co_argcount]:
			raise HookBaitingException("Can't lay bait on an attribute belonging to a class that does not have a 'hooks' attribute. ('hooks' is determined through class attribute lookup, class annotation lookup, and __init__ function arguments names)")
		self.category = self.category or f"{owner.__name__}{name.capitalize()}"
		self.eventInfo["owner"] = self.owner = owner
		self.eventInfo["attribute"] = self.attributeName = name
		self.eventInfo.setdefault("name", name)

	
	def __delete__(self, instance):
		
		del instance.__dict__[self.name]

	def __repr__(self):
		
		return f"<Baited {type(self._property).__name__ if self._property else 'Attribute'} '{self.owner.__name__}.{self.attributeName}' on {self.category!r} with {self.eventInfo!r}>"
	
	def setter(self, func):
		
		if self._property:
			self._property.setter(func)
		else:
			self._property = property(fset=func)
		
	def deleter(self, func):
		
		if self._property:
			self._property.deleter(func)
		else:
			self._property = property(fdel=func)

GlobalHooks = Hooks()

class HookedContainer:
	
	def __init__(self, *args, hooks : Hooks=GlobalHooks, **kwargs) -> None:
		self.hooks = hooks
		super().__init__(*args, **kwargs)

	def __setitem__(self, key, value):
		
		try:
			old = self[key]
			existed = True
		except:
			existed = False
		
		super().__setitem__(key, value)

		if existed and old != value:
			self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Changed", "value" : (key, value)})
		elif not existed:
			self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Added", "value" : (key, value)})	
		
	def __delitem__(self, key):
		
		try:
			old = self[key]
			existed = True
		except:
			existed = False
		
		super().__delitem__(key)
		
		if existed:
			self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : (key, old)})

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_NOT_SET = object()

class HookedDict(HookedContainer, dict):
	
	@overload
	def setdefault(self: "HookedDict[_KT, Any | None]", key: _KT, default: None = None, /) -> (Any | None): ...
	@overload
	def setdefault(self: "HookedDict[_KT, _VT]", key: _KT, default: _VT, /) -> _VT: ...
	def setdefault(self, key, default= None, /):
		if key in self:
			super().setdefault(key, default)
			self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Added", "value" : self[key]})
		else:
			super().setdefault(key, default)

	@overload
	def pop(self: dict, key: Any, /) -> Any: ...
	@overload
	def pop(self: dict, key: Any, default: Any, /) -> Any: ...
	@overload
	def pop(self: dict, key: Any, default: _T, /) -> (Any | _T): ...
	def pop(self, key, default=_NOT_SET, /):
		existed = key in self
		if default is _NOT_SET:
			ret = super().pop(key)
		else:
			ret = super().pop(key, default)
		if existed:
			self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : (key, ret)})
		return ret

	def popitem(self) -> tuple:
		ret = super().popitem()
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : ret})
		return ret
	

class HookedList(HookedContainer, list):
	
	def append(self, object: Any) -> None:
		index = len(self)
		super().append(object)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Added", "value" : (index, object)})
	
	def extend(self, iterable: Iterable) -> None:
		index = len(self)
		super().extend(iterable)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Added", "values" : list(zip(range(index, len(iterable)), iterable))})
	
	def reverse(self) -> None:
		super().reverse()
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Changed"})

	def pop(self, index: SupportsIndex = -1) -> Any:
		ret = super().pop(index)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : (index, ret)})
		return ret
	
	def insert(self, index: SupportsIndex, object: Any) -> None:
		super().insert(index, object)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Added", "value" : (index, object)})
	
	def remove(self, value: Any) -> None:
		if value in self:
			index = self.index(value)
		super().remove(value)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : (index, value)})

class HookedSet(HookedContainer, set):
	
	def add(self, element: Any) -> None:
		existed = element in self
		super().add(element)
		if not existed:
			self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Added", "value" : element})
	
	def update(self, *s: Iterable) -> None:
		super().update(*s)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Update", "values" : s})
	
	def difference_update(self, *s: Iterable[Any]) -> None:
		super().difference_update(*s)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "DifferenceUpdate", "values" : s})

	def intersection_update(self, *s: Iterable[Any]) -> None:
		super().intersection_update(*s)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "IntersectionUpdate", "values" : s})

	def symmetric_difference_update(self, s: Iterable) -> None:
		super().symmetric_difference_update(s)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "SymmetricDifferenceUpdate", "value" : s})

	def pop(self) -> Any:
		ret = super().pop()
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : ret})
		return ret
	
	def discard(self, element: Any) -> None:
		super().discard(element)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : element})
	
	def remove(self, element: Any) -> None:
		super().remove(element)
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "value" : element})

	def clear(self) -> None:
		super().clear()
		self.hooks(f"{self.__class__.__name__}", {"name" : id(self), "type" : "Removed", "values" : self.copy()})

class ProgressHook:

	category : str
	hooks : Hooks
	name : str
	def __init__(self, category : str, hooks : Hooks, name : str):
		self.category = category
		self.hooks = hooks
		self.name = name

	def __call__(self, progress : float):
		"""
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		if progress == None:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Failed"})
		elif progress == 2:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Skipped"})
		elif progress == 3:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Finished"})
		elif 0 <= progress < 1:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Progress", "value" : progress})
		elif progress <0:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Starting"})
		elif progress == 1.0:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "PostProcess"})
		else:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Failed"})
	
	def Starting(self): self.hooks.trigger(self.category, {"name" : self.name, "type" : "Starting"})
	def Progress(self, progress : float): self.hooks.trigger(self.category, {"name" : self.name, "type" : "Progress", "value" : progress})
	def PostProcess(self): self.hooks.trigger(self.category, {"name" : self.name, "type" : "PostProcess"})
	def Failed(self): self.hooks.trigger(self.category, {"name" : self.name, "type" : "Failed"})
	def Skipped(self): self.hooks.trigger(self.category, {"name" : self.name, "type" : "Skipped"})
	def Finished(self): self.hooks.trigger(self.category, {"name" : self.name, "type" : "Finished"})