
from GeekyGadgets.Globals import *
import urllib.request as ur
_T = TypeVar("_T")

__all__ = (
	"URLError", "AmbiguousURL", "BadURL", "URL", "URL_TEMPLATE", "HTTPS", "HTTP", "FTP", "MAILTO", "FILE", "DATA",
	"IRC", "ping")

class URLError(Exception): pass
class AmbiguousURL(URLError): pass
class BadURL(URLError): pass

class URL(str):
	"""This class can be used for class-checking that a string is intended to be used as a URL. For subclasses of 
	`URL`, the lowercase transformed version of the class name is used as the SCHEME of the link (Underscores `_` 
	"are converted to hyphens `-`), meaning it will be prepended to the link if it does not already exist. This class 
	also evaluates the regular expression `URL._URL_PATTERN` on each created `URL` object, and stores the retrieved 
	fields in properties of the same names.
	### Example
	```python
	class HTTPS(URL): ...
	
	myLink = HTTPS("GitHub.com/XJ-04561/GeekyGadgets")
	# creates a `HTTPS` object that inherits behavior from `str` objects.

	print(myLink)
	# "https://GitHub.com/XJ-04561/GeekyGadgets"
	print(myLink.SCHEME)
	# "https"
	print(myLink.LINK)
	# "GitHub.com/XJ-04561/GeekyGadgets"
	```
	"""

	_CLASS_CREATION_LOCK : threading.Lock = threading.Lock()
	"""This lock is used so that different threads don't create the same class twice. The same class created twice 
	will fail identity checks like `A1 is A2`, `A1 == A2`, and isinstance(A1(), A2).
	### Example
	```python
	>>> class A: pass
	...
	>>> B = A
	>>> class A: pass
	...
	>>> A is A
	True
	>>> A is B
	False
	>>> A == B
	False
	>>> isinstance(A(), B)
	False
	```"""
	_SCHEME_PATTERN = re.compile(r"^(?P<SCHEME>[a-zA-Z][a-zA-Z0-9+.-]*)[:].*$")
	_URL_PATTERN = re.compile(r"""
	(?:(?:[a-zA-Z]|[{].*?[}])(?:[a-zA-Z0-9+.-]|[{].*?[}])*)[:]
	(?:[/]{2}(?P<AUTHORITY>
		(?:(?P<USERINFO>
			(?P<USERNAME>(?:[\w_-]|[{].*?[}])+)
			(?:[:](?P<PASSWORD>.+))?
			)[@]
		)?
		(?P<HOST>(?:[\w.]|[{].*?[}])+|\[(?:[0-fF:]|[{].*?[}])+\])
		(?:[:](?P<PORT>(?:[0-9]|[{].*?[}])+))?
	))?
	(?P<PATH>(?:[\w_/.-]|[{].*?[}])*)
	(?:[?](?P<QUERY>(?:[\w&;:,=_-]|[{].*?[}])*))?
	(?:[#](?P<FRAGMENT>(?:[\w_-]|[{].*?[}])*))?
	""".replace("\t", "").replace("\n", "").replace("\r", ""))
	"""Pseudo-pattern (Optional enclosed in brackets `[ ]`):
	`SCHEME:[//AUTHORITY]PATH[?QUERY][#FRAGMENT]`
	where AUTHORITY consists of: `[USERINFO@]HOST[:PORT]`
		where USERINFO consists of: `USERNAME[:PASSWORD]`
	"""

	SCHEME : str
	AUTHORITY : str
	USERINFO : str
	USERNAME : str
	PASSWORD : str
	HOST : str
	PORT : str
	PATH : str
	"""Will use `/` as separator regardless of platform."""
	QUERY : str
	FRAGMENT : str
	LINK : str

	exists : bool

	def __new__(cls, string, **kwargs):
		"""Instantiate a URL object. If calling using the base class `URL` then the `SCHEME` is determined from 
		the string itself. If no class of this scheme exists, it will be created.
		
		If calling using a subclass of URL, and the scheme is not already prepended to the string, the scheme will be 
		prepended along with "://"."""
		_string = str(string).replace("\\", "/")

		if cls is URL:
			
			scheme = cls._SCHEME_PATTERN.fullmatch(_string)
			if scheme and (scheme := scheme.group("SCHEME")):
				with cls._CLASS_CREATION_LOCK:
					for subClass in URL.__subclasses__():
						if subClass.SCHEME == scheme:
							cls = subClass
							break
					else:
						cls = type(scheme.upper(), (URL,), {})
			else:
				raise AmbiguousURL("Attempted to create a URL object using the URL base class and "
									f"string {_string!r}, this string does not have a scheme prepended to it. "
									"Please instantiate using the specific URL type you are intending to use.")
		elif _string.startswith(cls.SCHEME+":"):
			pass
		else:
			_string = cls.SCHEME+"://"+_string
		
		sectionsMatch = cls._URL_PATTERN.fullmatch(_string)
		
		if sectionsMatch is None:
			raise BadURL(f"Attempt at creating `URL` object thwarted due to incorrect URL formating IN {_string!r}. "
							"URLs are only expected to contain specific characters defined in "
							"the regex `URL._URL_PATTERN`.")
		else:
			sections = sectionsMatch.groupdict()
		
		newPath = sections["PATH"].replace("\\", "/")
		obj = super().__new__(cls, _string.replace(sections["PATH"], newPath, 1), **kwargs)
		sections["PATH"] = newPath

		for name, value in sections.items():
			setattr(obj, name, value)
		
		# Unsure how to handle the '//', since it is only used when `AUTHORITY` is present, but it should be included
		# when using a `FILE`-url like: file:///home/fresor/Documents/homework.docx
		obj.LINK = obj.removeprefix(obj.SCHEME+"://")

		# if obj.AUTHORITY:
		# 	obj.LINK = obj.removeprefix(obj.SCHEME+"://")
		# else:
		# 	obj.LINK = obj.removeprefix(obj.SCHEME+":")
		
		return obj

	def __init_subclass__(cls) -> None:
		super().__init_subclass__()
		cls.SCHEME = cls.__name__.lower().replace("_", "-")
	
	def format(self : _T, *args : object, **kwargs : object) -> _T:
		"""Return the URL but all {}-marked field replaced by the provided values. This method uses ``str.format``."""
		return type(self)(super().format(*args, **kwargs))
	
	@property
	def exists(self):
		return ping(self) is not None

