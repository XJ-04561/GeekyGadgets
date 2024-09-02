
import GeekyGadgets.Illustrative.Globals as _GL

import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Iterators.Walkers as _Walkers
import GeekyGadgets.SpecialTypes as _SPT
import GeekyGadgets.Functions as _Funcs
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Semantics.Markups as _Markups
import GeekyGadgets.IO as _IO
import GeekyGadgets.DataFormats as _DataFormats
import GeekyGadgets.Semantics.Markups.HTML as _HTML
import GeekyGadgets.Semantics.Markups.GRAPHML as _GRAPHML

__all__ = ("Graph", "Edge", "Node", "RootNode", "Directed", "Tree", "Branch", "Leaf", "TreeRoot")

class HasPropertyDefaults:
	
	propertyNames : _GL.Iterator[str] = _Classy.ClassDefault(lambda self: map(_Funcs.first, self.properties), default=_GL.NON_ITER)
	propertyTypes : _GL.Iterator[str] = _Classy.ClassDefault(lambda self: map(_Funcs.second, self.properties), default=_GL.NON_ITER)
	properties : _Iterators.Zip[tuple[str,str]] = _Classy.ClassDefault(lambda self: zip(self.propertyNames, self.propertyTypes), default=_GL.NON_ITER)

	def __getattr__(self, name : str):
		if name in self.propertyNames:
			return None
		else:
			raise AttributeError(f"`{self.__class__.__name__}` object does not have an attribute {name!r}")
	def __setattr__(self, name : str, value : _GL.Any):
		if name in self.propertyNames:
			if value is not None:
				return super().__setattr__(name, value)
		else:
			return super().__setattr__(name, value)

class HashedByID:
	
	id : _GL.Hashable = _Classy.Default(lambda self: hex(id(self)))
	"""Defaults to `id(self)`"""

	def __hash__(self):
		return hash(self.id)
	
	def __eq__(self, other):
		if isinstance(other, _GL.Hashable):
			return hash(self) == hash(other)
		else:
			return NotImplemented

class OwnedByGraph:
	
	graph : "Graph"

	@_Classy.Default
	def graph(self) -> "Graph|None":
		return None
	@graph.setter
	def graph(self, graph) -> None:
		if not isinstance(graph, Graph):
			pass
		elif isinstance(self, Node):
			graph.allNodes.add(self)
		elif isinstance(self, Edge):
			graph.allEdges.add(self)
	@graph.deleter
	def graph(self) -> None:
		if not isinstance(self.graph, Graph):
			pass
		elif isinstance(self, Node):
			self.graph.allNodes.discard(self)
		elif isinstance(self, Edge):
			self.graph.allEdges.discard(self)

