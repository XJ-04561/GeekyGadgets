

from GeekyGadgets.Globals import *
import GeekyGadgets.Semantics.Markups as _Markups
import GeekyGadgets.Semantics.Markdown.Globals as _Markdown

class Illustrator(ABC):

	def illustrateHTML(self, *, file : TextIO=None, **kwargs) -> _Markups.Markup: raise NotImplementedError()
	def illustratePDF(self, *, file : TextIO=None, **kwargs) -> "_DF.BinaryDataStructure": raise NotImplementedError()
	def illustrateSVG(self, *, file : TextIO=None, **kwargs) -> _Markups.Markup: raise NotImplementedError()
	def illustrateMARKDOWN(self, *, file : TextIO=None, **kwargs) -> _Markdown.Markdown: raise NotImplementedError()
	def illustratePNG(self, *, file : BinaryIO=None, size : tuple[int,int]=(1080,1080), dark : bool=False, **kwargs) -> "_DF.BinaryDataStructure":
		from GeekyGadgets.DataFormats.PNG import PNG
		import GeekyGadgets.Semantics.Markups.HTML as _HTML
		try:
			from html2image import Html2Image as _Html2Image
		except ModuleNotFoundError as e:
			if hasattr(e, "add_note"):
				e.add_note("`html2image` is required to create a .png screenshot of the Illustration.")
			raise e
		tempFilePath = UniqueFilePath("./screenshot.png")
		
		Html2Image = _Html2Image(output_path=tempFilePath.directory, disable_logging=True, custom_flags=["--force-dark-mode"]*bool(dark))
		
		page = self.illustrateHTML(**kwargs)
		page.children[0].addChild(_HTML.Style(open(os.path.join(os.path.split(__file__)[0], "CSS", "PNG.css"), "r").read()))

		Html2Image.screenshot(html_str=page.compile(), size=size, save_as=tempFilePath.file)
		
		with open(tempFilePath, "rb") as f:
			obj = PNG.parse(f.read())
		os.remove(tempFilePath)

		if file is not None:
			file.write(obj.compile())
			file.flush()

		return obj


	def illustrateGRAPHML(self, *, file : TextIO=None, **kwargs) -> _Markups.Markup: raise NotImplementedError()

	def illustrate(self, outputFormat : Literal["HTML","PDF","SVG","PNG","GRAPHML"], *args, file : TextIO=None, **kwargs) -> _Markups.Markup:
		match outputFormat:
			case "HTML":
				return self.illustrateHTML(*args, file=file, **kwargs)
			case "PDF":
				return self.illustratePDF(*args, file=file, **kwargs)
			case "SVG":
				return self.illustrateSVG(*args, file=file, **kwargs)
			case "PNG":
				return self.illustratePNG(*args, file=file, **kwargs)
			case "GRAPHML":
				return self.illustrateGRAPHML(*args, file=file, **kwargs)
			case _:
				raise ValueError(f"{outputFormat=} is not a recognized output format name. Recognized names: `HTML`, `PDF` ,`SVG` ,`PNG` ,`GRAPHML`")

BASE_CSS=open(os.path.join(os.path.split(__file__)[0], "CSS", "BASE.css"), "r").read()

try:
	import GeekyGadgets.DataFormats as _DF
except ImportError:
	pass