"""## This

A `this` statement (class) that is inspired by the `this` statement in JavaScript, but works a bit differently.


When you need a function/lambda/callback that just simply accesses an object's attributes & methods, simply put `this` 
there and do on it what you would want done on each object in your iterable. But you must finish it by putting 
star/asterisk (`*`) in front of it, that makes it compile the defined expression as a function and returns a callable 
object which performs the given expression and returns the output.

### Javascript reference:
```js
function(){return this.myMethod().myAttr}
// Or
(obj) => obj.myMethod().myAttr
```
### Python reference:
```python
lambda obj : obj.myMethod().myAttr
```
### This package:
```python
class this: pass
this.myMethod().myAttr}
```
## Example Usage:
```python
from This import this

myList = ["Apple", "Lion", "Tennis"]
myMixedList = ["Apple", 12, b"\x03Oo"]
for item in map(*this.lower(), myList):
	print(item)
# apple
# lion
# tennis

for item in map(*this.lower(), filter(*this.__class__ == str, myMixedList)):
	print(item)
# apple
```
"""


from typing import Any, Callable
import ast
from ast import Assign, Attribute, Call, Subscript, BinOp, UnaryOp, Compare
from ast import arg as Argument, keyword as Keyword
from functools import cached_property, cache

__all__ = ("this",)

class this: pass
class ThisContainer:
	nodeTree : ast.AST = None
	values : dict[int,Any]
	add : Callable

oGet = object.__getattribute__
def container(self) -> ThisContainer:
	return oGet(self, "container")
CONTAINER_NAME = "_refs"

def isConstant(value):
	if isinstance(value, (type(None), str, bytes, bool, int, float, complex, type(...))):
		return True
	elif isinstance(value, (tuple, set)):
		for el in value:
			if not isConstant(el):
				return False
		return True
	else:
		return False

def createOperation(self, right=None, op=None):
	
	if isinstance(op, ast.unaryop):
		container(self).nodeTree = UnaryOp(op=op, operand=container(self).nodeTree)
	elif isinstance(op, ast.operator):
		container(self).nodeTree = BinOp(op=op, left=container(self).nodeTree, right=Reference(right, container(self)))
	elif isinstance(op, ast.cmpop):
		container(self).nodeTree = Compare(ops=[op], left=container(self).nodeTree, comparators=[Reference(right, container(self))])
	
	return self

class Reference(Subscript):

	actualValue : Any
	def __new__(cls : type["Reference"], actualValue : Any, cont : ThisContainer):
		if actualValue is this:
			return ast.Name(id="this", ctx=ast.Load())
		elif type(actualValue) is this:
			cont.values.update(container(actualValue).values)
			return container(actualValue).nodeTree
		elif isConstant(actualValue):
			return ast.Constant(value=actualValue)
		else:
			return super().__new__(cls)
	
	def __init__(self : "Reference", actualValue : Any, cont : ThisContainer):
		self.actualValue = actualValue
		cont.add(actualValue)
		super().__init__(value=ast.Name(id=CONTAINER_NAME, ctx=ast.Load()), slice=ast.Constant(value=id(actualValue)), ctx=ast.Load())

def visit_Reference(self, node):
	value = node.actualValue
	if isinstance(value, tuple):
		with self.delimit("(", ")"):
			self.items_view(self._write_constant, value)
	elif value is ...:
		self.write("...")
	else:
		self._write_constant(value)

ast._Unparser.visit_Reference = visit_Reference

class ThisContainer:

	nodeTree : ast.AST = None
	values : dict[int,Any]
	def __init__(self):
		self.nodeTree = ast.Name(id="this", ctx=ast.Load())
		self.values = {}
	def add(self, value):
		self.values[id(value)] = value

class Function:

	__callback__ : Callable
	__argname__ : str = "this"
	self : "Function"
	values : dict[int,Any]
	def __init__(self, container : ThisContainer):
		
		self.self = self
		self.tree = container.nodeTree
		self.values = self.__dict__[CONTAINER_NAME] = container.values
		
		module = ast.Module(
			body=[
				ast.FunctionDef(
					name="__callback__",
					args=ast.arguments(
						posonlyargs=[],
						args=[
							ast.arg(arg=self.__argname__, annotation=None)
						],
						kwonlyargs=[],
						kw_defaults=[],
						defaults=[]),
					decorator_list=[],
					body=[ast.Return(value=container.nodeTree)
				])],
			type_ignores=[],
		)

		ast.fix_missing_locations(module)
		exec(compile(module, filename=repr(self), mode="exec"), self.__dict__)
	
	@cached_property
	def __expr__(self):
		return ast.unparse(self.tree)
	
	def __repr__(self):
		return f"<This.Function ({self.__argname__}): return {self.__expr__} at {hex(id(self))}>"
	
	def __call__(self, this): return self.__callback__(this)

