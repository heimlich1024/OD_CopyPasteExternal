selnode = hou.selectedNodes()
for node in hou.selectedNodes():
    selPath = node.path()

sel = selPath.split("/")[-2]

hou.node('obj/'+sel).createNode("python", "ExportScript" )
hou.node('obj/'+sel+'/ExportScript/').setParms({"python": '''
import tempfile, os, random, sys

filePath = tempfile.gettempdir() + os.sep + ".." + os.sep + "ODVertexData.txt"

node = hou.pwd()
geo = node.geometry()

if len(geo.points()) > 0:
    f = open(filePath, "w")

    f.write("VERTICES:"+str(len(geo.points())) + "\\n")
    for point in geo.points():
        pos = point.position()
        f.write(str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]*-1) + "\\n")
    polyPrims = [prim for prim in geo.prims() if prim.type() == hou.primType.Polygon]

    uvs = []
    check = geo.findVertexAttrib("uv")
    f.write("POLYGONS:"+str(len(polyPrims)) + "\\n")
    count = 0
    for (fid, prim) in enumerate(polyPrims):
        ppoint = ""
        for point in prim.vertices():
             ppoint += "," + str(geo.points().index(hou.Vertex.point(point)))
             if check != None:
                uvs.append(str(point.attribValue("uv")[0]) + " " + str(point.attribValue("uv")[1]) + ":PLY:" + str(count) + ":PNT:" + str(geo.points().index(hou.Vertex.point(point))) + "\\n")
        surf = "Default"
        polytype = "FACE"
        #print ppoint
        f.write(ppoint[1:] + ";;" + surf + ";;" + polytype + "\\n")
        count += 1

    attribs = geo.pointAttribs()
    weights = []
    for attrib in attribs:
        if attrib.type() == hou.attribType.Point:
            if attrib.dataType() == hou.attribData.Float and attrib.size() == 1:
                weights.append(attrib.name())

    if len(weights) > 0:
        for wmap in weights:
            attrib = wmap
            f.write("WEIGHT:" + wmap + "\\n")
            for p in geo.points():
                f.write(str(p.attribValue(wmap))+ "\\n")

    if len(uvs) > 0:
        f.write("UV:UVMap:"+ str(len(uvs)) + "\\n")
        for uv in uvs:
            f.write(uv)
    f.close()
    '''})

hou.node('obj/'+sel).createNode("convert", "ODConvertToPolygon" )
hou.node('obj/'+sel+'/ODConvertToPolygon/').setInput(0, hou.node(selPath))
hou.node('obj/'+sel+'/ExportScript/').setInput(0, hou.node('obj/'+sel+'/ODConvertToPolygon/'))


#hou.node('obj/'+sel+'/ExportScript/').setInput(0, hou.node(selPath))
hou.node('obj/'+sel+'/ExportScript/').setDisplayFlag(True)
hou.node('obj/'+sel+'/ExportScript/').setRenderFlag(True)
hou.node('obj/'+sel+'/ExportScript/').setCurrent(1, False)
hou.node('obj/'+sel+'/ExportScript/').cook(force=True, frame_range=(int(hou.frame()),int(hou.frame())))
hou.node('obj/'+sel+'/ExportScript/').destroy()
hou.node('obj/'+sel+'/ODConvertToPolygon/').destroy()
