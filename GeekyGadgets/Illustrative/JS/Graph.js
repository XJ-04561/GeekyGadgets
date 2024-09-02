
var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion)")

function toggleHidden(element) {
	let group = element.parentElement;
	if (group.getAttribute("hidden") == "true") {
		console.log("Showing "+ group);
		showGroups(group)
	} else {
		console.log("Hiding "+ group);
		hideGroups(group)
	}
}

function hideGroups(group) {
	group.setAttribute("hidden", "true");
	Array.from(group.children).forEach((childGroup) => {
		if (group.TagName != childGroup.TagName) return;
		
		hideGroups(childGroup);
	})
}

function showGroups(group) {
	group.setAttribute("hidden", "false");
	Array.from(group.children).forEach((childGroup) => {
		if (group.TagName != childGroup.TagName) return;

		showGroups(childGroup);
	})
}
