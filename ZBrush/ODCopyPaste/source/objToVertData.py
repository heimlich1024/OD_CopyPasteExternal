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
  for line in lines:
    if line.startswith("v "):
      points.append(line.strip()[2:])
    if line.startswith("f "):
      polygons.append(line.strip()[2:])
    if line.startswith("vt "):
      uvs.append(line.strip()[2:])

  output += "VERTICES:" + str(len(points)) + "\n"
  for p in points:
    output += p + "\n"

  output += "POLYGONS:" + str(len(polygons)) + "\n"
  count = 0
  uvinfo = []
  for poly in polygons:
      pts = poly.split(" ")
      newpts = []
      #indices in an vertdata start at 0, so we gotta subtract one from each index
      for p in pts:
        if "/" in p:
          newpts.append(str(int(p.split("/")[0]) - 1))
          uvinfo.append([count, int(p.split("/")[1]), int(p.split("/")[0]) - 1])
        else:
          newpts.append(str(int(p) - 1))
      count += 1
      output += ",".join(newpts) + ";;Default;;FACE\n"

  if len(uvinfo) > 0:
    output += "UV:Default:" + str(len(uvinfo)) + "\n"
    for info in uvinfo:
      output += uvs[info[1]-1][1:] + ":PLY:" + str(info[0]) + ":PNT:" + str(info[2]) + "\n"

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
