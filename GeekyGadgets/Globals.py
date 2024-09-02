
from GeekyGadgets.TypeHinting import *
from GeekyGadgets.Paths import *
from collections import UserDict, UserList
import re, threading, time, sys, logging, os, types, random
from timeit import default_timer as timer
from time import sleep
from functools import cached_property, partial, cache, wraps, update_wrapper
from io import BufferedWriter, BufferedReader
from GeekyGadgets.This import this

_T = TypeVar("_T")
PYTHON_VERSION = sys.version_info
ROOT_LOGGER = logging.RootLogger(level=0)
DEV_NULL = open(os.devnull, "w")
DEV_NULL_BYTES = open(os.devnull, "wb")
ISATTY = sys.stdout.isatty()
BACKSLASH = "\\"
NEWLINE = "\n"
TABULATOR = "\t"
NAN = float("nan")
INF = float("inf")
NON_ITER = iter([])

NULL : "_NULL"
NIL : "_NIL"
REAL : "_REAL"
EXISTING : "_EXISTING"

GETATTR = object.__getattribute__
SETATTR = object.__setattr__
SET__DICT__ = lambda obj, attrName, value: GETATTR(obj, "__dict__").__setitem__(attrName, value)
DELATTR = object.__delattr__

FORMAT_PATTERN = re.compile(r"(?P<filler>[^<^>]+)?(?P<direction>[<^>])?(?P<size>\d+)?(?P<rest>.*)")
ANSI_MATCH = re.compile("\u001b.*?m|\x1b.*?m")

OPERATOR_INVERSE = {
	"<"		: ">",
	"<="	: ">=",
	">="	: "<=",
	">"		: "<",
	"="		: "!=",
	"=="	: "!=",
	"!="	: "==",

	"*"		: "/",
	"/"		: "*",
	"+"		: "-",
	"-"		: "+",
}
OPERATOR_LOGIC_INVERSE = {
	"<"		: ">=",
	"<="	: ">",
	">="	: "<",
	">"		: "<=",
	"="		: "!=",
	"=="	: "!=",
	"!="	: "==",
}
OPERATOR_DUNDER = {
	"<"		: "__lt__",
	"<="	: "__le__",
	">="	: "__ge__",
	">"		: "__gt__",
	"="		: "__eq__",
	"=="	: "__eq__",
	"!="	: "__ne__",

	"*"		: "__mul__",
	"/"		: "__truediv__",
	"+"		: "__add__",
	"-"		: "__sub__",
	"^"		: "__pow__",
	"//"	: "__floordiv__",
	"%"		: "__mod__",
	"@"		: "__matmul__",

	"*="		: "__imul__",
	"/="		: "__itruediv__",
	"+="		: "__iadd__",
	"-="		: "__isub__",
	"^="		: "__ipow__",
	"//="		: "__ifloordiv__",
	"%="		: "__imod__",
	"@="		: "__imatmul__",
}
OPERATOR_DUNDER_R = {
	"__lt__"		: "__rlt__",
	"__le__"		: "__rle__",
	"__ge__"		: "__rge__",
	"__gt__"		: "__rgt__",
	"__eq__"		: "__req__",
	"__eq__"		: "__req__",
	"__ne__"		: "__rne__",

	"__mul__"		: "__rmul__",
	"__truediv__"	: "__rtruediv__",
	"__add__"		: "__radd__",
	"__sub__"		: "__rsub__",
	"__pow__"		: "__rpow__",
	"__floordiv__"	: "__rfloordiv__",
	"__mod__"		: "__rmod__",
	"__matmul__"	: "__rmatmul__",
}
OPERATORS = [*OPERATOR_DUNDER]

class _NULL:
	def __call__(self, *args, **kwargs): return NULL
	def __repr__(self): return "NULL"
	def __str__(self): return "0"
	def __bool__(self): return False
	def __index__(self): return 0
class _NIL(_NULL): ...
class _REAL:
	def __repr__(self): return "REAL"
	def __str__(self): return "1"
	def __bool__(self): return True
	def __index__(self): return 1
class _EXISTING(_REAL): ...

NULL = _NULL
NIL = _NIL
REAL = _REAL
EXISTING = _EXISTING