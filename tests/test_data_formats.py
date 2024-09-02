

from GeekyGadgets.DataFormats import CSV, PNG, TSV
import os, re, pytest

@pytest.mark.skip
def test_png():
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])


def test_csv():
	from MetaCanSNPer.modules.Plotting import CanSNPTree
	
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	[tree1] = CanSNPTree.fromGraphML(os.path.join("..", "test_illustrative", "tree_4.graphml"))

	csvTable = CSV()

	tree1.illustrateCSV(csv=csvTable)

	csvTable.save("tree_4.csv")

	assert open("tree_4.csv", "r").readline()

	[tree2] = CanSNPTree.fromCSV("tree_4.csv")

	assert tree1.id == tree2.id
	assert tree1.root.id == tree2.root.id
	assert tree1.root == tree2.root
	assert tree1 == tree2