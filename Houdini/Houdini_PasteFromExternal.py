import random
offset = random.randint(0, 1000000)

hou.node('obj/').createNode("geo", 'geoIn'+str(offset)+'', run_init_scripts = False)
hou.node('obj/geoIn'+str(offset)+'/').createNode("python", "ImportScript" )
hou.node('obj/geoIn'+str(offset)+'/ImportScript/').setParms({"python": '''
# encoding: utf-8
import tempfile, os, random, sys, re

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
        surf = re.sub(r"[^a-zA-Z0-9]", lambda m: "_{:02x}".format(ord(m.group())), surf)
        polytype = (lines[i].split(";;")[2]).strip()
        for x in (lines[i].split(";;")[0]).strip().split(","):

            pts.append(int(x.strip()))
        pts.insert(len(pts), pts[0])
        pts.pop(0)
        pts = reversed(pts)
        poly = geo.createPolygon()#makes the Poly
        for p in pts:
            pVertex.append(poly.addVertex(points[p]))#adds vertex to position Poly
        if surf not in surfList:
            attrGroup = geo.addAttrib(hou.attribType.Prim, surf, 0)#Creates surface attributes
            surfList.append(surf)
        poly.setAttribValue(surf, (1))#gives it the surface name

#Create Weights
for weightMap in weightMaps:
    weightMap[0] = re.sub(r"[^a-zA-Z0-9]", lambda m: "_{:02x}".format(ord(m.group())), weightMap[0])
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
            pVertex[count].setAttribValue(attrUV, (float(split[0].split(" ")[0]), float(split[0].split(" ")[1]), 1.0))#Adds UV attribute info
        else:
            pVertex[count].setAttribValue(attrUV, (float(split[0].split(" ")[0]), float(split[0].split(" ")[1]), 1.0))#Adds UV attribute info
        count +=1

'''})

hou.node('obj/geoIn'+str(offset)+'/ImportScript/').setHardLocked(1)