class Graph(HashedByID, HasPropertyDefaults, _GL.Illustrator):

	HTML : _SPT.NameSpace = _SPT.NameSpace(
		JS=open(_GL.os.path.join(_GL.os.path.split(__file__)[0], "JS", "Graph.js"), "r").read(),
		CSS=open(_GL.os.path.join(_GL.os.path.split(__file__)[0], "CSS", "Graph.css"), "r").read()
	)

	rootClass : "type[RootNode]"
	nodeClass : "type[Node]"
	edgeClass : "type[Edge]"

	id : str
	name : str = _Classy.Default(lambda self: str(self.id))

	root : "Node" = _GL.cached_property(lambda self: RootNode(anchor="CENTER", graph=self))
	size : int = _Classy.CachedDefault["allNodes"](lambda self: len(self.allNodes))

	allNodes : "_SPT.HashedSet[Node]" #type: ignore
	allEdges : "_SPT.HashedSet[Edge]" #type: ignore
	endNodes : "_SPT.HashedSet[Node]" = property(lambda self: filter(lambda n:len(n.connections)<=1, self.allNodes)) #type: ignore

	def __init__(self) -> _GL.NoneType:
		self.allNodes = _SPT.HashedSet()
		self.allNodes.add(self.root)
		self.allEdges = _SPT.HashedSet()
		super().__init__()

	def illustrateCSV(self, *, file: _GL.TextIO = None, csv : _DataFormats.CSV|None=None, **kwargs) -> _DataFormats.TextDataInterpreter:
		
		csvTable = csv or _DataFormats.CSV()
		if not csvTable.header:
			csvTable.addHeader([self.__class__.__name__, "id|string", *(f"{name}|{tp}" for name, tp in self.properties), "rootID|string"])
			csvTable.addHeader([self.rootClass.__name__, "id|string", "graphID|string", *(f"{name}|{tp}" for name,tp in self.rootClass.properties)])
			csvTable.addHeader([self.nodeClass.__name__, "id|string", "graphID|string", *(f"{name}|{tp}" for name,tp in self.nodeClass.properties), "*edgeID|string"])
			csvTable.addHeader([self.edgeClass.__name__, "id|string", "graphID|string", *(f"{name}|{tp}" for name,tp in self.edgeClass.properties), "fromID|string","toID|string"])
		
		# Add the graph itself.
		csvTable.add([self.__class__.__name__, self.id, *(getattr(self, name, "") for name,tp in self.properties), self.root.id])
		for item in self.walk():
			if isinstance(item, self.rootClass):
				csvTable.add([item.__class__.__name__, item.id, self.id, *(getattr(item, name, "") for name,tp in item.properties)])
			elif isinstance(item, self.nodeClass):
				csvTable.add([item.__class__.__name__, item.id, self.id, *(getattr(item, name, "") for name,tp in item.properties), *(edge.id for edge in item.connections)])
			elif isinstance(item, self.edgeClass):
				csvTable.add([item.__class__.__name__, item.id, self.id, *(getattr(item, name, "") for name,tp in item.properties), *(node.id for node in item.connections)])
		
		if file is not None:
			file.write(csvTable.compile())
		
		return csvTable

	@classmethod
	def fromCSV(cls : "type[Graph]", file : _GL.TextIO|_GL.FilePath, /, *, root : str|None=None) -> "list[Graph]":

		if isinstance(file, (_GL.TextIO,_IO.TextIOWrapper)):
			file.seek(0)
			csvTable = _DataFormats.CSV()
			csvTable.parse(file.read())
		elif isinstance(file, str):
			from GeekyGadgets.DataFormats.CSV import openCSV
			csvTable = openCSV(file)
		else:
			raise TypeError(f"`file`/`filename` must be either a TextIO/str-like object, not {type(file).__name__}")
		
		if not csvTable.header:
			csvTable.header = csvTable.data[:4]
			csvTable.data = csvTable.data[4:]

		graphClassName, _, *graphHeader, _ = csvTable.header[0]
		rootClassName, _, _, *rootHeader = csvTable.header[1]
		nodeClassName, _, _, *nodeHeader, _ = csvTable.header[2]
		edgeClassName, _, _, *edgeHeader, _, _ = csvTable.header[3]
		
		graphCls = _Funcs.first((subCls for subCls in _Walkers.SubClassWalker(cls) if subCls.__name__ == graphClassName), cls)
		rootCls = _Funcs.first((subCls for subCls in _Walkers.SubClassWalker(cls) if subCls.__name__ == rootClassName), cls.rootClass)
		nodeCls = _Funcs.first((subCls for subCls in _Walkers.SubClassWalker(cls) if subCls.__name__ == nodeClassName), cls.nodeClass)
		edgeCls = _Funcs.first((subCls for subCls in _Walkers.SubClassWalker(cls) if subCls.__name__ == edgeClassName), cls.edgeClass)

		graphProperties = [tuple(string.split("|")) for string in graphHeader]
		rootProperties = [tuple(string.split("|")) for string in rootHeader]
		nodeProperties = [tuple(string.split("|")) for string in nodeHeader]
		edgeProperties = [tuple(string.split("|")) for string in edgeHeader]
		
		graphPropertyParsers, edgePropertyParsers, nodePropertyParsers = [
			[
				_Funcs.parseFloat
				if propType.lower()=="float"
				else _Funcs.parseInt
				if propType.lower().startswith("int")
				else str
				if propType.lower().startswith("str")
				else _DataFormats.parseObjects
				for propName,propType in properties
			]
			for properties in [graphProperties, edgeProperties, nodeProperties]
		]

		ret = []
		graphs = {}
		nodes : dict[int,dict[_GL.Any,Node]] = {}
		connections : dict[int,list] = {}
		for row in csvTable.data:
			if row[0] == graphClassName:
				ret.append(graph := graphCls())
				
				_, graph.id, *properties, rootName = row
				graphs[graph.id] = graph
				graph.root.id = rootName or str(root)
				nodes[graph.id] = {graph.root.id:graph.root}
				connections[graph.id] = []
				for (propName, propType), propString, parser in zip(graphProperties, properties, graphPropertyParsers):
					if propString:
						setattr(graph, propName, parser(propString))
			elif row[0] == edgeClassName:
				_, edgeID, graphID, *properties, fromID, toID  = row
				connections[graphID].append((fromID, toID, edgeID, properties))
			elif row[0] == nodeClassName:
				_, nodeID, graphID, *properties, _  = row
				nodes[graphID][nodeID] = node = nodeCls(graph=graph)
				node.id = nodeID
				for (propName, propType), propString, parser in zip(nodeProperties, properties, nodePropertyParsers):
					if propString:
						setattr(node, propName, parser(propString))
			elif row[0] == graph.root.__class__.__name__:
				_, nodeID, graphID, *properties  = row
				node = graphs[graphID].root
				node.id = nodeID
				for (propName, propType), propString, parser in zip(rootProperties, properties, nodePropertyParsers):
					if propString:
						setattr(node, propName, parser(propString))
		for graph in ret:
			for fromID, toID, edgeID, properties in connections[graph.id]:
				node, edge = nodes[graph.id][fromID].addNode(nodes[graph.id][toID], edgeID)
				for (propName, propType), propString, parser in zip(edgeProperties, properties, edgePropertyParsers):
					if propString:
						setattr(edge, propName, parser(propString))

		return ret

	@classmethod
	def fromGraphML(cls : "type[Graph]", file : _GL.TextIO|_GL.FilePath, /, *, root : str|None=None) -> "list[Graph]":

		from GeekyGadgets.Semantics.Markups.General import parseMarkup
		if isinstance(file, (_GL.TextIO,_IO.TextIOWrapper)):
			file.seek(0)
		elif isinstance(file, str):
			file = open(file, "r")
		else:
			raise TypeError(f"`file`/`filename` must be either a TextIO/str-like object, not {type(file).__name__}")
		
		document = parseMarkup(file.read(), markupType=_GRAPHML.GRAPHML)
		dataKeys = {}
		
		ret = []
		for instance in document.children:
			ret.append(graph := cls())
			
			if root is not None:
				graph.root.id = str(root)
			nodes : dict[str,Node] = {str(graph.root.id) : graph.root}
			
			for keyTag in filter(lambda x: isinstance(x, _GRAPHML.Key), instance.children):
				if keyTag.For not in dataKeys:
					dataKeys[keyTag.For] = {}
				match keyTag.attributes["attr.type"]:
					case "int":
						dataKeys[keyTag.For][keyTag.id] = _Funcs.parseInt
					case "float":
						dataKeys[keyTag.For][keyTag.id] = _Funcs.parseFloat
					case _:
						dataKeys[keyTag.For][keyTag.id] = lambda *args, **kwargs: args[0]
			
			for graphTag in filter(lambda x: isinstance(x, _GRAPHML.Graph), instance.children):
				for dataTag in filter(lambda x: isinstance(x, _GRAPHML.Data) and not _DataFormats.isNone(x.content[0]), graphTag.children):
					setattr(graph, dataTag.id, dataKeys["graph"][dataTag.id](dataTag.content[0], dataTag.content[0]))

				for nodeTag in filter(lambda x: isinstance(x, _GRAPHML.Node), graphTag.children):
					nodes[str(nodeTag.id)] = node = cls.nodeClass(str(nodeTag.id), graph=graph)
					for dataTag in filter(lambda x: isinstance(x, _GRAPHML.Data) and not _DataFormats.isNone(x.content[0]), nodeTag.children):
						setattr(node, dataTag.id, dataKeys["node"][dataTag.id](dataTag.content[0], dataTag.content[0]))
			
				for edgeTag in filter(lambda x: isinstance(x, _GRAPHML.Edge), graphTag.children):
					node, edge = nodes[str(edgeTag.source)].addNode(nodes[str(edgeTag.target)], str(edgeTag.target))
					for dataTag in filter(lambda x: isinstance(x, _GRAPHML.Data) and not _DataFormats.isNone(x.content[0]), edgeTag.children):
						setattr(edge, dataTag.id, dataKeys["edge"][dataTag.id](dataTag.content[0], dataTag.content[0]))

		return ret
	
	def illustrateHTML(self, *, file : _GL.TextIO=None, **kwargs) -> _Markups.Markup:
		from GeekyGadgets.Semantics.Markups.HTML import Figure, Div
		page = Figure(Div(self.illustrateSVG(**kwargs)))
		
		if file is not None:
			file.write(page.compile())
			file.flush()
		return page

	def illustrateSVG(self, *, file : _GL.TextIO=None, **kwargs) -> _Markups.Markup:

		import math

		WIDTH = 100
		HEIGHT = 100

		generations = []
		nextGen = [self.root]
		history = set(nextGen)
		while generation := nextGen:
			generations.append(generation)
			nextGen = []
			for node in generation:
				children = list(filter(lambda x:x not in history, node.children))
				history.update(children)
				nextGen.extend(children)
			
		generations = generations[1:]

		VISIBLE_NODES = (
			sum(1 for _ in _Iterators.TakeWhile(lambda gen: all(not n.hidden for n in gen), generations)),
			len(max(generations, key=lambda gen: sum(1 - 0*n.hidden for n in gen)))
		)

		NODE_SPACE = HEIGHT / (max(VISIBLE_NODES))

		NODE_RADIUS = NODE_SPACE * 0.4
		NODE_BORDER_WIDTH = "0.1"
		NODE_BORDER_COLOR = "black"

		EDGE_WIDTH = NODE_RADIUS * 1.25
		FONT_SIZE = NODE_SPACE
		EDGE_THIN_WIDTH = "1px"
		EMPTY_EDGE_COLOR = "gray"

		from GeekyGadgets.Semantics.Markups.SVG import Svg, Path, Circle, RadialGradient, Stop, Text, Defs, G

		page = Svg(
			id=self.id,
			height="100%",
			width="100%",
			viewBox="0 0 100 100",
			xmlns="http://www.w3.org/2000/svg",
			Class="Graph"
		)
		nodePositions = {self.root:(WIDTH*self.root.point[0], HEIGHT*self.root.point[1])}
		for genI, generation in enumerate(generations):
			nodeY = HEIGHT * (genI+1)/(len(generations)+2)
			genSize = sum(1 - 0*node.hidden for node in generation)
			
			i = 0
			for node in generation:
				nodeX = WIDTH * (i+1)/(genSize+1)
				nodePositions[node] = (nodeX, nodeY)
				i += 1 - 0*node.hidden
		
		nodeGroups = {}
		for generation in reversed([[self.root]]+generations):
			for node in generation:
				nodeGroups[node] = G(
					id=f"{node.id}Group",
					hidden=node.hidden,
					**(
						{name:getattr(node, name, None) for (name, dtype) in node.properties}
						| {
							name:getattr(node.incoming[0], name, None)
							for (name, dtype) in (node.incoming[0].properties
										 if node.incoming else
										 ())
						}
					)
				)
				for edge in node.connections:
					neighbor = edge.pair[0] if edge.pair[0] is not node else edge.pair[1]
					if neighbor in nodeGroups:
						nodeGroups[node].addChild(nodeGroups[neighbor])
		page.addChild(nodeGroups[self.root])

		for edge in map(lambda x:x.incoming[0], _Iterators.Chain(*generations)):
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
			
			if isinstance(edge.weight, _GL.Number): # Colored thick stroke
				weight = max(min(edge.weight, 1.0), 0.0)
				nodeGroups[endNode].addChild(Path(
					name=str(endNode.id), 
					d=f"M {start[0]} {start[1]} "
					f"C {startVector[0]} {startVector[1]}, "
					f"{endVector[0]} {endVector[1]}, "
					f"{end[0]} {end[1]}",
					fill="transparent",
					stroke=edge.color,
					strokeWidth=f"{EDGE_WIDTH*weight}",
					strokeOpacity=1.0
					))
			nodeGroups[endNode].addChild(Path(
				name=str(endNode.id), 
				d=f"M {start[0]} {start[1]} "
				f"C {startVector[0]} {startVector[1]}, "
				f"{endVector[0]} {endVector[1]}, "
				f"{end[0]} {end[1]}",
				fill="transparent",
				stroke=f"{EMPTY_EDGE_COLOR}",
				strokeWidth=f"{EDGE_THIN_WIDTH}",
				strokeOpacity=0.6,
				vectorEffect="non-scaling-stroke"))
		for node in nodePositions:
			if node is self.root: continue

			nodeX, nodeY = nodePositions[node]
			nodeGroups[node].addChild(
				Text(
					node.name,
					name=str(node.id),
					x=f"{nodeX+NODE_RADIUS/1.4}", y=f"{nodeY-NODE_RADIUS/1.4}",
					fontSize=FONT_SIZE, fontFamily="verdana", textAnchor="left",
				)
			)
			nodeGroups[node].addChild(
				Circle(
					name=str(node.id),
					r=NODE_RADIUS,
					cx=nodeX, cy=nodeY,
					stroke=NODE_BORDER_COLOR,
					strokeWidth=NODE_BORDER_WIDTH,
					fill=node.color,
					onclick="toggleHidden(this)"
				)
			)
		
		if file is not None:
			file.write(page.compile())
			file.flush()
		return page
			
	def illustrateGRAPHML(self, *, file : _GL.TextIO=None, **kwargs) -> _Markups.Markup:
		from GeekyGadgets.Semantics.Markups.GRAPHML import GraphML, Graph, Key, Data, Node, Edge, Default
		from GeekyGadgets.Formatting.Case import TitleCase

		page = _Markups.Document(graphml := GraphML())

		for className, cls in [("graph", type(self)), ("node", self.nodeClass), ("edge", self.edgeClass)]:
			for propName, propType in cls.properties:
				graphml.addChild(Key(Default("NaN"), id=propName, For=className, ATTRS={"attr.name" : TitleCase(propName), "attr.type" : TitleCase(propType)}))
		graphml.addChild(graph := Graph(id=self.id, edgedefault=f"{'un'*bool(not isinstance(self, Directed))}directed"))
		for propName, propType in graph.properties:
			graph.addChild(Data(getattr(self, propName, "NaN"), key=propName))
		
		for node in self.allNodes:
			graph.addChild(node := Node(id=node.id))
			for propName, propType in node.properties:
				node.addChild(Data(getattr(node, propName, "NaN"), key=propName))
		
		for edge in self.allEdges:
			graph.addChild(edge := Edge(id=edge.id, source=edge.connections[0], target=edge.connections[1]))
			for propName, propType in edge.properties:
				edge.addChild(Data(getattr(edge, propName, "NaN"), key=propName))

		if file is not None:
			file.write(graphml.compile())
			file.flush()
		return page

	def walk(self, skipSelf=True):
		if not skipSelf:
			yield self
		yield from _Walkers.GraphWalker(self.root)

