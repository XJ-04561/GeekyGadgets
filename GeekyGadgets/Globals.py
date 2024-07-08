
from GeekyGadgets.TypeHinting import *
from GeekyGadgets.Paths import *
from collections import UserDict, UserList
import re, threading, time, sys, logging, os, types, random
from timeit import default_timer as timer
from time import sleep
from functools import cached_property, partial, cache, wraps, update_wrapper
from io import BufferedWriter, BufferedReader

_T = TypeVar("_T")
PYTHON_VERSION = sys.version_info
ROOT_LOGGER = logging.getLogger()
DEV_NULL = open(os.devnull, "w")
DEV_NULL_BYTES = open(os.devnull, "wb")
ISATTY = sys.stdout.isatty()
BACKSLASH = "\\"
NEWLINE = "\n"
TABULATOR = "\t"

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

NULL = _NULL()
NIL = _NIL()
REAL = _REAL()
EXISTING = _EXISTING()

GETATTR = object.__getattribute__
SETATTR = object.__setattr__
SET__DICT__ = lambda obj, attrName, value: GETATTR(obj, "__dict__").__setitem__(attrName, value)
DELATTR = object.__delattr__

FORMAT_PATTERN = re.compile(r"(?P<filler>[^<^>]+)?(?P<direction>[<^>])?(?P<size>\d+)?(?P<rest>.*)")
ANSI_MATCH = re.compile("\u001b.*?m|\x1b.*?m")
