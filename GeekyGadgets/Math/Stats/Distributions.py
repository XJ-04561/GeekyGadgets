
from math import factorial as fac, e, pi, sqrt, erf, gamma

from GeekyGadgets.Globals import *
from GeekyGadgets.Functions import tryExcept, forceHash, operate

_T = TypeVar("_T")

###
###     GLOBAL FUNCTIONS USED BY CLASSES BUT BELONG IN THE OPEN
###

def E(data, n=None):
	"""
	E(data, n=None)
	
	Calculates the mean value of a given dataset.
	Input:
		data    -   Any iterable object that sum() can
					be called with.
		n       -   int corresponding to the size of
					the dataset. Determined
					automatically if not specified.
	Output:
		float/complex that is the mean of the given
		dataset of length n.
	"""
	
	if n is None:
		n = len(data)
	return sum(data)/n

def V(data, mean=None, n=None):
	"""
	V(data, mean=None, n=None)
	
	Calculates the variance of a given dataset.
	Variance being the mean of squaring the
	difference between each point and the mean.
	Input:
		data    -   Any iterable object that sum() can
					be called with.
		mean    -   The predetermined mean of the
					dataset. If None, will determine
					using the data set and n.
		n       -   int corresponding to the size of
					the dataset (Degrees of freedom
					are assumed already accounted
					for). Determined automatically if
					not specified.
	Output:
		float/complex representing the variance of a
		dataset with length n.
	"""
	
	if n is None:
		n = len(data)
	if mean is None:
		mean = E(data, n)
	return sum(( (x - mean)**2 for x in data )) / n

def comb(n, k):
	"""
	comb(n, k)
	
	This function is normally written as two
	parenthesis with n over k inbetween. It determines
	how many ways k amount of elements can be chosen
	from a set of n elements. Named after:
	Combinations of size k chosen from
	a set of size n.
	Input:
		n   -   int designating the size of the set.
		k   -   int designating the size of the sample.
	
	Ouput:
		float/complex representing the possible
		combinations of k elements chosen from a set
		of size n
	"""
	
	return fac(n)/(fac(k)*fac(n-k))

def flip(operator):
	"""
	flip(operator)
	
	This function gives an inverse of a given logical
	operator. It is sensitive to exclsive/inclusive
	operators.
	Input:
		operator    -   str of the operator to be
						inverted.
	
	Output:
		str with the inverted operator.
	"""
	
	return OPERATOR_LOGIC_INVERSE[operator]

def phi(x):
	"""
	phi(x)
	
	Cumulative distribution function for the standard
	normal distribution.
	Input:
		x   -   int/float number of standard
				deviations from the mean.
	
	Output:
		float value of the cumulative area under the
		normal distribution function from the left
		side up to the given value x.
	"""
	if x == INF:
		return 1
	elif x == -INF:
		return 0
	else:
		return (1 + erf(x / sqrt(2))) / 2

def VarPooled(s_1, s_2, n_1, n_2):
	"""
	VarPooled(s_1, s_2, n_1, n_2)
	
	Pools the variance of two given variances, and the
	sample sizes of the two sets the variances
	originate from.
	Input:
		s_1 -   int/float with the standard deviation
				of the first distribution.
		s_2 -   int/float with the standard deviation
				of the second distribution.
		n_1 -   int/float with the sample size of the
				first distribution.
		n_2 -   int/float with the sample size of the
				second distribution.
	
	Output:
		A float value of the pooled variance.
	"""
	
	return ((n_1 - 1)*s_1**2 + (n_2 - 1)*s_2**2) / (n_1 + n_2 - 2)

def sumRecip(*args):
	"""
	sumRecip(*args)
	
	Takes an indefinite amount of int/float values and
	returns the sum of each of their inverse.
	Input:
		*args   -   Container of int/float values that
					were given as arguments at
					function call.
	
	Output:
		int/float carrying the sum of all the inverses
		of the provided values.
	"""
	
	return sum(1/x for x in args)

