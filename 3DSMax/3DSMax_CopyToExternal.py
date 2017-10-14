###############################################################################
# Create a max script file, and this is how you call                          #
# it in the max script:                                                       #
# python.ExecuteFile "<full path.filename">                                   #
# example:                                                                    #
# python.ExecuteFile "C:\Users\Oliver\Desktop\3DSMax_CopyToExternal.py"       #
###############################################################################
# encoding: utf-8
import MaxPlus, tempfile, os

def writeODMesh(mesh):

    file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"
    f = open(file, "w")
    f.write("VERTICES:" + str(mesh.GetNumVertices()) + "\n")
    for i in xrange(mesh.GetNumVertices()):
      f.write(str(mesh.GetVertex(i).GetX()) + " " + str(mesh.GetVertex(i).GetZ()) + " " + str(mesh.GetVertex(i).GetY()*-1) + "\n")

    f.write("POLYGONS:" + str(mesh.GetNumFaces()) + "\n")
    for i in xrange(mesh.GetNumFaces()):
      #materialID = mesh.GetFace(i).GetMatID()
      fpts = []
      for x in xrange(0,3):
        face = mesh.GetFace(i)
        fpts.append(str(face.GetVert(x)))
      fpts = fpts[::-1]
      line = ",".join(fpts)
      #currently, material name and facetype are hardcoded
      line += ";;" + "Default" + ";;" + "FACE" + "\n"
      f.write(line)

    f.close()
    print "Finished Copy..."

def main():
    time = MaxPlus.Animation.GetTime()
    now = MaxPlus.Core.GetCurrentTime()
    triObjectID = MaxPlus.Class_ID(0x0009, 0)
    for node in MaxPlus.SelectionManager.Nodes:
        obj = node.EvalWorldState(time).Getobj()
        print "obj", obj
        if (obj.CanConvertToType(triObjectID)):
            mesh = MaxPlus.TriObject._CastFrom(obj.ConvertToType(triObjectID, time)).GetMesh()

    if mesh.GetNumVertices() > 0:
      writeODMesh(mesh)
    else:
      print "No Vertices Found, will only work on MeshObjects"

if __name__ == "__main__":
    main()