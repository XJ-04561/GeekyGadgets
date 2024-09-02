
import random, pytest, os
from GeekyGadgets.Illustrative import IllustrateFigure
import math

N = 10
DATA = [(x, 40*math.cos(x*math.pi/20)+50+random.random()*10) for i in range(N) for x in range(20)]

def test_line_clone():
	from GeekyGadgets.Illustrative.Plots import LinePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "clone"
	plot = LinePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_line_clone.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_line_widen():
	from GeekyGadgets.Illustrative.Plots import LinePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "widen"
	plot = LinePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_line_widen.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_line_shadow():
	from GeekyGadgets.Illustrative.Plots import LinePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "shadow"
	plot = LinePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_line_shadow.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_line_whiskers():
	from GeekyGadgets.Illustrative.Plots import LinePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "whiskers"
	plot = LinePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_line_whiskers.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_line_boxplot():
	from GeekyGadgets.Illustrative.Plots import LinePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "boxplot"
	plot = LinePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_line_boxplot.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_scatter_clone():
	from GeekyGadgets.Illustrative.Plots import ScatterPlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "clone"
	plot = ScatterPlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_scatter_clone.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_scatter_widen():
	from GeekyGadgets.Illustrative.Plots import ScatterPlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "widen"
	plot = ScatterPlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_scatter_widen.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_scatter_shadow():
	from GeekyGadgets.Illustrative.Plots import ScatterPlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "shadow"
	plot = ScatterPlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_scatter_shadow.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_scatter_whiskers():
	from GeekyGadgets.Illustrative.Plots import ScatterPlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "whiskers"
	plot = ScatterPlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_scatter_whiskers.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_scatter_boxplot():
	from GeekyGadgets.Illustrative.Plots import ScatterPlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "boxplot"
	plot = ScatterPlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_scatter_boxplot.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_curve_clone():
	from GeekyGadgets.Illustrative.Plots import CurvePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "clone"
	plot = CurvePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_curve_clone.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_curve_widen():
	from GeekyGadgets.Illustrative.Plots import CurvePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "widen"
	plot = CurvePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_curve_widen.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_curve_shadow():
	from GeekyGadgets.Illustrative.Plots import CurvePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "shadow"
	plot = CurvePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_curve_shadow.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_curve_whiskers():
	from GeekyGadgets.Illustrative.Plots import CurvePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "whiskers"
	plot = CurvePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_curve_whiskers.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

def test_curve_boxplot():
	from GeekyGadgets.Illustrative.Plots import CurvePlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	errorStyle = "boxplot"
	plot = CurvePlot(DATA)
	plot.setErrorStyle(errorStyle)
	with open("test_curve_boxplot.html", "w") as f:
		f.write(IllustrateFigure(plot).illustrateHTML().compile())

@pytest.mark.skip
def test_heat_clone():
	from GeekyGadgets.Illustrative.Plots import HeatPlot
	errorStyle = "clone"
@pytest.mark.skip
def test_heat_widen():
	from GeekyGadgets.Illustrative.Plots import HeatPlot
	errorStyle = "widen"
@pytest.mark.skip
def test_heat_shadow():
	from GeekyGadgets.Illustrative.Plots import HeatPlot
	errorStyle = "shadow"
@pytest.mark.skip
def test_heat_whiskers():
	from GeekyGadgets.Illustrative.Plots import HeatPlot
	errorStyle = "whiskers"
@pytest.mark.skip
def test_heat_boxplot():
	from GeekyGadgets.Illustrative.Plots import HeatPlot
	errorStyle = "boxplot"

def test_plots_all():
	
	from GeekyGadgets.Illustrative.Plots import LinePlot, CurvePlot, ScatterPlot
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	from GeekyGadgets.Illustrative.Envelopes import IllustrativeCollection
	
	for plotType in [LinePlot, CurvePlot, ScatterPlot]:
		with open(f"{plotType.__name__}All.html", "w") as f:
			IllustrativeCollection(
				[
					plotType(DATA, errorStyle=errorStyle)
					for errorStyle in ["clone", "widen", "shadow", "whiskers", "boxplot"]
				]
			).illustrateHTML(file=f)