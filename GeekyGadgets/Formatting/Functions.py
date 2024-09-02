
import GeekyGadgets.Globals as _GL

_PLURAL_PATTERN = _GL.re.compile(r"s$|x$|z$|sh$|ch$")
_HIDDEN_PATTERN = _GL.re.compile(r"^_[^_].*")
_DUNDER_PATTERN = _GL.re.compile(r"^__.*__$")
_DIRECTIONAL_CHARACTERS = {
	"<" : ">",
	">" : "<",
	"(" : ")",
	")" : "(",
	"[" : "]",
	"]" : "[",
}

_ALPHA_INDEX = 65
_ALPHA_LENGTH = 26
_DIGIT_SYMBOLS = "0123456789abcdefghijklmnopqrstuvwxyz"

from pprint import (
	pprint as pPrint,
	pformat as pFormat
)

def alphabetize(n : int):
	n = -n if (negative := n < 0) else n
	r = n % _ALPHA_LENGTH
	m = n // _ALPHA_LENGTH
	out = [_ALPHA_INDEX+r]
	while m > 0 and n > 0:
		n = m - 1
		m, r = divmod(n, _ALPHA_LENGTH)
		out.append(_ALPHA_INDEX+r)
	if negative:
		return "-"+bytes(reversed(out)).decode() 
	else:
		return bytes(reversed(out)).decode()

def alignBytes(byteString : bytes) -> list[str]:
	return " ".join(map(lambda b: (f'{repr(bytes([b]))[2:-1]:<4}'), byteString))

def numerateAlpha(string : str):
	string = string.strip()
	string = string[1:].upper() if (negative := string[0] == "-") else string.upper()
	nums = string.encode("utf-8")
	out = (nums[0]-_ALPHA_INDEX+1) *_ALPHA_LENGTH**i
	i = 1
	while i < len(nums):
		out += (nums[i]-_ALPHA_INDEX+1) *_ALPHA_LENGTH**i
		i += 1
	return -out if negative else out

@_GL.cache
def base(n : int, base : int, symbols : _GL.Iterable[str]=_DIGIT_SYMBOLS):
	if base > len(_DIGIT_SYMBOLS):
		return None
	m, r = divmod(n)
	if m == 0:
		return _DIGIT_SYMBOLS[r]
	else:
		return _DIGIT_SYMBOLS[r] + base(m)

def pluralize(string : str) -> str:
	match _PLURAL_PATTERN.search(string):
		case None:
			return f"{string}s"
		case _:
			return f"{string}es"

def flipString(string):
	return "".join(c if c not in _DIRECTIONAL_CHARACTERS else _DIRECTIONAL_CHARACTERS[c] for c in reversed(string))

@_GL.overload
def callFormat(func : _GL.Callable, args : tuple[_GL.Any]=(), kwargs : dict[str,_GL.Any]={}) -> str: ...
@_GL.overload
def callFormat(func : _GL.Callable, args : tuple[_GL.Any]=(), kwargs : dict[str,_GL.Any]={}, *, argLength : int=35) -> str: ...
def callFormat(func, args=(), kwargs={}, *, argLength=35):
	
	inner = []
	for arg in args:
		inner.append(str(arg))
		if len(inner[-1]) > argLength:
			inner[-1] = inner[-1][:argLength-3-1] + "..." + inner[-1][-1]
	for name, value in kwargs.items():
		inner.append(str(name)+"="+str(value))
		if len(inner[-1]) > argLength:
			inner[-1] = inner[-1][:argLength-3-1] + "..." + inner[-1][-1]
	
	return f"{getattr(func, '__qualname__', getattr(func, '__name__', func))}({', '.join(inner)})"

def dateFormat(seconds=None, template="%Y-%m-%d %H:%M:%S (UTC%z)"):
	return _GL.time.strftime(template, _GL.time.localtime(seconds))

def timeFormat(seconds):
	return f"{seconds//3600:0>2.0f}:{(seconds//60)%60:0>2.0f}:{seconds%60:0>6.3f}"

def timeStamp(seconds=None, template="%Y-%m-%d--%H-%M-%S--%"):
	return _GL.time.strftime(template, _GL.time.localtime(seconds))