class Directed(HashedByID):
	
	id : _GL.Hashable
	name : str

	incoming : "_GL.Iterable[_D]|_D"
	outgoing : "_GL.Iterable[_D]|_D"

_D = _GL.TypeVar("_D", bound=Directed)
_G = _GL.TypeVar("_G", Graph, Directed)

class Node(HashedByID, OwnedByGraph, HasPropertyDefaults, _GL.ABC):

	id : str
	name : str = _Classy.Default(lambda self: str(self.id))
	properties : list[tuple[str,str]] = [("color", "string")]
	color : str|None = None

	graph : _G
	connections : tuple
	hidden : bool = False

	color = "darkgray"

	def __init__(self, id : str=None, *, graph : _G|None=None) -> None:
		self.id = id or self.id
		self.connections = ()
		if graph is not None:
			self.graph = graph
	
	def addNode(self, node : "str|Node", edge : "str|Edge", **kwargs):
		
		if isinstance(node, str):
			node = type(self)(node, graph=(self.graph or kwargs.get("graph")), **kwargs)
		if isinstance(edge, str):
			if self.graph is None:
				self.graph = kwargs["graph"]
			edge = self.graph.edgeClass(edge, (self, node), graph=self.graph)
		self.connections = self.connections + (edge,)
		node.connections = node.connections + (edge,)
		return node, edge
	
	def walk(self) -> _GL.Generator["Node",None,None]:
		for edge in self.connections:
			yield edge