#def T0(X1, *args):
	#class placeHolder:
		#def __init__(self):
			#self.mean = 0
			#self.stDev = 0
			#self.variance = 0
			#self.n = 1000000000000000000000
	#if type(X1) in (type(x) for x in args):
		#X2 = [x for x in args if type(x) is type(X1)][0]
	#else:
		#X2 = placeHolder()
	
	#if int in (type(x) for x in args) or float in (type(x) for x in args):
		#diff = [x for x in args if type(x) in [int, float]][0]
	#else:
		#diff = 0
	
	#return (X1.mean - X2.mean - diff) / (sqrt(VarPooled(X1.stDev, X2.stDev, X1.n, X2.n)) / sqrt(1/X1.n + 1/X2.n))

def unique(l):
	"""
	unique(l)
	
	Takes an iterable object of any elements that can
	be compared for equivalence, and returns a copy of
	that list, but where each equal-value element
	appears only once.
	Input:
		l   -   Iterable object.
	
	Output:
		list containing the elements of the provided
		iterable object, but with no duplicate-value
		elements.
	"""
	
	ret = []
	for el in l:
		if el not in ret:
			ret.append(el)
	
	return ret

def rankSums(data):
	ret = [0, 0]
	ranks = []
	values = []
	i=1
	for el in data:
		if el != 0:
			ranks.append(i)
			values.append(el)
			i+=1
	
	for val in unique(values):
		sameRank = [ranks[i] for i in range(len(values)) if abs(values[i]) == abs(val)]
		if val < 0:
			ret[0] += sum((1 for val2 in values if val == val2))*sum(sameRank)/len(sameRank)
		elif val > 0:
			ret[1] += sum((1 for val2 in values if val == val2))*sum(sameRank)/len(sameRank)
	
	return ret

def rankSum(X_1, X_2):
	ret = [0, 0]
	ranks = []
	values = []
	data = X_1 + X_2
	data.sort(key=abs)
	i=1
	for el in data:
		if el != 0:
			ranks.append(i)
			values.append(el)
			i+=1
	
	for val in X_1:
		sameRank = [ranks[i] for i in range(len(values)) if values[i] == val]
		ret[0] += sum(sameRank)/len(sameRank)
	
	for val in X_2:
		sameRank = [ranks[i] for i in range(len(values)) if values[i] == val]
		ret[1] += sum(sameRank)/len(sameRank)
	
	return ret

try:
	from scipy.special import betainc, betaincinv, gammainc, gammaincinv # type: ignore
	
	def chiProb(x, v):
		return 1 - gammainc(v/2, x/2)

	def chi(a, v):
		return 2 * gammaincinv(v/2, 1 - a)

	def t(a, v):
		x = betaincinv(v/2, 1/2, a*2)
		
		ret = sqrt(v/x - v)
		return ret

	def tProb(t, v):
		x = v/(t**2 + v)
		return betainc(v/2, 1/2, x)/2

	def f(a, v1, v2):
		x = betaincinv(v1/2, v2/2, 1 - a)
		
		ret = v2/(1/x - 1) / v1
		return ret

	def fProb(f, v1, v2):
		x = v1*f/(v1*f + v2)
		return 1 - betainc(v1/2, v2/2, x)
except ImportError:
	pass

def wilcox(X1 : Iterable[Number], X2 : Iterable[Number]|None=None, mean_0 : Number|None=None):
	ret = VariableContainer()
	
	if X2 is not None and mean_0 is None:
		if len(X1) < len(X2):
			_X1 = list(X1[:])
			_X2 = list(X2[:])
		else:
			_X1 = list(X2[:])
			_X2 = list(X1[:])
		
		_X1.sort(key=abs)
		_X2.sort(key=abs)

		ret["n_1"] = n_1 = len(_X1)
		ret["n_2"] = n_2 = len(_X2)

		[W_1, W_2] = rankSum(_X1, _X2)
		
		ret["W_1"] = W_1
		ret["W_2"] = W_2
		ret["min(W_2, W_1)"] = min(W_1, W_2)
		
		ret["mean_W_1"] = mean_W_1 = n_1*(n_1 + n_2 + 1)/2

		ret["S_W_1"] = S_W_1 = sqrt(n_1*n_2*(n_1 + n_2 + 1)/12)

		ret["Z_0"] = (W_1 - mean_W_1)/S_W_1
	
	if X2 is None and mean_0 is not None:
		_X1 = [x - mean_0 for x in X1 if x - mean_0 != 0]

		_X1.sort(key=abs)

		ret["n"] = n = len(_X1)

		[W_neg, W_pos] = rankSums(_X1)
		
		ret["W_neg"] = W_neg
		ret["W_pos"] = W_pos
		ret["min(W_neg, W_pos)"] = min(W_neg, W_pos)
		
		ret["Z_0"] = Z_0 = (W_pos - n*(n+1)/4) / sqrt(n*(n+1)*(2*n+1)/24)
	
	return ret

