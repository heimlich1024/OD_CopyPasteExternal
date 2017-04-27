import os, sys
import maya.cmds as cmds
import tempfile
import maya.OpenMaya as om

exportFilename =  tempfile.gettempdir() + os.sep + "ODVertexData.txt"

global exportedObj

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


def fn_getObjectData():
    global exportedObj
    curSel = cmds.ls(selection = True)
    if len(curSel) > 0:
        exportedObj.name = curSel[0]
        exportedObj.vertexCount = cmds.polyEvaluate(exportedObj.name, vertex = True)
        exportedObj.polyCount = cmds.polyEvaluate(exportedObj.name, face = True)

        exportedObj.vertices = []
        exportedObj.polys = []
        exportedObj.weightMap = []

        for v in range(0,exportedObj.vertexCount - 0, 1):
            vStr = exportedObj.name + ".vtx[" + str(v) + "]"
            vPos = cmds.xform(vStr, q= True,  os = True, translation = True)
            exportedObj.vertices.append(vPos)
            try:
                w = cmds.polyColorPerVertex(vStr, q = True, r = True)[0]
            except:
                w = -1

            exportedObj.weightMap.append(w)


        for f in range(0,exportedObj.polyCount - 0, 1):
            vStr = exportedObj.name + ".f[" + str(f) + "]"
            cmds.select(vStr, replace = True)
            verts = cmds.polyInfo(fv = True)
            vertsTemp = verts[0].split(":")
            vertsTemp = vertsTemp[1].split(" ")
            vList = []
            for fv in vertsTemp:
                if fv.strip() != "":
                    vList.append(int(fv))
            exportedObj.polys.append(vList)

        cmds.select(curSel, replace = True)
        return True
    else:
        cmds.confirmDialog(title='Error:', message='No object selected!',button='Ok')
        print "Nothing selected!"
        return False

def fn_saveTempObject():
    global exportedObj

    f = open(exportFilename, 'w')
    sname = cmds.file(q = True, sceneName = True)

    f.write(sname)
    f.write ("VERTICES:")
    f.write (str(exportedObj.vertexCount))
    f.write ("\n")
    for v in exportedObj.vertices:
        f.write(str(v[0])+ " ")
        f.write(str(v[1])+ " ")
        f.write(str(v[2]))
        f.write("\n")
    f.write("POLYGONS:" + str(exportedObj.polyCount) + "\n")

    for p in exportedObj.polys:
        count = 0
        for v in p:
            f.write(str(v))
            if count < (len(p)-1):
                f.write(",")
            count += 1
        polytype = "FACE"
        f.write(";;Default;;"+polytype+"\n")

    if exportedObj.weightMap[0] != -1:
        f.write("WEIGHT:myweightmap\n")
        for w in exportedObj.weightMap:
            f.write(str(w) + "\n")


    f.close()



###########################
### main


exportedObj = iobject_def()

objectOK = fn_getObjectData()
if objectOK == True:
	fn_saveTempObject()

