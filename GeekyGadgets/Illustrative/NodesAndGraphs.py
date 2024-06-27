
from typing import Any
from GeekyGadgets.Globals import *
from GeekyGadgets.Iterators import Walker, Chain, GraphWalker, NodeWalker, EdgeWalker
from GeekyGadgets.SpecialTypes import NameSpace, Pair
from GeekyGadgets.Classy import Default
from GeekyGadgets.Semantics.Globals import Attributes

XML_TAG_PATTERN = re.compile(r"(?P<indentation>\s*)"
							 r"[<](?P<name>\w+)"
							 	r"(?P<attributes>"
									r"(?:\s+"
										r"(?:\w+[=]"
											r"(?:[\"].*?[\"]|['].*?[']|\S*?)"
										r")"
									r")*"
								r")?"
							 r"\s*[>]"
							 r"(?P<content>.*?)"
							 r"(?P=indentation)"
							 r"[<]/(?P=name)[>]", flags=re.DOTALL)
XML_ATTRIBUTES_PATTERN = re.compile(r"\s*"
									r"(?P<name>\w+)[=]"
									r"(?P<value>[\"].*?[\"]|['].*?[']|\S*?)", flags=re.DOTALL)

class Graph(ABC):
	
	TEXT_DATA : NameSpace

	nodeClass : "type[Node]"
	edgeClass : "type[Edge]"

	name : str
	properties : dict[str,Attributes]
	root : "Node"
	size : int

	@classmethod
	def fromGraphML(cls : "type[Graph]", file : TextIO):

		file.seek(0)
		freshContent = [file.read()]
		tags = []
		while freshContent:
			for m in XML_TAG_PATTERN.finditer(freshContent.pop()):
				freshContent.append(m.group("content"))
				tags.append(m.groupdict())
		
		graph = cls()
		nodes : dict[str,Node] = {}
		edges : list[tuple[str,str]] = []
		prev = None
		for tag in tags:
			match tag["name"]:
				case "node":
					attributes = {}
					for m in XML_ATTRIBUTES_PATTERN.finditer(tag["attributes"]):
						name = m.group("name")
						if m.group("value").startswith("\"") or m.group("value").startswith("'"):
							value = m.group("value")[1:-1]
						else:
							value = m.group("value")
						attributes[name] = value
					nodes[attributes["id"]] = prev = cls.nodeClass(attributes["id"], graph=graph)
				case "edge":
					attributes = {}
					for m in XML_ATTRIBUTES_PATTERN.finditer(tag["attributes"]):
						name = m.group("name")
						if m.group("value").startswith("\"") or m.group("value").startswith("'"):
							value = m.group("value")[1:-1]
						else:
							value = m.group("value")
						attributes[name] = value
					if attributes["source"] in nodes:
						node, edge = nodes[attributes["source"]].addNode(nodes[attributes["target"]], attributes["target"])
						prev = edge
					else:
						prev = DummyEdge()
				case "data":
					attributes = {}
					for m in XML_ATTRIBUTES_PATTERN.finditer(tag["attributes"]):
						name = m.group("name")
						if m.group("value").startswith("\"") or m.group("value").startswith("'"):
							value = m.group("value")[1:-1]
						else:
							value = m.group("value")
						attributes[name] = value
					
					if tag["content"].isnumeric():
						prev.properties[attributes["id"]] = int(tag["content"])
					elif "." in tag["content"] and len(tag["content"].split(".")) == 2 and all(x.isnumeric() for x in tag["content"].split(".")):
						prev.properties[attributes["id"]] = float(tag["content"])
					else:
						prev.properties[attributes["id"]] = tag["content"]
		for node in nodes.values():
			graph.root = node
			break

		return graph

	def illustrate(self, outputFormat : Literal["HTML","PDF","SVG","PNG","GraphML"], *, filename : str=None, encoding: str = "utf-8", nameProp=None, light : bool=True, dark : bool=False, **kwargs):

		import math
		if filename is None:
			filename = f"{self.name}.{outputFormat.lower()}"

		generations = [[self.root]]
		history = set()
		while generation := generations[-1]:
			nextGen = []
			for node in generation:
				for edge in node.connections:
					start, end = edge.pair
					if node == start:
						if end not in history:
							nextGen.append(end)
							history.add(end)
			generations.append(nextGen)
		generations = generations[:-1]

		# 50 points per node
		WIDTH = 50 * len(max(generations, key=len))
		HEIGHT = 50 * len(generations)
		NODE_RADIUS = round(min(WIDTH, HEIGHT) * 0.02)
		EDGE_WIDTH = round(NODE_RADIUS / 2)
		FONT_SIZE = round(NODE_RADIUS * 0.7)
		EDGE_THIN_WIDTH = max(round(NODE_RADIUS * 0.1), 1)
		if dark:
			NODE_FILL = "darkgray"
			TEXT_COLOR = "#fdfdfd"
			EDGE_COLOR = "#ff2020"
			EMPTY_EDGE_COLOR = "#aaaaaa"
		elif light:
			NODE_FILL = "white"
			TEXT_COLOR = "#202020"
			EDGE_COLOR = "#ff2020"
			EMPTY_EDGE_COLOR = "gray"


		match outputFormat:
			case "HTML":
				from GeekyGadgets.Semantics.Markup.HTML import HTML, Head, Body, Div, Canvas, Style, Script, Figure, Menu, Svg
				from GeekyGadgets.Semantics.Markup.SVG import Path, Circle, RadialGradient, Stop, Text
				page = HTML(head := Head(), body := Body())

				head.addChild(Style(self.TEXT_DATA.ILLUSTRATE.HTML.CSS))
				body.addChild(
					Figure(Class="TreeGraph primary").addChild(
						svg := Svg(id=self.name, Class="TreeGraph primary", width=f"{WIDTH}", height=f"{HEIGHT}", xmlns="http://www.w3.org/2000/svg")
					).addChild(
						Menu(Class="secondary")))
				
				nodePositions = {}
				for genI, generation in enumerate(generations):
					nodeY = HEIGHT * i/(len(generations)+1)
					genSize = len(generation)
					
					for i, node in enumerate(generation):
						nodeX = WIDTH * (i+1)/(genSize+1)
						svg.addChild(Text(node.name if nameProp is None else getattr(node.properties, nameProp), name=str(node.name), x=f"{nodeX+NODE_RADIUS}", y=f"{nodeY-EDGE_WIDTH}", fill=f"{TEXT_COLOR}", fontSize=FONT_SIZE, fontFamily="verdana", textAnchor="left"))
						svg.addChild(nodeGradient := RadialGradient(name=str(node.name), r=f"{NODE_RADIUS}", cx=f"{nodeX}", cy=f"{nodeY}", fx=f"{nodeX}", fy=f"{nodeY}"))
						nodeGradient.addChild(Stop(offset="0%", stopColor=NODE_FILL))
						nodeGradient.addChild(Stop(offset="85%", stopColor=NODE_FILL))
						nodeGradient.addChild(Stop(offset="100%", stopColor=node.color))
						nodePositions[node] = (nodeX, nodeY)
				
				for edge in EdgeWalker(self):
					startNode, endNode = edge.pair
					start = nodePositions[startNode]
					end = nodePositions[endNode]

					angle = math.pi * (startNode.outgoing.index(edge)+1) / (len(startNode.outgoing)+1)
					offsetRadii = (abs(end[0] - start[0]), abs(end[1] - start[1]))
					startVector = (
						start[0]+offsetRadii[0]*(-math.cos(angle)),
						start[1]+offsetRadii[1]*(math.sin(angle)))
					endVector = (start[0], end[1])
					
					if isinstance(edge.weight, Number): # Colored thick stroke
						weight = max(min(edge.weight, 1.0), 0.0)
						svg.addChild(Path(
							name=str(node.name), 
							d=f"M {start[0]} {start[1]} "
							f"C {startVector[0]} {startVector[1]}, "
							f"{endVector[0]} {endVector[1]}, "
							f"{end[0]} {end[1]}",
							strokeWidth=f"{EDGE_WIDTH*weight}",
							fill=f"{EDGE_COLOR}",
							fillOpacity=0.6))
					else: # Dashed thin stroke
						svg.addChild(Path(
							name=str(node.name), 
							d=f"M {start[0]} {start[1]} "
							f"C {startVector[0]} {startVector[1]}, "
							f"{endVector[0]} {endVector[1]}, "
							f"{end[0]} {end[1]}",
							strokeWidth=f"{EDGE_THIN_WIDTH}",
							fill=f"{EMPTY_EDGE_COLOR}",
							fillOpacity=0.6))
				
				filedata = str(page)
					
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
	
	def __hash__(self):
		return hash(self.name)
	
	def __eq__(self, other):
		if isinstance(other, Hashable):
			return hash(self) == hash(other)
		else:
			return NotImplemented