def z(alpha, decimals=10):
	a = -100000
	b = 100000
	ret = [0, 1]
	n=0
	while abs(ret[0] - alpha) > 10**(-decimals) and abs(ret[1] - alpha) > 10**(-decimals):
		new = phi((a + b)/2)
		if new < alpha:
			a = (a + b)/2
			ret[0] = new
		else:
			b = (a + b)/2
			ret[1] = new
		
		if n > 1000:
			break
		n+=1
	
	if abs(ret[0] - alpha) < 10**(-decimals):
		return a
	elif abs(ret[1] - alpha) < 10**(-decimals):
		return b
	else:
		return (a+b)/2

###
###
###



###
###     CLASSES OF DISTRIBUTIONS
###

class Comparison:
	def __init__(self, left, operator, right):
		self.left = left
		self.operator = operator
		self.right = right
	
	def __float__(self):
		if isinstance(self.left, Distribution):
			return self.left.P(self.operator, self.right)
		elif isinstance(self.right, Distribution):
			return self.right.P(flip(self.operator), self.left)
		else:
			return float(operate(self.left, self.operator, self.right))
		
	def __bool__(self):
		if isinstance(self.left, Distribution) and isinstance(self.right, Distribution):
			if self.operator in "==":
				return hash(self.left) == hash(self.right)
			elif self.operator == "!=":
				return hash(self.left) != hash(self.right)
			else:
				return False
		else:
			return bool(operate(
				self.left if isinstance(self.left, Number) else float(self.left),
				self.operator,
				self.right if isinstance(self.right, Number) else float(self.right)
			))
	
	def __str__(self):
		return f"{self.left} {self.operator} {self.right}"

	def __repr__(self):
		return f"<{self.__class__.__name__} '{self!s}' at {id(self):#x}>"
	
	def P(self):
		return float(self)

	# def Pinv(self, operator, right):
	# 	if isinstance(self.left, Distribution):
	# 		return self.left.Pinv(self.operator, right)
	# 	elif isinstance(self.right, Distribution):
	# 		return self.right.Pinv(self.operator, right)
	# 	else:
	# 		return operate(self.left, self.operator, self.right)


#
#	Distributions
#

class Distribution:
	
	name = property(lambda self: self.__class__.__name__)

	parameters : tuple[Number]

	def __init_subclass__(cls, *args, name : str|None=None, **kwargs) -> None:
		if name is not None:
			cls.name = name
		super().__init_subclass__(*args, **kwargs)
	
	__class_getitem__ = Subscriptable.__class_getitem__
	
	def __lt__(self, right): return Comparison(self, "<", right)
	def __le__(self, right): return Comparison(self, "<=", right)
	def __eq__(self, right): return Comparison(self, "=", right)
	def __ne__(self, right): return Comparison(self, "!=", right)
	def __gt__(self, right): return Comparison(self, ">", right)
	def __ge__(self, right): return Comparison(self, ">=", right)
	
	def __hash__(self): return hash((type(self), self.parameters))

	def __repr__(self): return f"<Distribution `{self}` at {id(self):#x}>"

	def __str__(self):
		from GeekyGadgets.Formatting.SISize import roundSignificant
		return f"{self.name}({', '.join(map(roundSignificant, self.parameters))})"
	
	def __float__(self): return NotImplemented
	
	def P(self : "Distribution[_T]", operator : str, other : "_T|Number|Distribution") -> Interval[0, 1]:
		raise NotImplementedError()
	
	def Pinv(self : "Distribution[_T]", operator : str, other : "Number|Distribution") -> _T:
		raise NotImplementedError()

class Table:
	def __init__(self, data, sep=None):
		self.table = data

