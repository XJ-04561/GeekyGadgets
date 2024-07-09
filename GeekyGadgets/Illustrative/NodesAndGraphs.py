
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

def xmlToDicts(text):
	tags = []
	for m in XML_TAG_PATTERN.finditer(text):
		tagDict = m.groupdict()
		attributes = {}
		for mAttr in XML_ATTRIBUTES_PATTERN.finditer(tagDict["attributes"]):
			name = mAttr.group("name")
			if mAttr.group("value").startswith("\"") or mAttr.group("value").startswith("'"):
				value = mAttr.group("value")[1:-1]
			else:
				value = mAttr.group("value")
			attributes[name] = value
		tagDict["attributes"] = attributes
		tags.append(tagDict)
		tags.extend(xmlToDicts(m.group("content")))
	return tags

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
		
		graph = cls()
		nodes : dict[str,Node] = {}
		prev = None
		for tag in xmlToDicts(file.read()):
			match tag["name"]:
				case "graph":
					graph.name = tag["attributes"]["id"]
				case "node":
					nodes[tag["attributes"]["id"]] = prev = cls.nodeClass(tag["attributes"]["id"], graph=graph)
					if not hasattr(graph, "root"):
						graph.root = prev
				case "edge":
					if tag["attributes"]["source"] in nodes:
						node, edge = nodes[tag["attributes"]["source"]].addNode(nodes[tag["attributes"]["target"]], tag["attributes"]["target"])
						prev = edge
					else:
						prev = DummyEdge()
				case "data":
					if tag["content"].isnumeric():
						prev.properties[tag["attributes"]["id"]] = int(tag["content"])
					elif "." in tag["content"] and len(tag["content"].split(".")) == 2 and all(x.isnumeric() for x in tag["content"].split(".")):
						prev.properties[tag["attributes"]["id"]] = float(tag["content"])
					else:
						prev.properties[tag["attributes"]["id"]] = tag["content"]
				case _:
					pass
				
		if not hasattr(graph, "root"):
			raise ValueError(f"Unrooted graph {graph}")

		return graph

	@overload
	def illustrate(self, outputFormat : Literal["HTML","PDF","SVG","PNG","GraphML"], *, encoding: str = "utf-8", nameProp=None, light : bool=True, dark : bool=False, **kwargs) -> bytes: ...
	@overload
	def illustrate(self, outputFormat : Literal["HTML","PDF","SVG","PNG","GraphML"], *, file : BinaryIO, encoding: str = "utf-8", nameProp=None, light : bool=True, dark : bool=False, **kwargs) -> None: ...
	def illustrate(self, outputFormat : Literal["HTML","PDF","SVG","PNG","GraphML"], *, file : BinaryIO=None, encoding: str = "utf-8", nameProp=None, light : bool=True, dark : bool=False, **kwargs) -> bytes|None:

		import math

		generations = [[self.root]]
		history = set()
		while generation := generations[-1]:
			nextGen = []
			for node in generation:
				for child in node.children:
					if child not in history and not child.hidden:
						nextGen.append(child)
						history.add(child)
			generations.append(nextGen)
		generations = generations[:-1]
		
		NODE_RADIUS = 20
		NODE_SPACE = NODE_RADIUS * 1.25

		WIDTH = 2*NODE_SPACE * len(max(generations, key=len))
		HEIGHT = 3*NODE_SPACE * len(generations)
		WIDTH, HEIGHT = max((WIDTH, WIDTH), (HEIGHT, HEIGHT))
		EDGE_WIDTH = round(NODE_RADIUS / 2)
		FONT_SIZE = round(NODE_RADIUS * 0.7)
		EDGE_THIN_WIDTH = 1
		# if dark:
		# 	NODE_FILL = "darkgray"
		# 	TEXT_COLOR = "#fdfdfd"
		# 	EDGE_COLOR = "#ff2020"
		# 	EMPTY_EDGE_COLOR = "#aaaaaa"
		# elif light:
		EDGE_COLOR = "#ff2020"
		EMPTY_EDGE_COLOR = "gray"


		match outputFormat:
			case "HTML":
				from GeekyGadgets.Semantics.Markup.HTML import HTML, Head, Body, Div, Canvas, Style, Script, Figure, Menu, Svg, H1
				from GeekyGadgets.Semantics.Markup.SVG import Path, Circle, RadialGradient, Stop, Text, Defs
				page = HTML(head := Head(), body := Body())

				head.addChild(Style(self.TEXT_DATA.ILLUSTRATE.HTML.CSS))
				body.addChild(
					fig := Figure(Class="TreeGraph primary").addChild(
						svg := Svg(id=self.name, Class="TreeGraph primary", width=f"{WIDTH}", height=f"{HEIGHT}", xmlns="http://www.w3.org/2000/svg")
					).addChild(
						menu := Menu(H1(self.name), Class="secondary")
				))
				menu.addChild(H1(self.name))
				
				nodePositions = {}
				for genI, generation in enumerate(generations):
					nodeY = HEIGHT * (genI+1)/(len(generations)+2)
					genSize = len(generation)
					
					for i, node in enumerate(generation):
						nodeX = WIDTH * (i+1)/(genSize+1)
						nodePositions[node] = (nodeX, nodeY)
				
				for edge in map(lambda x:x.incoming[0], Chain(*generations[1:])):
					startNode, endNode = edge.pair
					start = nodePositions[startNode]
					end = nodePositions[endNode]

					if isinstance(startNode, Directed):
						angle = math.pi * (startNode.outgoing.index(edge)+1) / (len(startNode.outgoing)+1)
					else:
						angle = 2 * math.pi * (startNode.connections.index(edge)) / (len(startNode.connections)) - math.pi
					offsetRadii = (abs(end[0] - start[0]), abs(end[1] - start[1]))
					startVector = (
						start[0]+offsetRadii[0]*(-math.cos(angle)),
						start[1]+offsetRadii[1]*(math.sin(angle)))
					endVector = (end[0], start[1])
					
					if isinstance(edge.weight, Number): # Colored thick stroke
						weight = max(min(edge.weight, 1.0), 0.0)
						svg.addChild(Path(
							name=str(node.name), 
							d=f"M {start[0]} {start[1]} "
							f"C {startVector[0]} {startVector[1]}, "
							f"{endVector[0]} {endVector[1]}, "
							f"{end[0]} {end[1]}",
							fill="transparent",
							stroke=f"{EDGE_COLOR}",
							strokeWidth=f"{EDGE_WIDTH*weight}",
							strokeOpacity=0.6))
						svg.addChild(Path(
							name=str(node.name), 
							d=f"M {start[0]} {start[1]} "
							f"C {startVector[0]} {startVector[1]}, "
							f"{endVector[0]} {endVector[1]}, "
							f"{end[0]} {end[1]}",
							fill="transparent",
							stroke=f"{EMPTY_EDGE_COLOR}",
							strokeWidth=f"{EDGE_THIN_WIDTH}",
							strokeOpacity=0.6))
				for node in nodePositions:
					nodeX, nodeY = nodePositions[node]
					svg.addChild(
						Text(
							node.name if nameProp is None else node.properties[nameProp],
							name=str(node.name),
							x=f"{nodeX+NODE_RADIUS}", y=f"{nodeY-EDGE_WIDTH}",
							fontSize=FONT_SIZE, fontFamily="verdana", textAnchor="left"
						)
					)
					svg.addChild(
						Circle(
							name=str(node.name),
							r=f"{NODE_RADIUS*0.9}", strokeWidth=NODE_RADIUS*0.2,
							cx=f"{nodeX}", cy=f"{nodeY}",
							fx=f"{nodeX}", fy=f"{nodeY}",
							stroke=node.color
						)
					)
					fig.addChild(
						Div()
					)
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
		
		if file is not None:
			file.write()
			return file.flush()
		else:
			return filedata if isinstance(filedata, bytes) else filedata.encode(encoding)

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