class Root:
	
	ANCHOR_POINTS = {
		"TOP LEFT" : 	(0.,0.),	"TOP" : 	(0.5,0.),	"TOP RIGHT" : 		(1.,0.),
		"LEFT" : 		(0.,0.5),	"CENTER" : 	(0.5,0.5),	"RIGHT" : 			(1.,0.5),
		"BOTTOM LEFT" : (0.,1.),	"BOTTOM" : 	(0.5,1),	"BOTTOM RIGHT" : 	(1.,1.),

		"OUTER TOP LEFT" 	: (-1.,-1.), "OUTER TOP" 	: (0.5,-1.), "OUTER TOP RIGHT"		: (2.,-1.),
		"OUTER LEFT" 		: (-1.,0.5), 							 "OUTER RIGHT"			: (2.,0.5),
		"OUTER BOTTOM LEFT" : (-1.,2.0), "OUTER BOTTOM"	: (0.5,2.0), "OUTER BOTTOM RIGHT"	: (2.,2.),
	}

	id = "root"
	name : str = _Classy.Default(lambda self: str(self.id))
	point : tuple[float,float]

	def __init__(self, *args, anchor : str="CENTER", **kwargs) -> None:
		self.point = self.ANCHOR_POINTS[anchor]
		super().__init__(*args, **kwargs)