class HyperGeo(Distribution):
	
	parameters : tuple[Number] = property( lambda self: (self.N, self.n, self.k))
	
	def __init__(self, N, n, k):
		self.N = N
		self.n = n
		self.k = k
	
	def P(self, operator, right):
		if type(right) in [int, float]:
			if right > self.n:
				raise ValueError("x can't be larger than n. x = {}, n = {}.".format(right, self.n))
			if operator == "<":
				ret = 0
				for i in range(right):
					ret += comb(self.k, i)*comb(self.N-self.k, self.n-i)/comb(self.N, self.n)
				return ret
			elif operator == "<=":
				ret = 0
				for i in range(right+1):
					ret += comb(self.k, i)*comb(self.N-self.k, self.n-i)/comb(self.N, self.n)
				return ret
			elif operator == ">":
				ret = 0
				for i in range(right+1, self.n+1):
					ret += comb(self.k, i)*comb(self.N-self.k, self.n-i)/comb(self.N, self.n)
				return ret
			elif operator == ">=":
				ret = 0
				for i in range(right, self.n+1):
					ret += comb(self.k, i)*comb(self.N-self.k, self.n-i)/comb(self.N, self.n)
				return ret
			elif operator == "=":
				return comb(self.k, right)*comb(self.N-self.k, self.n-right)/comb(self.N, self.n)
			else:
				raise ValueError("Bro, the signs you can use are: <, <=, =, >, >=.")

class Bin(Distribution):
	
	parameters : tuple[Number] = property( lambda self: (self.n, self.p))
	
	def __init__(self, n=None, p=None):
		self.n = n
		self.p = p
	
	def __float__(self):
		return self.p
	
	def P(self, operator, right):
		if type(right) in [int, float]:
			if right > self.n:
				raise ValueError("x has to be lower than n. x = {}, n = {}.".format(right, self.n))
			if operator == "<":
				ret = 0
				for i in range(right):
					ret += comb(self.n, i)*(self.p**i)*(1-self.p)**(self.n-i)
				return ret
			elif operator == "<=":
				ret = 0
				for i in range(right+1):
					ret += comb(self.n, i)*(self.p**i)*(1-self.p)**(self.n-i)
				return ret
			elif operator == ">":
				ret = 0
				for i in range(right+1, self.n+1):
					ret += comb(self.n, i)*(self.p**i)*(1-self.p)**(self.n-i)
				return ret
			elif operator == ">=":
				ret = 0
				for i in range(right, self.n+1):
					ret += comb(self.n, i)*(self.p**i)*(1-self.p)**(self.n-i)
				return ret
			elif operator == "=":
				return comb(self.n, right)*(self.p**right)*(1-self.p)**(self.n-right)
			else:
				raise ValueError("Bro, the signs you can use are: <, <=, =, >, >=.")

class Po(Distribution):
	
	parameters : tuple[Number] = property( lambda self: (self.l, ))
	
	def __init__(self, l):
		self.l = l
		
	def P(self, operator, right):
		if type(right) in [int, float]:
			if operator == "<":
				ret = 0
				for i in range(right):
					ret += e**(-self.l)*self.l**i/fac(i)
				return ret
			elif operator == "<=":
				ret = 0
				for i in range(right+1):
					ret += e**(-self.l)*self.l**i/fac(i)
				return ret
			elif operator == ">":
				ret = 0
				for i in range(right+1):
					ret += e**(-self.l)*self.l**i/fac(i)
				return 1 - ret
			elif operator == ">=":
				ret = 0
				for i in range(right):
					ret += e**(-self.l)*self.l**i/fac(i)
				return 1 - ret
			elif operator == "=":
				return e**(-self.l)*self.l**right/fac(right)
			else:
				raise ValueError("Bro, the signs you can use are: <, <=, =, >, >=.")
	
	def __str__(self):
		return self.__name__ + "(" + str(self.l) + ")"

