
from GeekyGadgets.Semantics import *
from GeekyGadgets.Semantics.Markups.General import parseMarkup, parseInline
from GeekyGadgets.Logging import logTo, setLevel, ROOT_LOGGER
import os, re, pytest
from timeit import default_timer as timer

setLevel()

ROW_PAT = re.compile(r".{80}")
SPACE_PAT = re.compile(r"\s+")

@pytest.mark.skip
def test_html():
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	LOGGER = ROOT_LOGGER.getChild(__name__+".HTML")

	from GeekyGadgets.Semantics.Markups.HTML import HTML

	startTime = timer()
	origHTML = open("sample.html", "r").read()
	LOGGER.info(f"Finished reading HTML text [{timer()-startTime}]")

	startTime = timer()
	naiveMarkup = parseMarkup(origHTML)
	LOGGER.info(f"Finished naive parsing of HTML [{timer()-startTime}]")

	startTime = timer()
	hintedMarkup = parseMarkup(origHTML, markupType=HTML)
	LOGGER.info(f"Finished hinted parsing of HTML [{timer()-startTime}]")

	startTime = timer()
	naiveHTML = str(naiveMarkup)
	LOGGER.info(f"Finished compiling HTML to text [{timer()-startTime}]")

	startTime = timer()
	hintedHTML = str(hintedMarkup)
	LOGGER.info(f"Finished compiling hinted HTML to text [{timer()-startTime}]")

	startTime = timer()
	assert naiveHTML == hintedHTML
	LOGGER.info(f"Finished comparing naive & hinted texts [{timer()-startTime}]")
	
	startTime = timer()
	with open("sample.out.html", "w") as f:
		f.write(str(naiveHTML))
	LOGGER.info(f"Finished saving naive text to file [{timer()-startTime}]")

	startTime = timer()
	for row1, row2 in zip(*map(lambda x: ROW_PAT.finditer(SPACE_PAT.sub("", x)), [naiveHTML, origHTML])):
		assert row1.group().strip() == row2.group().strip()
	LOGGER.info(f"Finished comparing naive & original texts [{timer()-startTime}]")

@pytest.mark.skip
def test_graph_ml():
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	LOGGER = ROOT_LOGGER.getChild(__name__+".GRAPHML")

	from GeekyGadgets.Semantics.Markups.GRAPHML import GRAPHML

	startTime = timer()
	origGRAPHML = open("sample.graphml", "r").read()
	LOGGER.info(f"Finished reading GRAPHML text [{timer()-startTime}]")

	startTime = timer()
	naiveMarkup = parseMarkup(origGRAPHML)
	LOGGER.info(f"Finished naive parsing of GRAPHML [{timer()-startTime}]")

	startTime = timer()
	hintedMarkup = parseMarkup(origGRAPHML, markupType=GRAPHML)
	LOGGER.info(f"Finished hinted parsing of GRAPHML [{timer()-startTime}]")

	startTime = timer()
	naiveGRAPHML = str(naiveMarkup)
	LOGGER.info(f"Finished compiling naive GRAPHML to text [{timer()-startTime}]")

	startTime = timer()
	hintedGRAPHML = str(hintedMarkup)
	LOGGER.info(f"Finished compiling hinted GRAPHML to text [{timer()-startTime}]")

	startTime = timer()
	assert naiveGRAPHML == hintedGRAPHML
	LOGGER.info(f"Finished comparing naive & hinted texts [{timer()-startTime}]")

	startTime = timer()
	with open("sample.out.graphml", "w") as f:
		f.write(str(naiveGRAPHML))
	LOGGER.info(f"Finished saving naive text to file [{timer()-startTime}]")

	startTime = timer()
	for row1, row2 in zip(*map(lambda x: ROW_PAT.finditer(SPACE_PAT.sub("", x)), [naiveGRAPHML, origGRAPHML])):
		assert row1.group().strip() == row2.group().strip()
	LOGGER.info(f"Finished comparing naive & original texts [{timer()-startTime}]")

@pytest.mark.skip
def test_svg():
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	LOGGER = ROOT_LOGGER.getChild(__name__+".SVG")

	from GeekyGadgets.Semantics.Markups.SVG import SVG

	startTime = timer()
	origSVG = open("sample.svg", "r").read()
	LOGGER.info(f"Finished reading SVG text [{timer()-startTime}]")

	startTime = timer()
	naiveMarkup = parseMarkup(origSVG)
	LOGGER.info(f"Finished naive parsing of SVG [{timer()-startTime}]")

	startTime = timer()
	hintedMarkup = parseMarkup(origSVG, markupType=SVG)
	LOGGER.info(f"Finished hinted parsing of SVG [{timer()-startTime}]")

	startTime = timer()
	naiveSVG = str(naiveMarkup)
	LOGGER.info(f"Finished compiling SVG to text [{timer()-startTime}]")

	startTime = timer()
	hintedSVG = str(hintedMarkup)
	LOGGER.info(f"Finished compiling hinted SVG to text [{timer()-startTime}]")

	startTime = timer()
	assert naiveSVG == hintedSVG
	LOGGER.info(f"Finished comparing naive & hinted texts [{timer()-startTime}]")
	
	startTime = timer()
	with open("sample.out.svg", "w") as f:
		f.write(str(naiveSVG))
	LOGGER.info(f"Finished saving naive text to file [{timer()-startTime}]")

	startTime = timer()
	for row1, row2 in zip(*map(lambda x: ROW_PAT.finditer(SPACE_PAT.sub("", x)), [naiveSVG, origSVG])):
		assert row1.group().strip() == row2.group().strip()
	LOGGER.info(f"Finished comparing naive & original texts [{timer()-startTime}]")

def test_magic_text():
	from GeekyGadgets.Semantics.Markups.SVG.Magic import Text, _SVG
	import GeekyGadgets.Semantics.Markups.HTML as _HTML

	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	string="""ThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThisThis is a very long text whith a specific purpose. That is, to be printed onto an `.svg` file, contained within a `Text` object. But, it is too long to fit in the viewBox, unless it is somehow wrapped. Therefore, a separate `Text` object is created, where this text is separated `Tspan` objects with no text longer than the `length` parameter."""
	
	ind = 2
	width = 80

	html = _HTML.Html(
		_HTML.Head(
			_HTML.Style("svg {font-size : 0.5mm;}", type="text/css")
		),
		_HTML.Body(
			_SVG.Svg(
				_SVG.Text(string, x=f"{ind}mm", y=f"{ind}mm", fontSize="1em"),
				Text(string, x=f"{ind}mm", y=f"{ind*2}mm", fontSize="1em", rowLength=width),
				width=f"{ind+width*2+ind}mm",
				height=f"{ind+width*2+ind}mm",
				viewBox="0 0 100 100"
			)
		)
	)

	open("wrappedText.html", "w").write(html.compile())
