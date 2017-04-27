import os, sys
import maya.cmds as cmds
import tempfile
import maya.OpenMaya as om

importFilename =  tempfile.gettempdir() + os.sep + "ODVertexData.txt"
importObjectName = "tempObject"

global importedObj

class iobject_def:
    name = ""
    vertexCount = 0
    polyCount = 0
    vertices = []
    polys = []
    materials = []
    weightMap = []
    omVertices = []
    loaded_data = []


def fn_loadObjectFromTextfile():
    global importedObj
    importedObj.loaded_data = []
    if not os.path.exists(importFilename):
        print "Cant find file"
        cmds.confirmDialog(title='Error:', message='Cant find file:\n' + importFilename,button='Ok')
        return False
    else:
        f = open(importFilename)
        importedObj.loaded_data = f.readlines()
        f.close()
        return True

def fn_parseTextdata():
    global importObj

    importedObj.name = "ODCOPY"

    # parse vertices:
    importedObj.vertexCount = int(importedObj.loaded_data[0].split(":")[1].strip())
    importedObj.vertices = []
    importedObj.omVertices = []

    for v in range(1, importedObj.vertexCount + 1, 1):
        newVertString = importedObj.loaded_data[v].split(" ")
        newVert = [ float(newVertString[0]), float(newVertString[1]), float(newVertString[2].rstrip()) ]
        importedObj.vertices.append(newVert)
        importedObj.omVertices.append(om.MPoint(newVert[0], newVert[1], newVert[2]))

    ### parse polys

    polyLine = -1
    count = 0

    for line in importedObj.loaded_data:
        if line.startswith("POLYGONS:"):
            polyLine = count
            break
        count += 1

    if polyLine == -1:
        cmds.confirmDialog(title='Error:', message='Error reading file\nNo polygons found!',button='Ok')
        return False

    importedObj.polyCount = int(importedObj.loaded_data[polyLine].split(":")[1])
    importedObj.polys = []
    importedObj.materials = []
    polyLine += 1

    for p in range(polyLine, polyLine + importedObj.polyCount , 1):
        newPolyString = importedObj.loaded_data[p].split(";")[0].split(",")
        newPoly = []
        for vs in newPolyString:
            newPoly.append(int(vs))
        importedObj.polys.append(newPoly)
        polyMaterial = importedObj.loaded_data[p].split(";")[2].rstrip()
        importedObj.materials.append(polyMaterial)


    ### parse weights

    importedObj.weights = []
    weightLine = -1
    count = 0

    for line in importedObj.loaded_data:
        if line.startswith("WEIGHT:"):
            weightLine = count
            break
        count += 1

    if weightLine != -1:
        weightLine += 1
        for w in range(weightLine, weightLine + importedObj.vertexCount , 1):
            newWeightString = importedObj.loaded_data[w].rstrip()
            importedObj.weightMap.append(float(newWeightString))

    return True

def fn_createObject_openMaya():
    global importedObj

    cmds.select( all = True, hierarchy = True)
    currentObjs = cmds.ls(selection = True )

    newMesh = om.MFnMesh()

    mergeVertices = True
    pointTolerance = 0.0001

    for p in range(0, len(importedObj.polys), 1):
        polylist = []
        vCount = len(importedObj.polys[p])
        polylist = om.MPointArray()
        polylist.setLength(vCount)
        for i in range(vCount):
            polylist.set(importedObj.omVertices[int(importedObj.polys[p][i])], i)

        newMesh.addPolygon(polylist, mergeVertices, pointTolerance)


    if len(importedObj.weightMap) > 0:
        for v in range(0, importedObj.vertexCount , 1):
            c = importedObj.weightMap[v]
            vColor = om.MColor(c,c,c,c )
            newMesh.setVertexColor(vColor,v)

    newMesh.updateSurface()

    cmds.select( all = True, hierarchy = True)
    cmds.select(currentObjs, deselect = True)
    newObjs = cmds.ls(selection = True, transforms = True )
    cmds.select(newObjs, replace = True)
    cmds.sets( newObjs, e=True,forceElement='initialShadingGroup')
    cmds.rename (newObjs, importObjectName)



def fn_createObject_PolyCreate():
    global importedObj

    objList = []

    for p in range(0, len(importedObj.polys), 1):
        facelist = []

        for v in range(0, len(importedObj.polys[p]),1):
            pVert = importedObj.vertices[importedObj.polys[p][v]]
            facelist.append(pVert)
        objList.append((cmds.polyCreateFacet( p = facelist, ch = False))[0])

    cmds.polyUnite( objList, ch = False, n=importObjectName )

###########################
### main


importedObj = iobject_def()
loadSuccess = fn_loadObjectFromTextfile()

if loadSuccess == True:
    parseSuccess = fn_parseTextdata()
    if parseSuccess == True:
        #fn_createObject_PolyCreate()
        fn_createObject_openMaya()