class N(Distribution):
	
	parameters : tuple[Number] = property( lambda self: (self.mean, self.variance))
	stDev : Number = property(lambda self: sqrt(self.variance))
	
	def __init__(self, mean, variance):
		self.mean = mean
		self.variance = variance

	# MATH OPERATORS TO USE THE PROBABILITY 
	def __mul__(self, right):
		if isinstance(right, N):
			return N(self.mean * right.mean, right.mean*self.variance + self.mean*right.variance + self.variance*right.variance)
		else:
			return N(self.mean * right, (self.stDev * right)**2)
	def __truediv__(self, right):
		if isinstance(right, N):
			if right.mean == 0:
				return ValueError(f"Can't divide Gaussian Distributions X / Y, if Y = 0.")
			return N(self.mean / right.mean, (self.stDev / right.mean)**2 + ((self.mean*right.stDev)/(right.mean**2))**2)
		else:
			if right == 0:
				return ValueError(f"Divison by zero: {self} / {right}")
			return N(self.mean / right, (self.stDev / right)**2)
	def __sub__(self, right):
		if isinstance(right, N):
			return N(self.mean - right.mean, self.variance + right.variance)
		else:
			return N(self.mean - right, self.variance)
	def __add__(self, right):
		if isinstance(right, N):
			return N(self.mean + right.mean, self.variance + right.variance)
		else:
			return N(self.mean + right, self.variance)
	# RECIPROCAL OPERATORS
	def __rmul__(self, left):
		if isinstance(left, N):
			return NotImplemented
		else:
			return N(left * self.mean, (left * self.stDev)**2)
	def __rtruediv__(self, left):
		if isinstance(left, N):
			return NotImplemented
		else:
			return N(left / self.mean, (left / self.stDev)**2)
	def __rsub__(self, left):
		if isinstance(left, N):
			return NotImplemented
		else:
			return N(left - self.mean, self.variance)
	def __radd__(self, left):
		if isinstance(left, N):
			return NotImplemented
		else:
			return N(left + self.mean, self.variance)
	
	def __float__(self):
		return self.mean

	def P(self : "N", operator : Literal["<","<=","==",">=",">","!="], right : Number|Distribution) -> Interval[0,1]:
		if isinstance(right, Distribution):
			return (self - right).P(operator, 0)
		from GeekyGadgets.Math.Stats.Functions import sign
		
		if operator in ["<", "<="]:
			return phi((right - self.mean)/self.stDev if self.stDev != 0 else sign(right - self.mean)*INF)
		elif operator in ["=", "=="]:
			return 2 * phi(-abs((right - self.mean)/self.stDev if self.stDev != 0 else sign(right - self.mean)*INF))
		elif operator == "!=":
			return 1 - 2*phi(-abs((right - self.mean)/self.stDev if self.stDev != 0 else sign(right - self.mean)*INF))
		else:
			return 1 - phi((right - self.mean)/self.stDev if self.stDev != 0 else sign(right - self.mean)*INF)
	
	def Pinv(self, operator, right):
		return z(right)*self.stDev + self.mean

Z = N(0,1)

#
#	Models
#

from GeekyGadgets.Classy import Default, CachedDefault
class Model:
	
	data : tuple[Number|Iterable[Number]] = property(lambda self: self.__dict__.get("data"), lambda self, value: (self.__dict__.__setitem__("data", tuple(value)), setattr(self, "dataHash", forceHash(self.data))))
	dataHash : int
	n : int = property(lambda self: len(self.data))

	def update(self, iterable : Iterable=()):
		self.data = (*self.data, *iterable)
	
	def __str__(self) -> str:
		return super().__str__() + f", n={len(self.data)}"
	
	def __hash__(self):
		return id(self)

class GaussianModel(Model, N, name="N"):
	
	mean = CachedDefault["dataHash"](lambda self: E(self.data))
	variance = CachedDefault["dataHash"](lambda self: V(self.data, self.mean, self.n-1))
	stDev : Number = CachedDefault["dataHash"](lambda self: sqrt(self.variance))

	def __init__(self, data : Iterable[Number], /, *, mean : Number=NAN, variance : Number=NAN):
		self.data = data
		if len(self.data) <= 1:
			self.mean = self.data[0] if self.data else NAN
			self.variance = NAN
		if mean is not NAN and mean is not None:
			self.mean = mean
		if variance is not NAN and variance is not None:
			self.variance = variance
		
	def Z_0(self, mean0):
		if self.stDev != 0:
			return (self.mean - mean0) / (self.stDev / sqrt(self.n))
		else:
			from GeekyGadgets.Math.Stats.Functions import sign
			return sign(self.mean - mean0) * INF
	
	def T_0(self, mean0):
		if self.stDev != 0:
			return (self.mean - mean0) / (self.stDev / sqrt(self.n))
		else:
			from GeekyGadgets.Math.Stats.Functions import sign
			return sign(self.mean - mean0) * INF
	
	def X2_0(self, variance0):
		if variance0 != 0:
			return (self.n-1)*self.stDev**2 / variance0
		else:
			return INF

