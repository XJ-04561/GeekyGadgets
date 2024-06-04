from typing import *
from collections import UserDict
import re, threading, time, sys, logging, os
from timeit import default_timer as timer

_T = TypeVar("_T")
PYTHON_VERSION = sys.version_info
ROOT_LOGGER = logging.getLogger()
DEV_NULL = open(os.devnull, "w")
DEV_NULL_BYTES = open(os.devnull, "wb")
ISATTY = sys.stdout.isatty()