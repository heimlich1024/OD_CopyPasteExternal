import Rhino, tempfile, os
import rhinoscriptsyntax as rs

def exportODMesh():

    file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"

    obj = rs.GetObject("Select mesh", rs.filter.mesh, True)
    vertices = rs.MeshVertices(obj)
    faces = rs.MeshFaceVertices(obj)

    f = open(file, "w")

    f.write("VERTICES:" + str(len(vertices))+"\n")
    for vert in vertices:
        f.write(str(vert[0]) + " " + str(vert[2]) + " " + str(vert[1]*-1) + "\n")

    f.write("POLYGONS:" + str(len(faces)) + "\n")
    for face in faces:
        fpt = []
        for p in face:
            if str(p) not in fpt: #need this check as when there's 3pt polys somehow, it gives 4 points
                fpt.append(str(p))
        line = ",".join(fpt)
        line += ";;" + "Default" + ";;" + "FACE" + "\n"
        f.write(line)
    f.close()

if __name__ == "__main__":
    exportODMesh()