class Directed:
	incoming : "Iterable[_D]|_D"
	outgoing : "Iterable[_D]|_D"
	connections : "list[_D]|_D" = property(lambda self: list(Chain(self.incoming, self.outgoing)), lambda self, value:None)
	def __init__(self : "_D", *, incoming : "Iterable[_D]|_D|None"=None, outgoing : "Iterable[_D]|_D|None"=None) -> None:
		if incoming is not None:
			self.incoming = incoming
		else:
			self.incoming = []
		if outgoing is not None:
			self.outgoing = outgoing
		else:
			self.outgoing = []
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
	connections : list

	color = "darkgray"
	def __init__(self, name : str, *, graph : _G|None=None, **properties) -> None:
		self.name = name
		self.connections = []
		if graph is not None:
			self.graph = graph
		self.properties = NameSpace(properties)
	
	def __hash__(self):
		return hash((self.name, self.graph))
	
	def __eq__(self, other):
		if isinstance(other, Hashable):
			return hash(self) == hash(other)
		else:
			return NotImplemented
	
	def addNode(self, node : "str|Node", edge : "str|Edge", **kwargs):
		if isinstance(node, str):
			node = type(self)(node, graph=self.graph, **kwargs)
		if isinstance(edge, str):
			edge = self.graph.edgeClass(edge, (self, node), graph=self.graph)
		self.connections.append(edge)
		node.connections.append(edge)
		return node, edge

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

class DummyEdge:
	def __getattribute__(self, name: str) -> Any:
		return self
	def __setattribute__(self, name, value):
		return None
	def __getitem__(self, name):
		return self
	def __setitem__(self, name, value):
		return None
	def __call__(self, *args, **kwargs):
		return self

Graph.edgeClass = Edge
Graph.nodeClass = Node

class Branch(Edge, Directed):
	graph : "Tree"

class Leaf(Node, Directed):
	graph : "Tree"
	incoming : list[Branch]
	outgoing : list[Branch]

	def addNode(self, node : "str|Leaf", edge : "str|Branch", **kwargs):
		if isinstance(node, str):
			node = type(self)(node, graph=self.graph, **kwargs)
		if isinstance(edge, str):
			edge = self.graph.edgeClass(edge, (self, node), graph=self.graph)
		self.outgoing.append(edge)
		node.incoming.append(edge)
		return node, edge

class Tree(Graph, Directed):
	nodeClass : "type[Leaf]" = Leaf
	edgeClass : "type[Branch]" = Branch
