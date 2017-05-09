import time
start_time = time.time()

import tempfile, os, random, sys, re
from win32com.client import Dispatch, constants as c

xsi=Application
#"ODVertexData.txt" this is the temp file where everything is stored
filePath = os.path.normpath(tempfile.gettempdir()).split("\\")
pfile = ""
for p in filePath:
  if "xsi_temp" not in p:
    pfile += p + os.sep
filePath = pfile + "ODVertexData.txt"
importObjectName = "tempObject"

f = open(filePath, "r")
lines = f.readlines()
f.close()

vertline = []; polyline = []; uvMaps = []; morphMaps = []; weightMaps = []

#Parse File to see what Data we have
count= 0
found=""
verticesx=[] ; verticesy=[]; verticesz=[]
poly=0
polyList=[]
polys=[]
surfaces={}
weightsdict={}
morphsdict={}

for line in lines:
    if line.startswith("VERTICES:"):
      vertline.append([int(line.strip().split(":")[1].strip()), count])
      found="VERTICES"
    if line.startswith("POLYGONS:"):
      polyline.append([int(line.strip().split(":")[1].strip()), count])
      found="POLYGONS"
    if line.startswith("UV:"):  #still to be implemented
      uvMaps.append([line.strip().split(":")[1:], count]) 
      found="UV"
    if line.startswith("MORPH"):
      morphMaps.append([line.split(":")[1].strip(), count])
      found="MORPH"
      morphline=count
      morphName=line.split(":")[1].strip()	 
    if line.startswith("WEIGHT"):
      found="WEIGHT"
      weightline=count
      weightName=line.split(":")[1].strip()	 
 
    count += 1

    if found=="VERTICES" and count <= vertline[0][0]+vertline[0][1]:
        x = lines[count].split(" ")
        pos = [ float(x[0]), float(x[1]), float(x[2].strip()) ]
        verticesx.append(float(x[0]))
        verticesy.append(float(x[1]))
        verticesz.append(float(x[2].strip()))
		
    if found=="POLYGONS" and count <= polyline[0][0]+polyline[0][1]:	
        newPolyString = lines[count].split(";")[0].split(",")		
        polys.append(str(len(newPolyString)))
        polys+=newPolyString
        polyMaterial = lines[count].split(";")[2].rstrip()
        surf = (lines[count].split(";;")[1]).strip()
        if surf not in surfaces.keys():
			surfaces[surf]=[]
			surfaces[surf].append(poly)
        else:
			surfaces[surf].append(poly)
        poly+=1
		
    if found=="WEIGHT" and count <= vertline[0][0]+weightline:
        weights=float(lines[count].strip())
        if weightName not in weightsdict.keys():
			weightsdict[weightName]=[]
			weightsdict[weightName].append(weights)
        else:
			weightsdict[weightName].append(weights)
			
    if found=="MORPH" and count <= vertline[0][0]+morphline:
        x=lines[count].split(" ")
        morphs = [ float(x[0]), float(x[1]), float(x[2].strip()) ]
        if morphName not in morphsdict.keys():
			morphsdict[morphName]=[]
			morphsdict[morphName]+=morphs
        else:
			morphsdict[morphName]+=morphs

#Create Point List	
points=(tuple(verticesx), tuple(verticesy), tuple(verticesz))

#Generate Mesh	
newMesh = xsi.GetPrim("EmptyPolygonMesh", importObjectName, "", "")
newMesh.ActivePrimitive.Geometry.Set(points,tuple(polys))

#create Surfaces
for surf in surfaces.keys():
	oCluster = newMesh.ActivePrimitive.Geometry.AddCluster( c.siPolygonCluster, surf, surfaces[surf] )

#Create Weights
for weightMap in weightsdict.keys():
    wmap = xsi.CreateWeightMap("WeightMap", newMesh , weightMap, "Weight Map Property", False)(0)
    wmap.Elements.Array = weightsdict[weightMap]

#Create Morphs
for morphMap in morphsdict.keys():
    mmap = xsi.StoreShapeKey(newMesh, "", "siShapeObjectReferenceMode", 1, "", "", "siShapeContentPrimaryShape", "")
    mmap.Elements.Array = morphsdict[morphMap]
    mmap.Name=morphMap
	
#create UVs (still to be implemented)

print("---Total %s seconds ---" % (time.time() - start_time))