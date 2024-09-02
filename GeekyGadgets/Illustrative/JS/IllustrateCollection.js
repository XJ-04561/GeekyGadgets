
var scalePat = /scale[(](\d*(?:[.]\d*)?)[)]/
var translatePat = /translate[(]([-]?\d*(?:[.]\d*)?)%, ([-]?\d*(?:[.]\d*)?)%[)]/

function expandGraph(graphContainer) {
	let parent = graphContainer.parentElement;
	let n = 0;
	while (!parent.classList.contains("CollectionViewer") && n++ < 100) {
		parent = parent.parentElement;
	}
	viewer = parent;
	container = viewer.getElementsByClassName("SvgContainer")[0].getElementsByTagName("figure")[0].parentElement
	container.innerHTML = "";
	container.appendChild(graphContainer.children[0].cloneNode(true))
	container.style.transform = "";
	
	let previousShown = viewer.getElementsByTagName("nav")[0].getElementsByClassName("showing");
	for (let i=0; i<previousShown.length; i++) {
		previousShown[i].classList.remove("showing");
	}
	graphContainer.classList.add("showing")
}

function zoomGraph(event) {
	
	const bRect = this.getBoundingClientRect()
	let svgBox = this.children[0].children[0].children[0]

	x = event.clientX - bRect.x
	y = event.clientY - bRect.y
	if (!((0 < x && x <= bRect.width) && (0 < y && y <= bRect.height))) {
		return;
	} else {
		event.preventDefault()
	}

	let scale = parseFloat((scalePat.exec(svgBox.style.transform) ?? [null, "1.0"])[1]);
	let translate = translatePat.exec(svgBox.style.transform) ?? [null, "0", "0"]
	tX = parseFloat(translate[1]) / 100;
	tY = parseFloat(translate[2]) / 100;

	let previousScale = scale
	scale += 2*event.deltaY / 1000
	if (scale < 1.0) {scale = 1.0}

	tX -= (scale/previousScale-1.0) * (x/bRect.width-0.5-tX)
	tY -= (scale/previousScale-1.0) * (y/bRect.height-0.5-tY)
	
	svgBox.style.transform = `translate(${100*tX}%, ${100*tY}%) scale(${scale})`;
}

function resetZoomGraph(event) {
	
	const bRect = this.getBoundingClientRect()
	let svgBox = this.children[0].children[0].children[0]

	x = event.clientX - bRect.x
	y = event.clientY - bRect.y
	if (!((0 < x && x <= bRect.width) && (0 < y && y <= bRect.height))) {
		return;
	} else {
		event.preventDefault()
	}

	svgBox.style.transform = "";
}

document.addEventListener("DOMContentLoaded", function(event) {
	for (let i=0; i < document.getElementsByClassName("SvgContainer").length; i++) {
		let container = document.getElementsByClassName("SvgContainer").item(i)
		container.addEventListener("wheel", zoomGraph)
		container.addEventListener("contextmenu", resetZoomGraph)
	}
})
