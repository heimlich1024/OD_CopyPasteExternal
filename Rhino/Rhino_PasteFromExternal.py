import Rhino, tempfile, os
import scriptcontext
import System.Guid

def buildODMesh():

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

    mesh = Rhino.Geometry.Mesh()

    #create Points
    for verts in vertline:
        for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
            x = lines[i].split(" ")
            pt = [ float(x[0]), float(x[2].strip())*-1, float(x[1].strip()) ]
            mesh.Vertices.Add(pt[0], pt[1], pt[2])

    for polygons in polyline:
        #create Polygons
        for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
            pts = []
            surf = (lines[i].split(";;")[1]).strip()
            polytype = (lines[i].split(";;")[2]).strip()
            for x in (lines[i].split(";;")[0]).strip().split(","):
                pts.append(int(x.strip()))
            if len(pts) == 4:
                mesh.Faces.AddFace(pts[0], pts[1], pts[2], pts[3])
            elif len(pts) == 3:
                mesh.Faces.AddFace(pts[0], pts[1], pts[2])

    mesh.Normals.ComputeNormals()
    mesh.Compact()
    if scriptcontext.doc.Objects.AddMesh(mesh)!=System.Guid.Empty:
        scriptcontext.doc.Views.Redraw()
        return Rhino.Commands.Result.Success
    return Rhino.Commands.Result.Failure

if __name__ == "__main__":
    buildODMesh()