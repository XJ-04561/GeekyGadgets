
from GeekyGadgets.Math.Stats.Globals import *

import GeekyGadgets.Iterators as _Iterators 
import GeekyGadgets.Formatting as _Formatting
import GeekyGadgets.Functions as _Functions
import GeekyGadgets.Math.Stats.Distributions as Dists
import GeekyGadgets.Math.Stats.Binning as Binning

_GT = TypeVar("_GT")
_E = TypeVar("_E")

def combineClose(data : Iterable[_E], p : float=0.8, gType : _GT=Dists.GaussianModel, debug : bool=True) -> list[_GT]:
	
	data = sorted(data)
	
	onlyMultiples = list(data)
	for value in set(data):
		onlyMultiples.remove(value)
	
	multiples = {x:sum(x==y for y in data) for x in set(onlyMultiples)}
	onlyUniques = list(set(data))

	# pairs = sorted(_Iterators.Echo(range(len(onlyUniques))), key=lambda x:abs(onlyUniques[x[1]] - onlyUniques[x[0]]))
	# groups : list[Dists.GaussianModel] = [Dists.GaussianModel(filter(value.__eq__, data)) for value in onlyMultiples]

	datapoints = sorted(onlyUniques, key=lambda x:x.mean if isinstance(x, gType) else x)
	distFunc = lambda x: abs(
		(x[0].mean if isinstance(x[0], gType) else x[0])
		- (x[1].mean if isinstance(x[1], gType) else x[1])
	)

	# for pair in pairs:
	while len(datapoints) > 1:
		if debug:
			print("Models:", ";\n        ".join(map(str, filter(lambda d:isinstance(d, gType), datapoints))))
			print("Data:", "; ".join(map(Dists.roundSignificant, filter(lambda d:not isinstance(d, gType), datapoints))) if len(datapoints) < 5 else f"n={len(datapoints)}")

		for x,y in sorted(_Iterators.Echo(datapoints), key=distFunc):
			if isinstance(x, gType) and isinstance(y, gType):
				prob = Dists.P(x == y)
				if debug:
					print(1, prob > p)
				if prob > p:
					if debug:
						print("1 is a win!")
					x.update(y.data)
					datapoints.remove(y)
					break
			elif isinstance(y, gType):
				prob = Dists.P(x == y)
				if debug:
					print(2, prob > p)
				if prob > p:
					if debug:
						print("2 is a win!")
					y.update((x,))
					if x in multiples:
						multiples[x] -= 1
						if multiples[x] <= 0:
							datapoints.remove(x)
					else:
						datapoints.remove(x)
					break
			elif isinstance(x, gType):
				prob = Dists.P(x == y)
				if debug:
					print(3, prob > p)
				if prob > p:
					if debug:
						print("3 is a win!")
					x.update((y,))
					if y in multiples:
						multiples[y] -= 1
						if multiples[y] <= 0:
							datapoints.remove(y)
					else:
						datapoints.remove(y)
					break
			else:
				if debug:
					print(4, x, y)
				if x in multiples:
					multiples[x] -= 1
					if multiples[x] <= 0:
						datapoints.remove(x)
				else:
					datapoints.remove(x)
				if y in multiples:
					multiples[y] -= 1
					if multiples[y] <= 0:
						datapoints.remove(y)
				else:
					datapoints.remove(y)
				datapoints.append(gType((x,y)))
				break
		else:
			break
		datapoints.sort(key=lambda x:x.mean if isinstance(x, gType) else x)
	
	clusters = list(filter(lambda x: isinstance(x, gType),datapoints))
	if debug:
		print("combineClose:", clusters)
		print("Data:", "; ".join(map(Dists.roundSignificant, filter(lambda d:not isinstance(d, gType), datapoints))) if len(datapoints) < 10 else f"n={len(datapoints)}")

	return clusters

def combineDensity(data : Iterable[_E], width : Number|Callable[[list[_E]],Number]=Binning.sturges, gType : _GT=Dists.GaussianModel, debug : bool=False) -> list[_GT]:

	data = sorted(data)
	
	windowIterator = _Iterators.SlidingWindow(data, width=width, strict=False)
	width = windowIterator.width or 1

	windows, positions = _Functions.unzip((tuple(window), pos) for window, pos in windowIterator)
	densities = [len(window)/width for window in windows]
	N = len(densities)
	minima = [
		j
		for i,j in _Iterators.Echo(range(len(densities)))
		if densities[i] > densities[j] < next(
			_Iterators.DropWhile(
				lambda x: x==densities[j],
				_Iterators.IterSlice(densities, j+1, N)
			),
			-INF
		)
	]

	minimaPos = [-INF, *(positions[i] for i in minima), INF]

	clusters = [gType(_Iterators.DropThenTakeWhile(data, lambda x:low<=x<high)) for low, high in _Iterators.Echo(minimaPos)]
	# clusters = list(map(_Formatting.alphabetize, range(len(minimaPos)-1)))
	
	if debug:
		print("combineDensity:", clusters)
		import matplotlib.pyplot as plt
		fig = plt.figure()
		axes = fig.add_subplot()

		axes.plot(data, [0.01]*len(data), "|")
		
		minima.append(len(positions))
		prev = 0
		for i, (low, high), cluster in zip(_Iterators.Count(), _Iterators.Echo(minimaPos), clusters):
			position, density = positions[prev:minima[i]], densities[prev:minima[i]]
			prev = minima[i]

			print(i, len(density), len(position))
			axes.plot(position, density, label=f"Cluster[ {cluster} ]")
			
		fig.savefig(f"{id(data):x}.png")

	return clusters