_D = TypeVar("_D", bound=Directed)
_G = TypeVar("_G", bound=Directed)

class Node(ABC):
	name : str
	graph : _G
	properties : dict[str,Any]
	connections : list
	hidden : bool = False

	color = "darkgray"
	def __init__(self, name : str, *, graph : _G|None=None, **properties) -> None:
		self.name = name
		self.connections = []
		if graph is not None:
			self.graph = graph
		self.properties = properties
	
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
		self.properties = properties

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
	incoming : "Leaf" = property(lambda self:self.pair[0], lambda self, value: setattr(self, "pair", (value, self.pair[1])), lambda self: setattr(self, "pair", (None, self.pair[1])))
	outgoing : "Leaf" = property(lambda self:self.pair[1], lambda self, value: setattr(self, "pair", (self.pair[0], value)), lambda self: setattr(self, "pair", (self.pair[0], None)))
	
	def __iter__(self) -> Generator["Leaf",None,None]:
		yield self.outgoing

class Leaf(Node, Directed):
	graph : "Tree"
	incoming : list[Branch]
	outgoing : list[Branch]
	parent : Branch = property(lambda self: self.incoming[0].incoming)
	children : list[Branch] = property(lambda self: [edge.outgoing for edge in self.outgoing])
	connections : "list[_D]|_D" = property(lambda self: list(Chain(self.incoming, self.outgoing)), lambda self, value:None)
	hidden : bool = False

	def __init__(self, name : str, incoming : list[Branch]=None, outgoing : list[Branch]=None, *, graph : _G|None=None, **properties) -> None:
		self.name = name
		self.incoming = incoming if incoming is not None else []
		self.outgoing = outgoing if outgoing is not None else []
		self.graph = graph if graph is not None else getattr(self, "graph", None)
		self.properties = properties
		
	def __iter__(self) -> Generator["Branch",None,None]:
		for branch in self.outgoing:
			yield branch

	def addNode(self, node : "str|Leaf", edge : "str|Branch", **kwargs):
		if isinstance(node, str):
			node = type(self)(node, graph=self.graph, **kwargs)
		if isinstance(edge, str):
			edge = self.graph.edgeClass(edge, (self, node), graph=self.graph)
		self.outgoing.append(edge)
		node.incoming.append(edge)
		return node, edge

class Tree(Graph, Directed):
	from GeekyGadgets.Illustrative.TextData import Tree as TEXT_DATA
	nodeClass : "type[Leaf]" = Leaf
	edgeClass : "type[Branch]" = Branch
