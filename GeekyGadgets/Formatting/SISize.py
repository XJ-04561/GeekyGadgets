

import GeekyGadgets.Math.Stats.Functions as _MathFunctions
import GeekyGadgets.TypeHinting as _TypeHinting

_PREFIX_MAGNITUDES : list[tuple[str,int]] = [""]+list("kMGTPEZYRQ")

# def shortenNumber(x : int|float, unit : str=""):
	
# 	if x % 1000:
# 		return f"{x}{unit}"
# 	for c, size in _PREFIX_MAGNITUDES[1:]:
# 		if x % size == 0:
# 			return f"{format(x/(size/1000), '.0f')} {unit}"
# 	return f"{x:.1e}{unit}"

def shortNumber(x : int|float, unit : str="", sep : str=" "):
	
	for i, letter in enumerate(_PREFIX_MAGNITUDES):
		if x / 10**(3*i) < 800:
			if (x / 10**(3*i)) % 1:
				return f"{x / 10**(3*i):.1f}{sep}{letter}{unit}"
			else:
				return f"{x / 10**(3*i):.0f}{sep}{letter}{unit}"
	return f"{x:.1e}{sep}{unit}"

def floatEmphasize(value, low=0, high=100, length : int=5):
	from math import log10
	maxSense = _MathFunctions.ceil(log10(high-low))
	lowLimit = maxSense - length
	if lowLimit >= 6:
		return f"{value/10**lowLimit:.0f}e{lowLimit}"
	elif lowLimit >= 0:
		return str(value).split(".")[0][lowLimit:] + "0"*lowLimit
	else:
		m = format(value - int(value), f".{-lowLimit}f")[2:]
		return rTrimRepeats(f"{int(value)}.{m}").rstrip("0").rstrip(".") if m else f"{int(value)}"

def rTrimRepeats(string : str):
	return string.rstrip(string[-1])+string[-1]

def percentEmphasize(value, length : int=5):
	return floatEmphasize(100*value, length=length)+" %"

def roundSignificant(x : _TypeHinting.Number, digits : int=4) -> str:
	if x == 0:
		return "0"
	from math import log10
	size = log10(abs(x))
	if size < 0:
		upperSize = _MathFunctions.floor(size)
		lowerSize = _MathFunctions.ceil(size)
	else:
		upperSize = _MathFunctions.ceil(size)
		lowerSize = _MathFunctions.floor(size)
	if size < -3:
		return format(x, f".{digits-1}e")
	elif size < 0:
		return "."+format(format(x / (10**(upperSize+1)), f".{digits}f").partition(".")[-1], f"0>{abs(upperSize)-1+digits}").rstrip("0")
	elif size == 0:
		return "1"
	elif size <= digits-1:
		numbers = format(x / (10**(upperSize+1)), f".{digits}f").partition(".")[-1]
		
		return (f"{numbers[:upperSize+1]}.{numbers[upperSize+1:].rstrip('0')}").rstrip(".")
	elif size <= 3+digits:
		return format(format(x / (10**(upperSize+1)), f".{digits}f").partition(".")[-1], f"0<{upperSize}")
	else:
		return format(x, f".{digits}e")
	
def numericScale(first : _TypeHinting.Number, last : _TypeHinting.Number, ticks : int, base : int|None=10):
	
	origOrder = _MathFunctions.sign(last - first)
	if last < first:
		first, last = last, first
	from math import log
	diff = abs(last - first)
	if diff == 0:
		return []
	elif abs(first) < 2*abs(last - first) / (ticks-1):
		first = 0
	targetDelta = abs(last - first) / (ticks-1)
	delta = min(base**_MathFunctions.ceil(log(targetDelta, base)), base**_MathFunctions.floor(log(targetDelta, base)),  key=lambda x: abs(targetDelta-x))
		
	return [
		delta*tick
		for tick in range(
			_MathFunctions.floor(first/delta),
			_MathFunctions.ceil(last/delta)+1+(delta*ticks + first < last < delta*(ticks+1) + first)
		) if first <= tick <= last][::origOrder]