class BinomialGaussianModel(Model, N, name="N"):
	
	BOOLEAN_DATA = CachedDefault["dataHash"](lambda self: tryExcept(lambda : set(self.data).issubset({True,False,0,1})))

	mean = CachedDefault["dataHash"](lambda self: self.n*self.p)
	variance = CachedDefault["dataHash"](lambda self: self.n*self.p*self.q)
	stDev : Number = CachedDefault["dataHash"](lambda self: sqrt(self.variance))

	n = CachedDefault["dataHash"](lambda self: len(self.data) if self.BOOLEAN_DATA else max(self.data))
	p = CachedDefault["dataHash"](lambda self: sum(self.data)/self.n if self.BOOLEAN_DATA else min(self.data)/self.n)
	q = CachedDefault["dataHash"](lambda self: 1 - self.p)

	def __init__(self, data : Iterable[Literal[1,0]|bool]|Iterable[Iterable[Number],Iterable[Number]],
			  /, *, mean : Number=NAN, variance : Number=NAN):
		self.data = data
		if len(self.data) <= 1:
			raise ValueError(f"Not enough data for model. Data received: {self.data}")
		
	def Z_0(self, p0):
		return (self.mean - self.n*p0) / sqrt(self.n*p0*(1-p0))

###

class VariableContainer:
	def __init__(self, items=None, significant=None, indent=0):
		self.names = []
		self.values = []
		if type(items) is dict:
			for key, value in items.items():
				self.names.append(key)
				self.values.append(value)
		self.indent=indent
		
	def __getitem__(self, name):
		if name not in self.names:
			raise KeyError('variable "{}" not in VariableContainer'.format(name))
		return self.values[self.names.index(name)]
	
	def __setitem__(self, name, value):
		if name not in self.names:
			self.names.append(name)
			self.values.append(value)
		else:
			self.values[self.names.index(name)] = value
	
	def __delitem__(self, name):
		i = self.names.index(name)
		del self.names[i]
		del self.values[i]
	
	def __str__(self):
		_sep = [" = ",":\n"]
		return "\n".join(( "{}{}{}{}".format(self.indent*" ", self.names[i], _sep[isinstance(self.values[i], Number)], self.values[i]) for i in range(len(self.values)) ))
	
	def __repr__(self):
		_sep = [" = ",":\n"]
		return "\n".join(( "{}{}{}{}".format(self.indent*" ", self.names[i], _sep[isinstance(self.values[i], Number)], self.values[i]) for i in range(len(self.values)) ))

