
###############################################################################
# Create a max script file, and this is how you call                          #
# it in the max script:                                                       #
# python.ExecuteFile "<full path.filename">                                   #
# example:                                                                    #
# python.ExecuteFile "C:\Users\Oliver\Desktop\3DSMax_PastefromExternal.py"    #
###############################################################################
# encoding: utf-8
import MaxPlus, tempfile, os

def buildODMesh(mesh):

    file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"

    #open the temp file
    if os.path.exists(file):
      f = open(file)
      lines = f.readlines()
      f.close()

    vertline   = []
    polyline   = []
    uvMaps     = []
    morphMaps  = []
    weightMaps = []
    count      = 0
    #Parse File to see what Data we have
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

    #create Points
    mesh.SetNumVerts(vertline[0][0])
    for verts in vertline:
        points = []
        count = 0
        for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
            x = lines[i].split(" ")
            pt = [ float(x[0]), float(x[2].strip())*-1, float(x[1].strip()) ]
            mesh.SetVert(count, MaxPlus.Point3(pt[0], pt[1], pt[2]))
            count += 1

    #need to calculate the amount of faces we are going to have
    faces = 0
    for polygons in polyline:
        for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
            pt = []
            for x in (lines[i].split(";;")[0]).strip().split(","):
                pt.append(x.strip())
            if len(pt) > 3:
                faces += 2
            else: faces += 1

        #create Polygons
        mesh.SetNumFaces(faces)
        count = 0
        for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
            pts = []
            surf = (lines[i].split(";;")[1]).strip()
            polytype = (lines[i].split(";;")[2]).strip()
            for x in (lines[i].split(";;")[0]).strip().split(","):
                pts.insert(0, int(x.strip()))
            if len(pts) > 3:
                faces += 1
                mesh.GetFace(count).SetVerts(pts[0], pts[1], pts[2])
                mesh.GetFace(count).SetEdgeVisFlags(1,1,0)
                count += 1
                mesh.GetFace(count).SetVerts(pts[2], pts[3], pts[0])
                mesh.GetFace(count).SetEdgeVisFlags(1,1,0)
            else:
                mesh.GetFace(count).SetVerts(pts[0], pts[1], pts[2])
                mesh.GetFace(count).SetEdgeVisFlags(1,1,0)
            count +=1

def main():
    geom = MaxPlus.Factory.CreateGeomObject(MaxPlus.ClassIds.TriMeshGeometry)
    tri = MaxPlus.TriObject._CastFrom(geom)
    mesh = tri.GetMesh()
    buildODMesh(mesh)
    node = MaxPlus.Factory.CreateNode(tri)

if __name__ == "__main__":
    main()