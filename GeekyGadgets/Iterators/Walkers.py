
import GeekyGadgets.Globals as _GL

import GeekyGadgets.Illustrative.Graphs as _Graphs
import GeekyGadgets.Configs as _Configs

_E = _GL.TypeVar("_E")
_NOT_SET = object()

class WalkerABC(_GL.ABC):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element."""
	
	iterator : _GL.Iterator[_E]
	
	keyFunc : _GL.Callable[[_E],_GL.Iterator] = iter
	cond : _GL.Callable[[_E],bool] = staticmethod(lambda item: True)
	recurseCond : _GL.Callable[[_E],bool] = staticmethod(lambda item: isinstance(item, _GL.Iterable))

	def __init__(self, iterable : _GL.Iterable, key : _GL.Callable|None=None, cond : _GL.Callable[[_E],bool]|None=None, recurseCond : _GL.Callable[[_E],bool]|None=None):
		if key is not None: self.keyFunc=key
		if cond is not None: self.cond=cond
		if recurseCond is not None: self.recurseCond=recurseCond
		self.iterator = self.recursiveWalk(iterable)
	
	def __iter__(self):
		return self

	def __next__(self) -> _E:
		return next(self.iterator)
	
	@_GL.abstractmethod
	def recursiveWalk(self, iterable) -> _GL.Generator[_E, None, None]:
		raise NotImplementedError()

class DepthFirst(WalkerABC):
	def recursiveWalk(self, iterable) -> _GL.Generator[_E, None, None]:
		for item in self.keyFunc(iterable):
			if self.cond(item):
				yield item
			if self.recurseCond(item):
				yield from self.recursiveWalk(item)
Walker = DepthFirst
class BreadthFirst(WalkerABC):
	def recursiveWalk(self, iterable) -> _GL.Generator[_E, None, None]:
		iterables = [iterable]
		while iterables:
			item = iterables.pop(0)
			if self.cond(item):
				yield item
			if self.recurseCond(item):
				for newItem in self.keyFunc(item):
					iterables.append(newItem)

class ItemWalker(DepthFirst):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are not 
	themselves iterable."""
	
	iterator : _GL.Iterator[_GL.Iterable|_E]

	def __next__(self) -> _E:
		for item in self.iterator:
			if not isinstance(item, _GL.Iterable):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

class BagWalker(DepthFirst):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the 
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are themselves iterable, and not their non-iterable elements.
	"""
	
	iterator : _GL.Iterator[_E]

	def __next__(self) -> _E:
		for item in self.iterator:
			if isinstance(item, _GL.Iterable):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

class SubClassWalker(DepthFirst):
	
	keyFunc = staticmethod(lambda x: iter(x.__subclasses__()))
	recurseCond : _GL.Callable[[_E],bool] = staticmethod(lambda item: True)

#
#	Relevant to Illustrative.Graphs
#

_GE = _GL.TypeVar("_GE", bound=_Graphs.Graph)
class GraphWalker(BreadthFirst):
	"""Does a breadth-first walk, but does not repeat itself by keeping track of the identities of objects it has already yielded."""

	history = _GL.cached_property(lambda self: set())

	def __init__(self : "GraphWalker[_GE]", iterable : _GE, key : _GL.Callable[[_GE],bool]|None=None, cond : _GL.Callable[[_GE],bool]|None=None, recurseCond : _GL.Callable[[_GE],bool]|None=None):
		super().__init__(iterable.root if isinstance(iterable, _Graphs.Graph) else iterable)

	def recurseCond(self, item) -> _GL.Callable[[_E],bool]:
		return id(item) not in self.history and isinstance(item, (_Graphs.Node, _Graphs.Edge))
	
	@staticmethod
	def keyFunc(item : _GE) -> _GL.Iterator:
		return item.walk()

	def recursiveWalk(self, iterable : _GE) -> _GL.Generator[_GE, None, None]:
		for element in super().recursiveWalk(iterable):
			if id(element) not in self.history:
				self.history.add(id(element))
				yield element

class NodeWalker(GraphWalker):
	
	iterator : _GL.Iterator[_E]
	
	@staticmethod
	def cond(item):
		return isinstance(item, _Graphs.Node)

class EdgeWalker(GraphWalker):
	
	iterator : _GL.Iterator[_E]
	
	@staticmethod
	def cond(item):
		return isinstance(item, _Graphs.Edge)

class TreeWalker(BreadthFirst):

	@staticmethod
	def keyFunc(item : _GE) -> _GL.Iterator:
		return item.walk()
	
	@staticmethod
	def recurseCond(item) -> _GL.Callable[[_E],bool]:
		return isinstance(item, (_Graphs.Tree, _Graphs.Leaf, _Graphs.Branch))
	
GraphWalker.register(TreeWalker)

class LeafWalker(TreeWalker):
	
	iterator : _GL.Iterator[_E]
	
	@staticmethod
	def cond(item):
		return isinstance(item, _Graphs.Leaf)

class BranchWalker(TreeWalker):
	
	iterator : _GL.Iterator[_E]

	@staticmethod
	def cond(item):
		return isinstance(item, _Graphs.Branch)
	
class LeafClimber(TreeWalker):
	
	keyFunc = staticmethod(lambda leaf: [leaf.parent])
	recurseCond = staticmethod(lambda leaf: hasattr(leaf.parent, "parent"))

	@staticmethod
	def cond(item):
		return isinstance(item, _Graphs.Leaf)
	
class BranchClimber(TreeWalker):
	
	keyFunc = staticmethod(lambda branch: branch.incoming.incoming)
	recurseCond = staticmethod(
		lambda branch:
			getattr(branch, "incoming", False) 
			and getattr(branch.incoming, "incoming", False)
			and branch.incoming.incoming[0]
	)
	@staticmethod
	def cond(item):
		return isinstance(item, _Graphs.Branch)

#
#	Relevant to Configs.py
#

class ConfigWalker(DepthFirst):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.

	Yields name-value pairs, where the name-value pairs are dependent on the iterator method used:

	* `ConfigWalker.__next__` - Iterates through both categories and variables.
	
	* `ConfigWalker.categories` - Iterates only through categories.
	
	* `ConfigWalker.variables` - Iterates only through variables."""
	
	iterator : _Configs.Config[str,_GL.Any]

	recurseCond = staticmethod(lambda value: isinstance(value, _Configs.ConfigCategory))

	def recursiveWalk(self, iterable : _Configs.Config, root : str=None) -> _GL.Generator[tuple[str,str,_Configs.ConfigCategory|_GL.Any],None,None]:
		for name, value in iterable.items():
			yield (root, name, value)
			if self.recurseCond(value):
				yield from self.recursiveWalk(value, root=f"{root}.{name}" if root is not None else name)
	
	@property
	def categories(self) -> _GL.Generator[tuple[str,str,_Configs.ConfigCategory],None,None]:
		for root, name, value in self:
			if isinstance(value, _Configs.ConfigCategory):
				yield (root, name, value)
	
	@property
	def variables(self) -> _GL.Generator[tuple[str,str,_GL.Any],None,None]:
		for root, name, value in self:
			if not isinstance(value, _Configs.ConfigCategory):
				yield (root, name, value)
