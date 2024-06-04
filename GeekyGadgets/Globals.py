from typing import *
import re, threading, time
from timeit import default_timer as timer

_T = TypeVar("_T")