class Regression:
	def __init__(self, SumX, SumY, SumX2=None, SumY2=None, SumXY=None, n=None):
		if type(SumX) is list and type(SumY) is list:
			self.SumX  = sum(SumX)
			self.SumY  = sum(SumY)
			self.SumX2 = sum(x**2 for x in SumX)
			self.SumY2 = sum(y**2 for y in SumY)
			self.SumXY = sum(x*y for x,y in zip(SumX, SumY))
			self.n = len(SumX)
			
			self.calc()
		elif SumX2 is not None and SumY2 is not None and SumXY is not None and n is not None:
			self.SumX  = SumX
			self.SumY  = SumY
			self.SumX2 = SumX2
			self.SumY2 = SumY2
			self.SumXY = SumXY
			self.n = n
			
			self.calc()
		else:
			wrong = []
			if SumX2 is None:
				wrong.append("SumX^2")
			if SumY2 is None:
				wrong.append("SumY^2")
			if SumXY is None:
				wrong.append("SumXY")
			
			raise ValueError("Missing data for: " + ", ".join(wrong))
	
	def calc(self):
		self.S_xx = self.SumX2 - self.SumX**2 / self.n
		self.S_yy = self.SumY2 - self.SumY**2 / self.n
		self.S_xy = self.SumXY - self.SumX*self.SumY / self.n
		
		self.B_1 = self.S_xy / self.S_xx
		self.B_0 = (self.SumY - self.B_1 * self.SumX) / self.n
		
		self.SS_R = self.B_1 * self.S_xy
		self.SS_E = self.S_yy - self.B_1 * self.S_xy
		
		self.MS_R = self.SS_R / 1
		self.MS_E = self.SS_E / (self.n - 2)
		
		self.xMean = self.SumX / self.n
		self.yMean = self.SumY / self.n
		
		self.seB_1 = sqrt( self.MS_E / self.S_xx )
		self.seB_0 = sqrt( self.MS_E * (1 / self.n + self.xMean**2 / self.S_xx) )
		
		self.R2 = self.SS_R/(self.SS_R + self.SS_E)
	
	def __str__(self):
		ret = ""
		
		ret = ret + "Sum(X) = {:.4f}\n".format(self.SumX)
		ret = ret + "Sum(Y) = {:.4f}\n".format(self.SumY)
		ret = ret + "Sum(X²) = {:.4f}\n".format(self.SumX2)
		ret = ret + "Sum(Y²) = {:.4f}\n".format(self.SumY2)
		ret = ret + "Sum(XY) = {:.4f}\n".format(self.SumXY)
		ret = ret + "n = {:.4f}\n".format(self.n)
		
		ret = ret + "\nS_xx = {:.4f}\n".format(self.S_xx)
		ret = ret + "S_yy = {:.4f}\n".format(self.S_yy)
		ret = ret + "S_xy = {:.4f}\n".format(self.S_xy)

		ret = ret + "\nB_1 = {:.4f}\n".format(self.B_1)
		ret = ret + "B_0 = {:.4f}\n".format(self.B_0)

		ret = ret + "\nSS_R = {:.4f}\n".format(self.SS_R)
		ret = ret + "SS_E = {:.4f}\n".format(self.SS_E)

		ret = ret + "\nMS_R = {:.4f}\n".format(self.MS_R)
		ret = ret + "MS_E = {:.4f}\n".format(self.MS_E)

		ret = ret + "\nxMean = {:.4f}\n".format(self.xMean)
		ret = ret + "yMean = {:.4f}\n".format(self.yMean)

		ret = ret + "\nseB_1 = {:.4f}\n".format(self.seB_1)
		ret = ret + "seB_0 = {:.4f}\n".format(self.seB_0)
		
		ret = ret + "\nstDev_e = {:.4f}\n".format(sqrt(self.MS_E))
		
		ret = ret + "\nR² = {:.4f}\n".format(self.R2)
		ret = ret + "r = {:.4f}\n".format(sqrt(self.R2))
		
		return ret
	
	def test(self, a=None, B_10=0, B_00=0):
		ret = VariableContainer()
		
		ret["B_1"] = VariableContainer(indent=2)
		
		ret["B_1"]["T_0"] = (self.B_1 - B_10) / self.seB_1
		
		ret["B_1"]["P"] = tProb(ret["B_1"]["T_0"], self.n-2)
		
		ret["B_0"] = VariableContainer(indent=2)
		
		ret["B_0"]["T_0"] = (self.B_0 - B_00) / self.seB_0
		
		ret["B_0"]["P"] = tProb(ret["B_0"]["T_0"], self.n-2)
		
		if a is not None:
			ret["t_a,n-2"] = t(a, self.n - 2)
		
		ret["Regression"] = VariableContainer(indent=2)
		
		ret["Regression"]["F_0"] = self.MS_R / self.MS_E
		
		ret["Regression"]["P"] = fProb(ret["Regression"]["F_0"], 1, self.n-2)
		
		return ret
	
	def CI(self, a, x1=None, x2=None):
		ret = VariableContainer()
		
		B_1lower = self.B_1 - t(a/2, self.n-2)*self.seB_1
		B_1upper = self.B_1 + t(a/2, self.n-2)*self.seB_1
		ret["B_1"] = (B_1lower, B_1upper)
		
		B_0lower = self.B_0 - t(a/2, self.n-2)*sqrt( 1/self.n + self.xMean**2/self.S_xx )
		B_0upper = self.B_0 + t(a/2, self.n-2)*sqrt( 1/self.n + self.xMean**2/self.S_xx )
		ret["B_0"] = (B_0lower, B_0upper)
		
		
		if x1 is None:
			pass
		elif x2 is None:
			_x1 = x1
			_x2 = 0
			ret["y"] = ( x1*B_1lower + B_0lower , x1*B_1upper + B_0upper )
		else:
			ret["d"] = ( (x1 - x2)*B_1lower , (x1 - x2)*B_1upper )
		
		return ret

