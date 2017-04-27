hou.node('obj/').createNode("geo", "geoIn", run_init_scripts = False)
hou.node('obj/geoIn/').createNode("python", "ImportScript" )
hou.node('obj/geoIn/ImportScript/').setParms({"python": '''
import tempfile, os, random, sys
def openMaster(filepath):    #Opens a file and puts every line of the file in a list and returns the list.
    masterOpen=open(filepath, "r")
    lines = [i for i in masterOpen.readlines()]
    masterOpen.close()
    return lines
filePath = tempfile.gettempdir() + os.sep + "ODVertexData.txt" #this is the temp file where everything is stored
#print filePath
exchFile = openMaster(filePath) #Makes list of every line in file
pointLength = exchFile[0]
garbage, sep, pointLength = pointLength.rpartition(":") #gets last item on line 1
pointLength = int(pointLength)
realPoints = [] #this list contains the actual objects so I can call them by name later
node = hou.pwd()
geo = hou.pwd().geometry()
attrUV = geo.addAttrib(hou.attribType.Vertex, "uv", (0.0, 0.0, 0.0))#Creates UV attributre
weightList = []#total weights,
weightIndex = []#this is so when I call the weight, I know what line to start one to get the weights.
startLine = "NoUV" #so later if there arent UVs we dont break
for i in exchFile:
    if "UV:" in i: #look for UV tell me what lien
        startLine = exchFile.index(i) + 1
    if "POLYGONS:" in i:#look for when polys start
        polyLine = exchFile.index(i)
    if "WEIGHT:" in i:#look for when weights start
        garbage, sep, weight = i.partition(':')
        weight = weight.strip()
        if weight not in weightList:
            weightList.append(weight)
            weightIndex.append(exchFile.index(i) + 1)
polyCount = exchFile[polyLine]
garbage, sep, polyCount = polyCount.partition(":") #get number of Polys
surfList = []
for item in range(1 + int(polyLine), 1 + int(polyLine) + int(polyCount)):#this is where we look through the list for surface names
    f = exchFile[item]
    f = f.strip()
    points, sep, PolyName = f.partition(";;")
    if PolyName not in surfList:
        surfList.append(PolyName)
for surf in surfList:
    attrGroup = geo.addAttrib(hou.attribType.Prim, surf, 0)#Creates surface attributes
for w in weightList:
    attrWeight = geo.addAttrib(hou.attribType.Point, w, 0.0)#Creates Weight attributes
for item in range(1, 1 + int(pointLength)): #makes points
    f = exchFile[item]
    f = f.strip()
    f = f.replace(" ", ",")
    pt = geo.createPoint()
    pt.setPosition(hou.Vector3(eval(f)))
    for w in weightList: #go over each weighMap
        wIndex = weightList.index(w)#get index of the item in small list weight
        vIndex = weightIndex[wIndex]#get full list index for maps
        wValue = float(exchFile[vIndex + item -1])
        pt.setAttribValue(w, wValue)#set point weight
    realPoints.append(pt)#put actually object into list for later use when looking up point names.
for item in range(1 + int(polyLine), 1 + int(polyLine) + int(polyCount)): #makes Polys
    f = exchFile[item]
    f = f.strip()
    points, sep, PolyName = f.partition(";;")
    polyPoints = []
    while True: #gets vertex for each poly
        if "," in points:
            num, sep, points = points.partition(",")
            polyPoints.append(num)
        else:
            polyPoints.append(points)
            break
    poly = geo.createPolygon()#makes th ePoly
    poly.setAttribValue(PolyName, (1))#gives it the surface name
    miniCount = 0 #this is for iterating over PolyPoints
    for p in polyPoints:
        if startLine != "NoUV": #if there are UVs get info
            uvLine = exchFile[startLine + miniCount]
            u, sep, uvLine = uvLine.partition(' ')
            v, sep, garbage = uvLine.partition(':')
        else: #else just zero out UVs
            u = 0
            v = 0
        vtx_num = poly.addVertex(realPoints[int(p)])#adds vertex to position Poly
        vtx_num.setAttribValue(attrUV, (float(u), float(v), 1.0))#Adds UV attribute info
        miniCount += 1
    startLine += len(polyPoints)
 '''})