class ThisBase:
	
	container : ThisContainer
	
	def __init__(self):
		self.container = ThisContainer()

	def __iter__(self):
		yield Function(container(self))
	def __next__(self):
		return Function(container(self))
	
	def __repr__(self):
		return f"<{ast.unparse(container(self).nodeTree)} at {hex(id(self))}>"

	def __getattribute__(self, name: str) -> "ThisBase":
		container(self).nodeTree = Attribute(value=container(self).nodeTree, attr=name, ctx=ast.Load())
		return self
	def __call__(self, *args, **kwargs) -> "ThisBase":
		cont = container(self)
		cont.nodeTree = Call(func=cont.nodeTree, args=[Reference(arg, cont) for arg in args], keywords=[Keyword(name, Reference(kwargs[name], cont)) for name in kwargs])
		return self
	def __getitem__(self, key: Any) -> "ThisBase":
		container(self).nodeTree = Subscript(value=container(self).nodeTree, slice=Reference(key, container(self)), ctx=ast.Load())
		return self
	
	# Comparisons
	def __eq__(self, other):		return createOperation(self, other, ast.Eq())
	def __ne__(self, other):		return createOperation(self, other, ast.NotEq())
	def __lt__(self, other):		return createOperation(self, other, ast.Lt())
	def __le__(self, other):		return createOperation(self, other, ast.LtE())
	def __gt__(self, other):		return createOperation(self, other, ast.Gt())
	def __ge__(self, other):		return createOperation(self, other, ast.GtE())
	def __contains__(self, other):	raise NotImplementedError("`item in this`")

	# Unary operations
	def __neg__(self):				return createOperation(self, op=ast.USub())
	def __pos__(self):				return createOperation(self, op=ast.UAdd())
	def __not__(self):				return createOperation(self, op=ast.Not())
	def __invert__(self):			return createOperation(self, op=ast.Invert())
	
	# Binary operations
	def __add__(self, other):		return createOperation(self, other, ast.Add())
	def __sub__(self, other):		return createOperation(self, other, ast.Sub())
	def __mul__(self, other):		return createOperation(self, other, ast.Mult())
	def __div__(self, other):		return createOperation(self, other, ast.Div())
	def __floordiv__(self, other):	return createOperation(self, other, ast.FloorDiv())
	def __mod__(self, other):		return createOperation(self, other, ast.Mod())
	def __pow__(self, other):		return createOperation(self, other, ast.Pow())
	def __lshift__(self, other):	return createOperation(self, other, ast.LShift())
	def __rshift__(self, other):	return createOperation(self, other, ast.RShift())
	def __or__(self, other):		return createOperation(self, other, ast.BitOr())
	def __xor__(self, other):		return createOperation(self, other, ast.BitXor())
	def __and__(self, other):		return createOperation(self, other, ast.BitAnd())
	def __matmul__(self, other):	return createOperation(self, other, ast.MatMult())

class ThisType(type):
	def __getattribute__(self, name: str) -> this:			return getattr(super().__call__(), name)
	def __call__(self, *args: Any, **kwds: Any) -> this:	return super().__call__()(*args, **kwds)
	def __getitem__(self, key: Any) -> this:				return super().__call__()[key]

	# Comparisons
	def __eq__(self, other):		return super().__call__() == other
	def __ne__(self, other):		return super().__call__() != other
	def __lt__(self, other):		return super().__call__() < other
	def __le__(self, other):		return super().__call__() <= other
	def __gt__(self, other):		return super().__call__() > other
	def __ge__(self, other):		return super().__call__() >= other
	def __contains__(self, other):	raise NotImplementedError("`item in this`")

	# Unary operations
	def __neg__(self):				return -super().__call__()
	def __pos__(self):				return +super().__call__()
	def __not__(self):				return not super().__call__()
	def __invert__(self):			return ~super().__call__()
	
	# Binary operations
	def __add__(self, other):		return super().__call__() + other
	def __sub__(self, other):		return super().__call__() - other
	def __mul__(self, other):		return super().__call__() * other
	def __div__(self, other):		return super().__call__() / other
	def __floordiv__(self, other):	return super().__call__() // other
	def __mod__(self, other):		return super().__call__() % other
	def __pow__(self, other):		return super().__call__() ** other
	def __lshift__(self, other):	return super().__call__() << other
	def __rshift__(self, other):	return super().__call__() >> other
	def __or__(self, other):		return super().__call__() | other
	def __xor__(self, other):		return super().__call__() ^ other
	def __and__(self, other):		return super().__call__() & other
	def __matmul__(self, other):	return super().__call__() @ other

class this(ThisBase, metaclass=ThisType): pass
