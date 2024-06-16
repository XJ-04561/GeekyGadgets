
from GeekyGadgets.TypeHinting import *
from collections import UserDict, UserList
import re, threading, time, sys, logging, os, types
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

FORMAT_PATTERN = re.compile(r"(?P<filler>[^<^>]+)?(?P<direction>[<^>])?(?P<size>\d+)?(?P<rest>.*)")
ANSI_MATCH = re.compile("\u001b.*?m|\x1b.*?m")