class RootNode(Root, Node): ...

class Edge(HashedByID, OwnedByGraph, HasPropertyDefaults, _GL.ABC):
	
	id : str
	name : str = _Classy.Default(lambda self: str(self.id))
	properties : list[tuple[str,str]] = [("color", "string")]
	color : str|None = None

	graph : _G
	pair : _SPT.Pair
	connections : _GL.Iterable = property(lambda self: self.pair)
	hidden : bool = False

	color = "#ff2020"
	def __init__(self, id : str, pair : _GL.Iterable[Node,Node], *, graph : _G|None=None) -> None:
		self.id = id
		self.pair = _SPT.Pair(pair)
		if graph is not None:
			self.graph = graph
	
	def walk(self) -> _GL.Generator["Edge",None,None]:
		for node in self.pair:
			yield node

class DummyEdge:
	def __getattribute__(self, name: str) -> _GL.Any:
		return self
	def __setattribute__(self, name, value):
		return None
	def __getitem__(self, name):
		return self
	def __setitem__(self, name, value):
		return None
	def __call__(self, *args, **kwargs):
		return self

Graph.rootClass = RootNode
Graph.edgeClass = Edge
Graph.nodeClass = Node

class Branch(Edge, Directed):
	propertyNames : list[tuple[str,str]] = [("color", "string")]
	color : str = "Chocolate"

	graph : "Tree"

	incoming : "Leaf" = property(lambda self:self.pair[0], lambda self, value: setattr(self, "pair", (value, self.pair[1])), lambda self: setattr(self, "pair", (None, self.pair[1])))
	outgoing : "Leaf" = property(lambda self:self.pair[1], lambda self, value: setattr(self, "pair", (self.pair[0], value)), lambda self: setattr(self, "pair", (self.pair[0], None)))
	
	def walk(self) -> _GL.Generator["Leaf",None,None]:
		yield self.outgoing

