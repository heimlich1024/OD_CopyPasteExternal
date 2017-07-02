var comPath = moi.filesystem.getCommandsDir();
var obj = comPath + "1.obj";
//Export
moi.geometryDatabase.fileExport( obj, 'NoUI=true' ); //also try: Output=ngons | quads | triangles
//use external app to convert to vertdata
moi.filesystem.shellExecute( comPath + "objToVertData.exe");
