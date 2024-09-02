
import GeekyGadgets.Math.Stats.Globals as _Globals

def sturges(data : _Globals.Iterable) -> float:
	from math import log
	return 1 + 3.322 * log(len(data) if not isinstance(data, _Globals.Iterator) else (n := sum(1 for _ in data)))

def squareRoot(data : _Globals.Iterable) -> float:
	from math import sqrt
	return sqrt(len(data) if not isinstance(data, _Globals.Iterator) else sum(map(lambda x:1, data)))

def rice(data : _Globals.Iterable) -> float:
	return 2*((len(data) if not isinstance(data, _Globals.Iterator) else sum(map(lambda x:1, data)))**(1/3))

def freedmanDiaconis(data : _Globals.Iterable) -> float:
	from GeekyGadgets.Math.Stats.Functions import span, quantiles
	data = sorted(data)
	_, Q_1, _, Q_3, _ = quantiles(data)
	return span(data) / (2*(Q_3 - Q_1)/(len(data)**(1/3)))