class Leaf(Node, Directed):
	propertyNames : list[tuple[str,str]] = [("color", "string")]
	color : str|None = None

	graph : "Tree"
	incoming : tuple[Branch]
	outgoing : tuple[Branch]
	parent : "Leaf" = property(lambda self: self.incoming[0].incoming)
	parentBranch : "Leaf" = property(lambda self: self.incoming[0])
	children : list[Branch] = property(lambda self: [edge.outgoing for edge in self.outgoing])
	childBranches : list[Branch] = property(lambda self: self.outgoing)
	connections : "list[_D]|_D" = property(lambda self: tuple(_Iterators.Chain(self.incoming, self.outgoing)), lambda self, value:None)
	hidden : bool = False

	def __init__(self, id : str=None, incoming : _GL.Iterable[Branch]=(), outgoing : _GL.Iterable[Branch]=(), *, graph : _G|None=None) -> None:
		super().__init__(id, graph=graph)
		
		self.incoming = tuple(incoming)
		self.outgoing = tuple(outgoing)
		
	def walk(self) -> _GL.Generator["Branch",None,None]:
		for branch in self.outgoing:
			yield branch

	def addNode(self, node : "str|Leaf", edge : "str|Branch", **kwargs):
		if isinstance(node, str):
			node = type(self)(node, graph=(self.graph or kwargs.get("graph")), **kwargs)
		if isinstance(edge, str):
			if self.graph is None:
				self.graph = kwargs["graph"]
			edge = self.graph.edgeClass(edge, (self, node), graph=self.graph)
		self.outgoing = self.outgoing + (edge,)
		node.incoming = node.incoming + (edge,)

		return node, edge
	
	def isAncestor(self, leaf) -> bool:
		return any(ancestor == leaf for ancestor in _Walkers.LeafClimber(self))
	
	def isDescendant(self, leaf) -> bool:
		return any(descendant == leaf for descendant in _Walkers.LeafWalker(self))

