#pyinstaller --distpath "C:\Users\Oliver\BitTorrent Sync\BTSync\_CODING\LW_Python\___WORK_IN_PROGRESS-EXPERIMENTS\ExternalCopyPaste\ZBrush" --noupx --onefile ODVertData_To_Obj.py
import tempfile, os, sys

def objToVertData(inputfile):
  output = ""
  file = open(inputfile, "r")
  lines = file.readlines()
  file.close()
  points = []
  polygons = []
  uvs = []
  vertexnormals = []
  count = 0
  for line in lines:
    if line.startswith("v "):
      points.append(line.strip()[2:])
    if line.startswith("f "):
      polygons.append([line.strip()[2:], count])
    if line.startswith("vt "):
      uvs.append(line.strip()[2:])
    if line.startswith("vn "):
      vertexnormals.append(line.strip()[2:])
    count += 1

  output += "VERTICES:" + str(len(points)) + "\n"
  for p in points:
    output += p + "\n"

  output += "POLYGONS:" + str(len(polygons)) + "\n"
  count = 0
  uvinfo = []
  mat = "Default"
  for poly in polygons:
      pts = poly[0].split(" ")
      newpts = []
      #indices in an vertdata start at 0, so we gotta subtract one from each index
      for p in pts:
        if "/" in p:
          newpts.append(str(int(p.split("/")[0]) - 1))
          uvinfo.append([count, int(p.split("/")[1]), int(p.split("/")[0]) - 1])
        else:
          newpts.append(str(int(p) - 1))
      count += 1
      if "usemtl" in lines[poly[1]-1]:
        mat = lines[poly[1]-1].split(" ")[1].strip()
      output += ",".join(newpts) + ";;" + mat + ";;FACE\n"

  if len(uvinfo) > 0:
    output += "UV:Default:" + str(len(uvinfo)) + "\n"
    for info in uvinfo:
      output += uvs[info[1]-1][1:] + ":PLY:" + str(info[0]) + ":PNT:" + str(info[2]) + "\n"

  if len(vertexnormals) > 0:
    output += "VERTEXNORMALS:" + str(len(vertexnormals)) + "\n"
    for normal in vertexnormals:
      output += normal + "\n"

  #writing output file
  f = open(tempfile.gettempdir() + os.sep + "ODVertexData.txt", "w")
  f.write(output)
  f.close()

##########################################################
# Main Call (just vertices and polys for now, no uv yet) #
##########################################################

##### to convert an obj to vertdata
inputfile = os.path.dirname(sys.executable) + os.sep + "1.OBJ"
objToVertData(inputfile)
