
from GeekyGadgets.TypeHinting import *
from collections import UserDict
import re, threading, time, sys, logging, os, types
from timeit import default_timer as timer
from time import sleep
from functools import cached_property, partial, cache, wraps
from io import BufferedWriter, BufferedReader

_T = TypeVar("_T")
PYTHON_VERSION = sys.version_info
ROOT_LOGGER = logging.getLogger()
DEV_NULL = open(os.devnull, "w")
DEV_NULL_BYTES = open(os.devnull, "wb")
ISATTY = sys.stdout.isatty()