class TreeRoot(Root, Leaf):
	
	parent = None

	def __init__(self, *args, anchor: str="TOP", graph: _G | None = None, **kwargs) -> None:
		super().__init__(*args, anchor=anchor, graph=graph, **kwargs)

class Tree(Graph, Directed):

	root : TreeRoot = _GL.cached_property(lambda self: TreeRoot(anchor="OUTER TOP", graph=self))
	
	rootClass : type[TreeRoot] = TreeRoot
	nodeClass : type[Leaf] = Leaf
	edgeClass : type[Branch] = Branch

	depth : int = _Classy.CachedDefault["allNodes"](lambda self: max(1+sum(1 for _ in _Walkers.LeafWalker(leaf, key=lambda n: iter(n.incoming[0].incoming), recurseCond=lambda n: n.incoming[0].incoming)) for leaf in self.endNodes)) # max(sum(1 for _ in _Iterators.TakeWhile(lambda n: n.outgoing, iterator)) for iterator in [_Walkers.LeafWalker(self.root, key=lambda x:x.connections)]))
	endNodes : "set[Node]" = property(lambda self: filter(lambda n:not n.children, self.allNodes))

	def illustrateHTML(self, *, file : _GL.TextIO=None, **kwargs) -> _Markups.Markup:
		page = _HTML.Figure(_HTML.Div(svg := self.illustrateSVG(**kwargs)))
		classes = set(svg.Class.split())
		classes.add("Tree")
		svg.Class = " ".join(classes)
		if file is not None:
			file.write(page.compile())
			file.flush()
		return page
	
	def walk(self, skipSelf=True):
		if not skipSelf:
			yield self
		yield from _Walkers.TreeWalker(self.root)
