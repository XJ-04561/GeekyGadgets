
from GeekyGadgets.Illustrative import *
from GeekyGadgets.TypeHinting import Number
from GeekyGadgets.Illustrative.NodesAndGraphs import XML_TAG_PATTERN, XML_ATTRIBUTES_PATTERN

import sys, os
from subprocess import Popen

EXE = sys.executable

def test_from_graph_ml():
	
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	assert XML_TAG_PATTERN.match("<node id=\"1\">\n"
    "  <data id=\"genotype\">T/N.1</data>\n"
    "</node>\n"
    "<node id=\"2\">\n"
    "  <data id=\"genotype\">T.1</data>\n"
    "</node>\n"
    "<node id=\"3\">\n"
    "  <data id=\"genotype\">B.1</data>\n"
    "</node>")
	assert XML_ATTRIBUTES_PATTERN.match(' id="nonCanon" for="edge" attr.name="Non-Canonical Bases" attr.type="int"')

	Graph.fromGraphML(open("tree.graphml", "r"))

	assert True

def test_tree():
	
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	class CanSNPLeaf(Leaf):
		"""Properties:
		genotype : str"""

		@property
		def color(self) -> str:
			
			if not self.incoming[0].properties["depth"] or not isinstance(self.incoming[0].properties["depth"], Number):
				return "#303030"
			elif 0.05 < self.incoming[0].properties["nonCanon"] / self.incoming[0].properties["depth"]:
				return "#ff30ff"
			calledSNPs = []
			ratios = []
			node = self
			while node.incoming:
				ratios.append(node.incoming[0].properties["ratio"])
				calledSNPs.append(node.incoming[0].properties["called"])
				node = node.incoming[0].pair[0]
			
			if any(prevCalled > 1 and 1.1 < thisNode/prevNode for thisNode, prevNode, prevCalled in zip(ratios, ratios[1:], calledSNPs[1:])):
				return "#ff30ff"
			
			return "#20ff20"

	class CanSNPBranch(Branch):
		"""Properties:
		called : int
		ancestral : int
		nonCanon : int
		depth : int
		ratio : float
		logRatio : float"""

		weight = property(lambda self: self.properties["ratio"])
	
	class CanSNPTree(Tree):
		nodeClass = CanSNPLeaf
		edgeClass = CanSNPBranch

		weightProp : str = ""

	tree = CanSNPTree.fromGraphML(open("tree.graphml", "r"))

	tree.illustrate("HTML", filename="tree.html", nameProp="genotype")
	
	assert True