class ChiTable(Table):
	def __init__(self, data, sep=None):
		super().__init__(data, sep=sep)
		
		self.O = self.table[:]
		del self.table
		
		self.nRows = len(self.O)
		self.nCols = len(self.O[0])
		self.rowSums = [sum(row) for row in self.O]
		self.colSums = [sum(self.O[i][j] for i in range(self.nRows)) for j in range(self.nCols)]
		self.n = sum(self.rowSums)
		self.v = (self.nRows -1)*(self.nCols -1)
		
		self.E = [ [self.rowSums[i]*self.colSums[j]/self.n for j in range(self.nCols) ]  for i in range(self.nRows) ]
		
		self.Q = sum((self.O[i][j] - self.E[i][j])**2/self.E[i][j] for i in range(self.nRows) for j in range(self.nCols))
	
	def __str__(self):
		ret = VariableContainer()
		
		ret["O"] = self.O
		ret["E"] = self.E
		ret["Q"] = self.Q
		ret["P(X² < X²_0 )"] = chiProb(self.Q, self.v)
		
		return str(ret)

class P:
	def __init__(self, comparison):
		self.comparison = comparison
	
	def __float__(self):
		return self.comparison.P()

	# LOGIC OPERATOR, USED TO RETURN THE PROBABILITY OF A CONDITION
	def __gt__(self, right):
		if isinstance(right, Number):
			return Comparison(self, ">", right)
		else:
			return NotImplemented
		# return self.comparison.Pinv(">", right)
	def __ge__(self, right):
		if isinstance(right, Number):
			return Comparison(self, ">=", right)
		else:
			return NotImplemented
		# return self.comparison.Pinv(">=", right)
	def __eq__(self, right):
		if isinstance(right, Number):
			return Comparison(self, "==", right)
		else:
			return NotImplemented
		# return self.comparison.Pinv("==", right)
	def __ne__(self, right):
		if isinstance(right, Number):
			return Comparison(self, "!=", right)
		else:
			return NotImplemented
		# return self.comparison.Pinv("!=", right)
	def __le__(self, right):
		if isinstance(right, Number):
			return Comparison(self, "<=", right)
		else:
			return NotImplemented
		# return self.comparison.Pinv("<=", right)
	def __lt__(self, right):
		if isinstance(right, Number):
			return Comparison(self, "<", right)
		else:
			return NotImplemented
		# return self.comparison.Pinv("<", right)
	
	# MATH OPERATORS TO USE THE PROBABILITY 
	def __pow__(self, right):
		return float(self) ** right
	def __mul__(self, right):
		return float(self) * right
	def __truediv__(self, right):
		return float(self) / right
	def __floordiv__(self, right):
		return float(self) // right
	def __mod__(self, right):
		return float(self) % right
	def __sub__(self, right):
		return float(self) - right
	def __add__(self, right):
		return float(self) + right
	# RECIPROCAL OPERATORS
	def __rmul__(self, left):
		return left * float(self)
	def __rtruediv__(self, left):
		return left / float(self)
	def __rfloordiv__(self, left):
		return left // float(self)
	def __rmod__(self, left):
		return left % float(self)
	def __rsub__(self, left):
		return left - float(self)
	def __radd__(self, left):
		return left + float(self)
	
	# SIMPLY PRINTING THE PROBABILITY
	def __repr__(self):
		return f"<Probability '{self}' at {id(self):#x}>"
	def __str__(self):
		from GeekyGadgets.Formatting.SISize import roundSignificant
		return f"P({self.comparison}) -> {roundSignificant(float(self), 4)}"

	