class URL_TEMPLATE(str):
	"""Inherits behavior from `str` objects with format fields.

	When a formattable link needs more complex formatting, create a class the inherits from this class, defining 
	the class' `url` to be a formattable string, and defining a `complexFormat` method.
	
	The base class' `complexFormat` method raises `NotImplementedError`, which is catched by the class' `format` 
	method, which then instead returns the result of calling `.format` directly on the class' `url` attribute.
	
	### Example
	```python
	class HTTPS(URL): ...
	class MySocialMediaLink(URL_TEMPLATE):
		url = HTTPS("www.mySocialMedia.com/{region}/{userHash}/")
		formatters = (
			{
				"europe" : "eu",
				"north america" : "NA",
				"south america" : "SA",
				"middle east" : "ME",
				"asia" : "AS",
				"china" : "CN",
				"south africa" : "ZA"
			},
		)

		@classmethod
		def complexFormat(cls, region : str, username : str):
			from hashlib import md5
			return cls.url.format(region=cls.formatters[0][region], userHash=md5(username.encode("utf-8")).hexdigest())
	
	myLink = MySocialMediaLink.format("europe", "XJ-04561")
	# creates a `HTTPS` object that inherits behavior from `str` objects.

	print(myLink)
	# "https://www.mySocialMedia.com/EU/1b01e924faa7ee9ccc8fbb8cae192c94/"
	print(myLink.SCHEME)
	# "https"
	print(myLink.PREFIX)
	# "https://"
	print(myLink.LINK)
	# "www.mySocialMedia.com/EU/1b01e924faa7ee9ccc8fbb8cae192c94/"
	```
	"""

	url : URL
	formatters : tuple = ()

	def __new__(cls, *args, **kwargs):
		"""Instantiating this class results in the same output as the class' 'format' method. All arguments are passed 
		on to it and the resulting string is returned."""
		return cls.format(*args, **kwargs)

	@classmethod
	def complexFormat(cls, *args, **kwargs) -> URL:
		"""Not implemented in the base class, if not implemented, the calling function should catch 
		the raised NotImplementedError in order to implement a backup. The base class uses the cls.url.format method 
		as a backup."""
		raise NotImplementedError(f"'complexFormat' not implemented in {cls!r}")

	@classmethod
	def format(cls, *args, **kwargs) -> URL:
		"""Simply passes arguments on to the str.format method of the class' 'url' object and return the results of 
		the formatting."""
		try:
			return cls.complexFormat(cls.url, *args, **kwargs)
		except NotImplementedError:
			return cls.url.format(*args, **kwargs)


class HTTPS(URL): ...
class HTTP(URL): ...
class FTP(URL): ...
class MAILTO(URL): ...
class FILE(URL): ...
class DATA(URL): ...
class IRC(URL): ...

def ping(url : URL|str) -> float|None:
	"""Use `urllib.request.urlopen` to try to open `url` and return time from function call to HTTP responsestatus code check. If url can't be reached with an HTTP response status code lower than 400, `None` is returned."""
	start = timer()
	try:
		with ur.urlopen(url) as response:
			if response.status < 400:
				return timer() - start
	except:
		pass
	return None