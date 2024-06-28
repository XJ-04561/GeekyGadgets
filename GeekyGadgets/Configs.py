
from GeekyGadgets.Globals import *
if PYTHON_VERSION < (3, 11):
	import toml # type: ignore
else:
	import tomllib as toml # type: ignore

__all__ = ("loadTOML", "Config", "ConfigCategory")

_NOT_SET = object()
_NO_DEFAULT = object()
_NOT_FOUND = object()
_NO_TYPE = type("_NO_TYPE", (), {})
_D = TypeVar("_D", bound=dict[str,Any])

class FlagNotFound(KeyError):
	def __init__(self, flag : str, config : Union["Config","ConfigCategory"]) -> None:
		super().__init__(f"Flag {flag!r} not found in {config!r}.")

class Config(dict):
	"""A `dict`-like object that stores values and sub-categories under a given `str` object denoted as *flags*. 
	`ConfigCategory` objects directly inherit from `Config`. No `Config` object should contain other `Config` objects, 
	only `ConfigCategory` objects.
	
	A flag/category can be accessed either by it's name, or the hierarchy it is under plus its name. Hierachy is 
	indicated by separating flags with `.`, like: `gameConfig["video_options.driver.version"] == 535`.

	When not specifying hierarchy, it is assumed to be a top-level name of a category or a variable, if not, then 
	the entire config is recursively walked to find all flags with that name. If the name only appears once, the 
	value is returned as is. If multiple entries of that name are found, a dict is returned, where the keys are 
	the hierarchies of each found entry (Without the flag name appended), and the values are the values of each 
	found entry.
	### Example
	```python
	config = Config({
		"version" : 1.0,
		"video_options" : {
			"resolution" : (1080, 1920),
			"anti_aliasing" : "FXAA",
			"frequency" : 60, # Hz/FPS
			"driver" : {
				"name" : "nvidia",
				"version" : 535
			}
		},
		"controls" : {
			"mouse" : {
				"frequency" : 1000,
				"sensitivity" : 1.2
			},
			"keyboard" : {
				"forward" : 87,
				"backward" : 83,
				"left" : 65,
				"right" : 68,
				"jump" : 32
			}
		}
	})

	print(config["version"])
	>>> 1.0

	print(config["video_options"])
	>>> {'resolution': (1080, 1920), 'anti_aliasing': 'FXAA', 'frequency' : 60}
	
	print(config["controls.mouse.sensitivity"])
	>>> 1.2
	
	print(config["frequency"])
	>>> {'video_options': 60, 'controls.mouse': 1000}
	```
	"""

	_LOCK : threading.Lock
	CATEGORY_CLASS : type["ConfigCategory"]
	_DEFAULT : Any
	
	@overload
	def __init__(self, iterable : Iterable[tuple[str,Any]], /): ...
	@overload
	def __init__(self, dictLike : Dict[str,Any], /): ...
	@overload
	def __init__(self, iterable : Iterable[tuple[str,Any]], /, *, default): ...
	@overload
	def __init__(self, dictLike : Dict[str,Any], /, *, default): ...
	@overload
	def __init__(self, /, **kwargs : Any): ...

	def __init__(self, iterable=_NOT_SET, /, **kwargs):

		self._LOCK = threading.RLock()

		if iterable is not _NOT_SET and (tuple(kwargs) != ("default",) and kwargs):
			super().__init__(iterable, **kwargs)
			self._DEFAULT = kwargs.get("default", _NO_DEFAULT)
		elif iterable is not _NOT_SET:
			super().__init__(iterable)
			self._DEFAULT = kwargs.get("default", _NO_DEFAULT)
		else:
			super().__init__(**kwargs)
			self._DEFAULT = _NO_DEFAULT
	
	@overload
	def fromDict(cls : type["Config"], d : dict) -> "Config": ...
	@overload
	def fromDict(cls : type["Config"], d : dict, *, default : Any) -> "Config": ...
	@overload
	def fromDict(cls : type["ConfigCategory"], d : dict) -> "ConfigCategory": ...
	@overload
	def fromDict(cls : type["ConfigCategory"], d : dict, *, default : Any) -> "ConfigCategory": ...
	@classmethod
	def fromDict(cls, d, *, default=_NO_DEFAULT, obj : "Config"=None):
		"""Converts a dict to a `Config` object, with all underlying dictionaries being converted 
		to `ConfigCategory` objects."""
		if obj is None:
			obj = cls((), default=default)
		categoryType = getattr(d, "CATEGORY_CLASS", dict)
		if isinstance(d, Dict):
			iterator = d.items()
		elif isinstance(d, Iterator):
			iterator = d
		else:
			iterator = iter(d)

		for name, value in iterator:
			if isinstance(value, categoryType):
				if name not in obj or not isinstance(obj[name], obj.CATEGORY_CLASS):
					obj[name] = obj.CATEGORY_CLASS((), default=obj._DEFAULT)
				obj.CATEGORY_CLASS.fromDict(value, default=obj._DEFAULT, obj=obj[name])
			else:
				obj[name] = value
		
		return obj

	@overload
	def __getitem__(self, flag : str) -> Any: ...
	@overload
	def __getitem__(self, flag : str, *, default : Any) -> Any: ...
	def __getitem__(self, flag : str, *, default=_NO_DEFAULT) -> Any:
		"""Get the value of a settings flag or an entire category by its name.
		
		A flag/category can be accessed either by it's name, or its full full name. The full name is the full 
		hierarchy under which the flag lies. Hierachy is indicated by separating flags with `.`, 
		like: `"main.sub.subsub.variable"`.

		When not specifying hierarchy, it is assumed to be a top-level name of a category or a variable, if not, then 
		the entire config is recursively walked to find all flags with that name. If the name only appears once, the 
		value is returned as is. If multiple entries of that name are found, a dict is returned, where the keys are 
		the hierarchies of each found entry (Without the flag name appended), and the values are the values of each 
		found entry.
		"""
		default = default or self._DEFAULT

		with self._LOCK:
			if "." in flag:
				first, rest = flag.split(".", 1)

				if first in self.main and isinstance(self[first], self.CATEGORY_CLASS):
					return self[first].__getitem__(rest, default=default)
				elif default is not _NO_DEFAULT:
					return default
				else:
					raise FlagNotFound(flag, self)
			elif flag in self.main:
				return super().__getitem__(flag)
			else:
				res = {}
				for root, name, value in self.walk():
					if name == flag:
						res[root] = value
				if len(res) == 1:
					return next(res.values())
				elif res:
					return res
				elif default is not _NO_DEFAULT:
					return default
				else:
					raise FlagNotFound(flag, self)
	
	def __contains__(self, flag : str):
		with self._LOCK:
			if self.__getitem__(flag, default=_NOT_FOUND) is _NOT_FOUND:
				return False
			else:
				return True

	def __setitem__(self, flag : str, value : Any):
		with self._LOCK:
			if "." in flag:
				first, rest = flag.split(".", 1)
				if first not in self.main:
					super().__setitem__(first, self.CATEGORY_CLASS((), default=self._DEFAULT))
				
				self[first][rest] = value
				# Should raise case-specific exception. If self[first] is a list, TypeError will be raised, if self[first]
				# is a dict, KeyError *might* be raised, etc. etc.
			else:
				super().__setitem__(flag, value)

	def __str__(self):
		return f"{{{', '.join(map(lambda x:': '.join(map(repr, x)), self.items()))}}}"
	
	def __repr__(self):
		return str(self)

	def walk(self) -> "ConfigWalker":
		from GeekyGadgets.Iterators import ConfigWalker
		return ConfigWalker(self)
	
	def __getattr__(self, name : str):
		"""Returns the results of `self[name]`"""
		with self._LOCK:
			if name in self.walk():
				return self[name]
			else:
				return self.__getattribute__(name) # Called to raise appropriate error.
	
	def __or__(self, other : dict):
		if not isinstance(other, dict):
			return NotImplemented
		
		obj = self.fromDict(self, default=self._DEFAULT)
		self.fromDict(other, obj=obj)

		return obj
	
	def __ror__(self, other : dict):
		if not isinstance(other, dict):
			return NotImplemented
		
		obj = self.fromDict(other, default=getattr(other, "_DEFAULT", self._DEFAULT))
		self.fromDict(self, obj=obj)

		return obj
	
	def __ior__(self, other : dict):
		if not isinstance(other, dict):
			return NotImplemented
		
		self.fromDict(other, obj=self)

		return self

	def update(self, other : dict=_NOT_SET, **kwargs):
		if isinstance(other, dict):
			self |= other
		elif other is not _NOT_SET:
			self |= dict(other)
		
		if kwargs:
			self.update(kwargs)
	
	def get(self : "Config", flag : str, default=_NO_DEFAULT, /) -> Any:
		"""Attempts config[key] and if flag is not found, will first try to return the default value keyword argument. 
		If default is not given, the instances own default value is returned. If no instance default value has been 
		set, then None is returned."""
		if "." in flag:
			first, rest = flag.split(".", 1)
			with self._LOCK:
				if first in self.main and isinstance(self[first], self.CATEGORY_CLASS):
					return self[first].get(rest, default)
				elif default is not _NO_DEFAULT:
					return default
				elif self._DEFAULT is not _NO_DEFAULT:
					return self._DEFAULT
				else:
					return None
		else:
			return super().get(flag, default if default is not _NO_DEFAULT else \
									self._DEFAULT if self._DEFAULT is not _NO_DEFAULT else None)
	
	def setdefault(self, flag, default=None):
		if "." in flag:
			first, *rest = flag.split(".", 1)
			with self._LOCK:
				if first in self.main:
					self[first].setdefault(rest, default)
				else:
					self[first] = self.CATEGORY_CLASS((), default=self._DEFAULT)
					self[first].setdefault(rest, default)
		else:
			super().setdefault(flag, default)

	@property
	def main(self) -> tuple[str]:
		return tuple(super().keys())
	
	@property
	def categories(self) -> Generator[tuple[str,"ConfigCategory"],None,None]:
		from GeekyGadgets.Iterators import ConfigWalker
		for root, name, value in ConfigWalker(self).categories:
			yield (name, value)
	
	@property
	def variables(self) -> Generator[tuple[str,Any],None,None]:
		from GeekyGadgets.Iterators import ConfigWalker
		for root, name, value in ConfigWalker(self).variables:
			yield (name, value)

class ConfigCategory(Config): pass

Config.CATEGORY_CLASS = ConfigCategory

@overload
def loadTOML(filename) -> Config[str,Any]: ...
@overload
def loadTOML(filename, dictType : type[_D]=Config) -> _D: ...
def loadTOML(filename, dictType=Config):
	if PYTHON_VERSION < (3, 11):
		return dictType(toml.load(filename, _dict=dictType.CATEGORY_CLASS))
	else:
		with open(filename, "rb") as f:
			return dictType.fromDict(toml.load(f))

try:
	from GeekyGadgets.Iterators import ConfigWalker
except ImportError:
	pass