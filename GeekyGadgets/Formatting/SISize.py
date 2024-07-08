
from GeekyGadgets.Iterators import Count

PREFIX_MAGNITUDES : list[tuple[str,int]] = list(zip([""]+list("kMGTPEZYRQ"), map((1000).__pow__, Count(1))))

def shortenNumber(x : int|float, unit : str=None):
	
	if x % 1000:
		return f"{x}{unit}"
	for c, size in PREFIX_MAGNITUDES[1:]:
		if x % size == 0:
			return f"{format(x/(size/1000), '.0f')}{unit}"
	return f"{x:.1e}{unit}"

def shortNumber(x : int|float, unit : str=None):
	
	for c, size in PREFIX_MAGNITUDES:
		if x / size < 1:
			return f"{format(x/(size/1000), '.1f')}{unit}"
	return f"{x:.1e}{unit}"