
from GeekyGadgets.SpecialTypes import NameSpace

Tree = NameSpace(
	ILLUSTRATE=NameSpace(
		HTML=NameSpace(
			CSS=
""":root {
	--BORDER-WIDTH-THIN : min(0.25vh, 0.25vw);
	--BORDER-WIDTH-MID : min(0.5vh, 0.5vw);
	--BORDER-WIDTH-THICK : min(1vh, 1vw);

	--BORDER-RADIUS-THIN : min(1vh, 1vw);
	--BORDER-RADIUS-MID : min(2.5vh, 2.5vw);
	--BORDER-RADIUS-THICK : min(5vh, 5vw);
	--PADDING-THIN : min(1vh, 1vw);
	--PADDING-MID : min(2.5vh, 2.5vw);
	--PADDING-THICK : min(5vh, 5vw);

	--DARK-PAGE-BACKGROUND : #1a1a1a;

	--DARK-PRIMARY-COLOR : #efefef;
	--DARK-PRIMARY-BACKGROUND : #202020;
	--DARK-PRIMARY-BORDER : #505050;

	--DARK-SECONDARY-COLOR : #f9f9f9;
	--DARK-SECONDARY-BACKGROUND : #303030;
	--DARK-SECONDARY-BORDER : #404040;

	--DARK-TERTIARY-COLOR : #101010;
	--DARK-TERTIARY-BACKGROUND : #505050;
	--DARK-TERTIARY-BORDER : #404040;
}

@media (prefers-color-scheme: dark) {
	.primary {
		color : var(--DARK-PRIMARY-COLOR);
		fill : var(--DARK-PRIMARY-COLOR);
		background-color : var(--DARK-PRIMARY-BACKGROUND);
		border-color : var(--DARK-PRIMARY-BORDER);
	}
	text.primary {
		fill : var(--DARK-PRIMARY-COLOR);
	}
	circle.primary {
		fill : var(--DARK-PRIMARY-BACKGROUND);
	}
	.secondary {
		color : var(--DARK-SECONDARY-COLOR);
		fill : var(--DARK-SECONDARY-COLOR);
		background-color : var(--DARK-SECONDARY-BACKGROUND);
		border-color : var(--DARK-SECONDARY-BORDER);
	}
	circle.secondary {
		fill : var(--DARK-SECONDARY-BACKGROUND);
	}
	text.secondary {
		fill : var(--DARK-SECONDARY-COLOR);
	}
	.tertiary {
		color : var(--DARK-TERTIARY-COLOR);
		background-color : var(--DARK-TERTIARY-BACKGROUND);
		border-color : var(--DARK-TERTIARY-BORDER);
	}
	circle.tertiary {
		fill : var(--DARK-TERTIARY-BACKGROUND);
	}
	text.tertiary {
		fill : var(--DARK-TERTIARY-COLOR);
	}
}
.primary:not(.primary .primary){
	border-radius: var(--BORDER-RADIUS-THICK);
	box-shadow: var(--DARK-PRIMARY-BACKGROUND) 0 0 var(--BORDER-WIDTH-THICK) var(--BORDER-WIDTH-THICK);
}
.primary > .secondary{
	box-shadow: inset var(--DARK-PRIMARY-BACKGROUND) 0 0 var(--BORDER-WIDTH-MID) var(--BORDER-WIDTH-MID);
	border-style: solid;
}
.primary > .tertiary{
	box-shadow: inset var(--DARK-SECONDARY-BACKGROUND) 0 0 var(--BORDER-WIDTH-MID) var(--BORDER-WIDTH-MID);
	border-style: solid;
}
.secondary, .tertiary {
	border-width: var(--BORDER-WIDTH-THIN);
	border-radius: var(--BORDER-RADIUS-MID);
}
body {
	padding: 3vh 3vw;
	height: 94vh;
	width: 94vw;
	margin : 0;
	border : none;
	border-radius : none;
	background-color: var(--DARK-PAGE-BACKGROUND);
	
	box-shadow : none;
	display : flex;
	flex-wrap: wrap;
	justify-content : center;
	font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
}
figure.TreeGraph {
	margin: 0;
	padding : 0;
	/* aspect-ratio : 1 / 1; */
	flex-grow: 1;
	display : flex;
	justify-content : center;
	flex-direction: row;
	max-width : 100%;
	max-height : 100%;
}
figure.TreeGraph > * {
	margin-top : 2%;
	margin-bottom : 2%;
	max-height : 96%;
}
figure.TreeGraph > svg {
	flex-grow: 3;
}
figure.TreeGraph > menu {
	flex-grow : 1;

}
"""
)))