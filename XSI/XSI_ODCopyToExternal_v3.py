import time
start_time = time.time()
from win32com.client import Dispatch, constants as c
import tempfile, os, random, sys, re
xsi=Application

def TestSelection():
	if (xsi.Selection.Count == 0):
		return "Please select an object"
	elif (xsi.Selection.Count > 1):
		return "Please select just one object"
	else:
		return ""	

def ProcessGeometry():
	oSel=Application.Selection
	selOk = TestSelection()
	if not selOk == "":
		XSIUIToolkit.MsgBox(selOk)
		return		
	filePath = os.path.dirname(os.path.normpath(tempfile.gettempdir())) + os.sep + "ODVertexData.txt"
	
	oMesh=oSel(0).ActivePrimitive.geometry	
	f = open(filePath, "w")	

	oArray=oMesh.Points.PositionArray
	
	f.write("VERTICES:"+str(len(oArray[0])) + "\n")
	
	for p in range(len(oArray[0])):
		pString=str(oArray[0][p]) + " " + str(oArray[1][p]) + " " + str(oArray[2][p])
		f.write(pString + "\n")
		
	print("---Total processing points took %s seconds ---" % (time.time() - start_time))	
	
	oPolys=oMesh.Polygons	
	f.write("POLYGONS:"+str(oPolys.count) + "\n")
	count = 0
	surfaces = []	
	clusters={}
	for oCluster in oMesh.Clusters:
		
		if oCluster.Type=="poly":			
			for oElement in oCluster.Elements:
				if str(oCluster.Name) not in clusters.keys():
					clusters[str(oCluster.Name)]=[]
					clusters[str(oCluster.Name)].append(oElement)
				else:
					clusters[str(oCluster.Name)].append(oElement)

	oPolys=oMesh.Polygons
	for oPoly in oPolys:
		oPoint=[]

		for oVertice in oPoly.Vertices:
			oPoint.append(str(oVertice.Index))

		surf = "Default"
		for key in clusters:
			if oPoly.Index in clusters[key]:
				surf=key

		polytype = "FACE"
		oPoint = ",".join(oPoint)

		f.write(oPoint + ";;" + surf + ";;" + polytype + "\n")
	print("---Total processing polys took %s seconds ---" % (time.time() - start_time))
	
	for oCluster in oMesh.Clusters:
		if oCluster.Type=="pnt":
			for prop in oCluster.Properties:
				
				if prop.Type=="wtmap":
					f.write("WEIGHT:" + prop.Name + "\n")
					for p in prop.Elements.Array[0]:
						f.write(str(p)+ "\n")
				elif prop.IsClassOf(c.siShapeKeyID ) and prop.Name!= "ResultClusterKey":
					f.write("MORPH:" + prop.Name + "\n")
					oArray=prop.Elements.Array
					for p in range(len(oArray[0])):
						pString=str(oArray[0][p]) + " " + str(oArray[1][p]) + " " + str(oArray[2][p])
						f.write(pString + "\n")
			
ProcessGeometry()
print("---Total processing took %s seconds ---" % (time.time() - start_time))
	
	
