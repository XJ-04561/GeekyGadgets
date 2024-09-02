
var rootElement = document.querySelector(':root');

function changePageBackground(color) {
	rootElement.style.setProperty('--PAGE-BACKGROUND', color);
}