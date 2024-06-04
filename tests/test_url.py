

from GeekyGadgets.URL import *

def test_subclassing():
	class CUSTOM_SCHEME(URL): ...

	assert CUSTOM_SCHEME.SCHEME == "custom-scheme"
	url1 = CUSTOM_SCHEME("myLink")

	assert url1 == "custom-scheme://myLink"
	assert url1.LINK == "myLink"

	try:
		url2 = URL("myLink")
	except AmbiguousURL as e:
		assert isinstance(e, AmbiguousURL)
	
	url2 = URL("custom-scheme://myLink")

	assert isinstance(url2, URL)
	assert isinstance(url2, CUSTOM_SCHEME)

	assert url1.SCHEME == url2.SCHEME
	assert url1.LINK == url2.LINK
	assert url1 == url2

	url3 = FILE("/home/fresor/Documents/homework.docx")

	assert isinstance(url3, FILE)
	assert url3 == "file:///home/fresor/Documents/homework.docx"

def test_creation():
	pass

def test_templating():
	pass

def test_ping():
	pass