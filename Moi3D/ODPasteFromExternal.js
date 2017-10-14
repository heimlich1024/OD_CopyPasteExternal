var vertices=[], faces=[], max={ x:-100000, y:-100000, z:-100000 }, min={ x:100000, y:100000, z:100000 }, objName, errors=0, scale, normalize, faceobj = moi.geometryDatabase.createObjectList();
function cleanSpaces(str) { return str.replace(/^\s+|\s+$/g, '').replace(/ +(?= )/g,'')};
function loadObj( objPath )
{
	var objFile = moi.filesystem.openFileStream( objPath, 'r' ), x, y, z;
	while ( !objFile.AtEOF )
	{
		var nextLine = cleanSpaces(objFile.readLine()).split(' ');
		if ( nextLine[0] === "v" )
		{
			x = nextLine[1]*1;			y = -nextLine[3]*1;			z = nextLine[2]*1;
			if (x<min.x) { min.x=x; }	if (y<min.y) { min.y=y; }	if (z<min.z) { min.z=z; }
			if (x>max.x){ max.x=x; }	if (y>max.y){ max.y=y; }	if (z>max.z) { max.z=z; }
			vertices.push({x:x, y:y, z:z});
		}
		if (  nextLine[0] === "f" ) faces.push(nextLine);
	}
	objFile.close();
	objName = moi.filesystem.getFileNameFromPath(objPath);
	objName = objName.substr(0, objName.lastIndexOf('.'));
}

function normalizeObj (norm)
{
	normalize = norm;
	scale = 200/(max.x-min.x+max.y-min.y+max.z-min.z)/3
	var scalelog = Math.pow(10, Math.round(Math.log(scale)/Math.log(10)));
	if (scalelog>1) { scalelog /=10 }
	scale = Math.round(scale/scalelog)*scalelog;
	if (scale == 0) scale = scalelog;
	if ( !normalize && scale<1 ) scale=1;
	scale *=100;
	if ( !normalize ) for ( v in vertices ) vertices[v] = moi.VectorMath.createPoint(vertices[v].x*scale, vertices[v].y*scale, vertices[v].z*scale);
	if ( normalize ) for ( v in vertices ) vertices[v] = moi.VectorMath.createPoint((vertices[v].x-max.x/2-min.x/2)*scale, (vertices[v].y-max.y/2-min.y/2)*scale, (vertices[v].z-min.z)*scale);
	scale /=100;
}

function processObj(startPos, endPos)
{
	var lineF = moi.command.createFactory( 'line' ), lineV;
	var loftF = moi.command.createFactory( 'loft' ), loftV;
	var planarF = moi.command.createFactory( 'planarsrf' ), planarV;
	for ( var f=startPos; f<endPos; f++ )
	{
		var face = [], edges = moi.geometryDatabase.createObjectList();
		for (var i=1; i < faces[f].length; i++) face.push(faces[f][i].split("/",1)-1);
		var flen = face.length;
		if ( flen > 4 )
		{
			for (var i=0; i < flen; i++)
			{
				lineF.setInput( 0, vertices[face[i]]);
				lineF.setInput( 1, vertices[face[(i+1)%flen]]);
				lineV=lineF.calculate();
				edges.addObject(lineV.item(0));
			}
			planarF.setInput( 0, edges );
			planarV=planarF.calculate();
			if ( planarV.length > 0 ) { faceobj.addObject(planarV.item(0)) } else { errors++ }
		}
		else if ( flen ==3 || flen == 4 )
		{
			var sPt = 0, maxLength = 0, cLength=0, nPt;
			for (var i = 0; i<flen; i++)
			{
				nPt=(i+1)%flen;
				cLength = Math.sqrt((vertices[face[nPt]].x-vertices[face[i]].x)*(vertices[face[nPt]].x-vertices[face[i]].x)+(vertices[face[nPt]].y-vertices[face[i]].y)*(vertices[face[nPt]].y-vertices[face[i]].y)+(vertices[face[nPt]].z-vertices[face[i]].z)*(vertices[face[nPt]].z-vertices[face[i]].z));
				if ( cLength > maxLength ) { maxLength = cLength; sPt = i; }
			}
			lineF.setInput( 0, vertices[face[sPt]]); 			lineF.setInput( 1, vertices[face[(sPt+1)%flen]]);	lineV=lineF.calculate();	edges.addObject(lineV.item(0));
			lineF.setInput( 0, vertices[face[(sPt+3)%flen]]);	lineF.setInput( 1, vertices[face[(sPt+2)%flen]]);	lineV=lineF.calculate();	edges.addObject(lineV.item(0));
			loftF.setInput( 0, edges);
			loftV = loftF.calculate();
			if (loftV.length>0) { faceobj.addObject(loftV.item(0)) } else { errors++ }
		} else { errors++ }
	}
}

function showObj()
{
	var scale3d = moi.command.createFactory( 'scale' );
	scale3d.setInput( 0, faceobj );
	scale3d.setInput( 1, moi.VectorMath.createPoint(0,0,0) );
	scale3d.setInput( 2, (normalize)?1/100:0.01/scale );
	faceobj=scale3d.calculate();

	moi.geometryDatabase.addObjects(faceobj);
	if ( normalize ) if (scale > 1) { objName = objName + " ["+scale+":1]" } else if (scale < 1) { objName = objName + " [1:"+Math.round(100/scale)/100+"]" }
	if (errors>0) objName = objName + " err:"+errors;
	faceobj.setProperty( 'name', objName);
}
function joinObj(joinmax)
{
	if (faceobj.length>joinmax) return;
	var joinF=moi.command.createFactory( 'join' );
	joinF.setInput(0, faceobj);
	joinF.commit();
}

var comPath = moi.filesystem.getCommandsDir();
var obj = comPath + "1.obj";
//Export
moi.filesystem.shellExecute( comPath + "vertDataToObj.exe");
moi.ui.commandUI.progressinfo.innerHTML="Loading";
loadObj( obj );
moi.ui.commandUI.progressinfo.innerHTML="Normalizing";
var facesnum = faces.length;
if ( moi.command.getCommandLineParams() ==='exact' ) { normalizeObj( false ) } else { normalizeObj( true ) }
var cstart = 0, cend=0, cstep = 2000;
do {	cend = (cend+cstep>facesnum)?facesnum:cend+cstep;
	moi.ui.commandUI.progressinfo.innerHTML="Processing ("+cstart+"/"+facesnum+")<br/>Press ESC to abort";
	processObj(cstart, cend);
	cstart +=cstep;
} while (cend<facesnum);

if ( moi.command.getCommandLineParams() ==='exact' ) { normalizeObj( false ) } else { normalizeObj( true ) }
moi.ui.commandUI.progressinfo.innerHTML="Resizing";
showObj();
moi.ui.commandUI.progressinfo.innerHTML="Joining<br/>Press ESC to skip";
joinObj(20000);
moi.ui.commandUI.progressinfo.innerHTML="";