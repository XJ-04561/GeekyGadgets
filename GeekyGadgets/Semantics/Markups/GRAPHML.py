
from GeekyGadgets.Semantics.Markups import Globals as _Globals

# ATTRS = ["id", "For", "source", "target", "edgedefault", "key"]

# class GraphmlAttributes(_Globals.Attributes):
# 	def __str__(self):
# 		return str(_Globals.Attributes(**{(name.lower() if name in ATTRS else f"attr.{name}"):value for name, value in self.items()}))

class GRAPHML(_Globals.Markup):

	_explicitAttributeNames = ["xsi:schemaLocation"]
	
	def compile(self, encoding="utf-8"):
		return f"<?xml version=\"1.0\" encoding={encoding.upper()!r}?>\n"+str(self)

class GraphML(GRAPHML, tagName="graphml"):
	def __init__(self: "GraphML", *content: _Globals.AnyStr | _Globals.Markup, **attributes: _Globals.AnyStr | int | float | bool) -> _Globals.NoneType:
		super().__init__(
			*content,
			**({
				"xmlns" : "http://graphml.graphdrawing.org/xmlns",
    			"xmlns:xsi" : "http://www.w3.org/2001/XMLSchema-instance",
    			"xsi:schemaLocation" : "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
			} | attributes)
		)
	
class Graph(GRAPHML): ...
class Key(GRAPHML): ...
class Data(GRAPHML): ...
class Node(GRAPHML): ...
class Edge(GRAPHML): ...
class Default(GRAPHML): ...
class Hyperedge(GRAPHML): ...
class Port(GRAPHML): ...