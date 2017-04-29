hou.node('obj/').createNode("geo", "geoIn", run_init_scripts = False)
hou.node('obj/geoIn/').createNode("python", "ImportScript" )
hou.node('obj/geoIn/ImportScript/').setParms({"python": '''

import tempfile, os, random, sys

filePath = tempfile.gettempdir() + os.sep + ".." + os.sep + "ODVertexData.txt" #this is the temp file where everything is stored
#print filePath

f = open(filePath, "r")
lines = f.readlines()
f.close()

node = hou.pwd()
geo = hou.pwd().geometry()

vertline = []; polyline = []; uvMaps = []; morphMaps = []; weightMaps = []

#Parse File to see what Data we have
count      = 0
for line in lines:
    if line.startswith("VERTICES:"):
      vertline.append([int(line.strip().split(":")[1].strip()), count])
    if line.startswith("POLYGONS:"):
      polyline.append([int(line.strip().split(":")[1].strip()), count])
    if line.startswith("UV:"):
      uvMaps.append([line.strip().split(":")[1:], count])  # changed this to add the # of uv coordinates into the mix
    if line.startswith("MORPH"):
      morphMaps.append([line.split(":")[1].strip(), count])
    if line.startswith("WEIGHT"):
      weightMaps.append([line.split(":")[1].strip(), count])
    count += 1

#Create Points
points = []
for verts in vertline:
    for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
        x = lines[i].split(" ")
        pos = [ float(x[0]), float(x[1]), float(x[2].strip()) ]
        pt = geo.createPoint()
        pt.setPosition(pos)
        points.append(pt)

#create Polygons
surfList = []; pVertex = []
for polygons in polyline:
    for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
        pts = []
        surf = (lines[i].split(";;")[1]).strip()
        polytype = (lines[i].split(";;")[2]).strip()
        for x in (lines[i].split(";;")[0]).strip().split(","):
            pts.append(int(x.strip()))
        poly = geo.createPolygon()#makes th ePoly
        for p in pts:
            pVertex.append(poly.addVertex(points[p]))#adds vertex to position Poly
        if surf not in surfList:
            attrGroup = geo.addAttrib(hou.attribType.Prim, surf, 0)#Creates surface attributes
            surfList.append(surf)
        poly.setAttribValue(surf, (1))#gives it the surface name

#Create Weights
for weightMap in weightMaps:
    geo.addAttrib(hou.attribType.Point, weightMap[0], 0.0)
    count = 0
    for point in points:
        if lines[weightMap[1]+1+count].strip() != "None":
            point.setAttribValue(weightMap[0], float(lines[weightMap[1]+1+count].strip()))#set point weight
        count += 1

#create UVs
for uvMap in uvMaps:
    attrUV = geo.addAttrib(hou.attribType.Vertex, "uv", (0.0, 0.0, 0.0))#Creates UV attributre
    count = 0
    for i in range(int(uvMap[0][1])):
        line = lines[uvMap[1]+1+count]
        split = line.split(":")
        if len(split) > 3: #check the format to see if it has a point and poly classifier, determining with that, whether the uv is discontinuous or continuous
            #mesh_edit_op.pntVPMap(mesh_edit_op.state, points[int(split[4])], polys[int(split[2])], lwsdk.LWVMAP_TXUV, uvMap[0][0], [float(split[0].split(" ")[0]), float(split[0].split(" ")[1])])
            print "Discont not working yet"
        else:
            pVertex[count].setAttribValue(attrUV, (float(split[0].split(" ")[0]), float(split[0].split(" ")[1]), 1.0))#Adds UV attribute info
        count +=1

'''})