
from typing import Any
from GeekyGadgets.Globals import *

_NOT_SET = object()
_NO_DEFAULT = object()

if PYTHON_VERSION < (3, 11):
	import toml
else:
	import tomllib as toml

class Config(dict):
	
	CATEGORY_CLASS : type
	_DEFAULT : Any
	
	@overload
	def __init__(self, iterable : Iterable[tuple[str,Any]]): ...
	@overload
	def __init__(self, iterable : Dict[str,Any]): ...
	@overload
	def __init__(self, iterable : Iterable[tuple[str,Any]], *, default): ...
	@overload
	def __init__(self, iterable : Dict[str,Any], *, default): ...

	def __init__(self, iterable, *, default=_NO_DEFAULT):
		if isinstance(iterable, Dict):
			iterator = iterable.items()
		else:
			iterator = iter(iterable)
		self._DEFAULT = default

		for name, value in iterator:
			if isinstance(value, Dict):
				self[name] = self.CATEGORY_CLASS(value)
			else:
				self[name] = value

	def __getitem__(self, name : str):
		if "." in name:
			swap = self
			oname = name
			*queue, final = name.split(".")
			for name in queue:
				for flag, value in swap.items():
					if name == flag and isinstance(value, Category):
						swap = value
						break
				else:
					break
			else:
				res = swap.get(final, self._DEFAULT)
				if res is _NO_DEFAULT:
					raise KeyError(f"Variable {oname!r} not found in {self!r}")
				else:
					return res
		elif name in self.categories:
			return super().__getitem__(name)
		else:
			from GeekyGadgets.Iterators import ConfigWalker
			for flag, value in ConfigWalker(self):
				if name == flag:
					return value
		return self.default
	
	def __getattr__(self, name : str):
		"""Returns the results of `self[name]`"""
		return self[name]
	
	@property
	def categories(self):
		return super().keys()
	
class Category(Config): pass
Config.CATEGORY_CLASS = Category

def loadTOML(filename) -> Config[str,Any]:
	if PYTHON_VERSION < (3, 11):
		return Config(toml.load(filename))
	else:
		with open(filename, "rb") as f:
			return Config(toml.load(f, ))
