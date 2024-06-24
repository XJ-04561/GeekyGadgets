
from GeekyGadgets.Globals import *
from GeekyGadgets.Iterators import Walker, Chain, GraphWalker, NodeWalker, EdgeWalker
from GeekyGadgets.SpecialTypes import NameSpace, Pair
from GeekyGadgets.Classy import Default
from GeekyGadgets.Semantics.Globals import Attributes

class Graph(ABC):
	
	TEXT_DATA : NameSpace

	name : str
	properties : dict[str,Attributes]
	root : "Node"
	size : int

	def illustrate(self, outputFormat : Literal["HTML","PDF","SVG","PNG","GraphML"], *, filename : str=None, encoding: str = "utf-8", **kwargs):
		if filename is None:
			filename = f"{self.name}.{outputFormat.lower()}"

		match outputFormat:
			case "HTML":
				from GeekyGadgets.Semantics.Markup.HTML import HTML, Head, Body, Div, Canvas, Style, Script, Figure, Menu, Svg
				from GeekyGadgets.Semantics.Markup.SVG import Path
				page = HTML(head := Head(), body := Body())

				head.addChild(Style(self.TEXT_DATA.ILLUSTRATE.HTML.CSS))
				body.addChild(
					Figure(Class="TreeGraph primary").addChild(
						svg := Svg(id=self.name, Class="TreeGraph primary", width="1000", height="750", xmlns="http://www.w3.org/2000/svg")
					).addChild(
						Menu(Class="secondary")))
				generations = [[self.root]]
				history = set()
				while generation := generations[-1]:
					for node in generation:
						node.connections
				for edge in EdgeWalker(self):
					start = ("x", "y")
					startVector = ("x", "y")
					endVector = ("x", "y")
					end = ("x", "y")
					svg.addChild(Path(d="M {start[0]} {start[1]} "
					   					"C {startVector[0]} {startVector[1]}, "
										"{endVector[0]} {endVector[1]}, "
										"{end[0]} {end[1]}"))
					
			case "PDF":
				raise NotImplementedError(f"`PDF` output is not implemented yet")
			case "SVG":
				raise NotImplementedError(f"`SVG` output is not implemented yet")
			case "PNG":
				raise NotImplementedError(f"`PNG` output is not implemented yet")
			case "GraphML":
				HEADER = []
				BODY = []

				for Id, attributes in self.properties:
					if "default" in attributes:
						HEADER.append(
							f"  <key id=\"{Id}\" for=\"{attributes['for']}\" attr.name=\"{attributes.name}\" attr.type=\"{attributes.type}\">\n"
							f"    <default>{attributes.default if attributes.default is not None else 'NaN'}</default>\n"
							"  </key>\n")
					else:
						HEADER.append("  <key id=\"genotype\" for=\"node\" attr.name=\"Variant\" attr.type=\"string\"/>\n")
				HEADER.append(f"  <graph id=\"{self.name}\" edgedefault=\"{'directed' if isinstance(self, Directed) else 'undirected'}\">\n")

				for node in NodeWalker(self):
					BODY.append(f"    <node id=\"{node.name}\">\n")
					for Id, attributes in self.properties:
						if attributes["for"] == "node" and Id in node.properties:
							BODY.append(f"      <data id=\"{Id}\">{node.properties[Id]}</data>\n")
					BODY.append("    </node>\n")

				for edge in EdgeWalker(self):
					BODY.append(f"    <edge id=\"{edge.name}\" source=\"{edge.pair[0]}\" target=\"{edge.pair[1]}\">\n")
					for Id, attributes in self.properties:
						if attributes["for"] == "edge" and Id in edge.properties:
							BODY.append(f"      <data id=\"{Id}\">{edge.properties[Id]}</data>\n")
					BODY.append(f"    </edge>\n")
				
				filedata = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
				"<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\"  \n"
				"    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
				"    xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd\">\n"
				f"{HEADER}"
				f"{BODY}"
				"  </graph>\n"
				"</graphml>\n").encode(encoding)
			case _:
				raise ValueError(f"{outputFormat=} is not a recognized output format name. Recognized names: `HTML`, `PDF` ,`SVG` ,`PNG` ,`GraphML`")
		
		with open(filename, "wb") as outFile:
			outFile.write(filedata)

	@property
	def size(self):
		return sum(1 for _ in GraphWalker(self.root, key=lambda x:x.connections))

class Directed:
	incoming : "Iterable[_D]|_D"
	outgoing : "Iterable[_D]|_D"
	connections : "Iterable[_D]|_D" = property(lambda self: Chain(self.incoming, self.outgoing))
	def __init__(self : "_D", *, incoming : "Iterable[_D]|_D|None"=None, outgoing : "Iterable[_D]|_D|None"=None) -> None:
		if incoming is not None:
			self.incoming = incoming
		if outgoing is not None:
			self.outgoing = outgoing
	def __init_subclass__(cls) -> None:
		if issubclass(cls, Edge):
			cls.incoming = property(lambda self:(self.pair[0],), lambda self, value: setattr(self, "pair", (value, self.pair[1])), lambda self: setattr(self, "pair", (None, self.pair[1])))
			cls.outgoing = property(lambda self:(self.pair[1],), lambda self, value: setattr(self, "pair", (self.pair[0], value)), lambda self: setattr(self, "pair", (self.pair[0], None)))

_D = TypeVar("_D", bound=Directed)
_G = TypeVar("_G", bound=Directed)

class Node(ABC):
	name : str
	graph : _G
	properties : dict[str,Any]
	connections : Iterable
	def __init__(self, name : str, *, graph : _G|None=None, **properties) -> None:
		self.name = name
		if graph is not None:
			self.graph = graph
		self.properties = NameSpace(properties)

class Edge(ABC):
	name : str
	graph : _G
	properties : dict[str,Any]
	pair : set[Node,Node]
	connections : Iterable
	def __init__(self, name : str, pair : Iterable[Node,Node], *, graph : _G|None=None, **properties) -> None:
		self.name = name
		self.pair = Pair(pair)
		if graph is not None:
			self.graph = graph
		self.properties = NameSpace(properties)

class Path(list):
	def prepend(self, object: Any) -> None:
		self.insert(0, object)

class Tree(Graph, Directed): ...

class Branch(Edge, Directed): ...

class Leave(Node, Directed): ...