
from typing import *
from types import *
from collections import UserDict
import re, threading, time, sys, logging, os, types
from timeit import default_timer as timer
from functools import cached_property

class Number: pass
Number = int|float|complex

_T = TypeVar("_T")
PYTHON_VERSION = sys.version_info
ROOT_LOGGER = logging.getLogger()
DEV_NULL = open(os.devnull, "w")
DEV_NULL_BYTES = open(os.devnull, "wb")
ISATTY = sys.stdout.isatty()