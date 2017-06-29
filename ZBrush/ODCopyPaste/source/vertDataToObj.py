#pyinstaller --distpath "C:\Users\Oliver\BitTorrent Sync\BTSync\_CODING\LW_Python\___WORK_IN_PROGRESS-EXPERIMENTS\ExternalCopyPaste\ODVertData_To_Obj.py" --noupx --onefile ODVertData_To_Obj.py

import tempfile, os, sys

def vertDataToObj(outputfile):

  output = ""
  inputfile = tempfile.gettempdir() + os.sep + "ODVertexData.txt"
  file = open(inputfile, "r")
  lines = file.readlines()
  file.close()

  #Parse File to see what Data we have
  vertline = []; polyline = []; uvMaps = []; morphMaps = []; weightMaps = []
  count = 0
  for line in lines:
    if line.startswith("VERTICES:"):
      vertline.append([int(line.strip().split(":")[1].strip()), count])
    if line.startswith("POLYGONS:"):
      polyline.append([int(line.strip().split(":")[1].strip()), count])
    if line.startswith("UV:"):
      uvMaps.append([line.strip().split(":")[1:], count])  # changed this to add the # of uv coordinates into the mix
    count += 1

  #write header
  output += "o ODVertexData.obj\n"
  output += "g default\n"

  #rewrite verts
  for verts in vertline:
      for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
        x = map(float, lines[i].split())
        output += "v " + str(x[0]) + " " + str(x[1]) + " " + str(x[2]) + "\n"

  #Set UV Map Values
  uvforobj = []
  for uvMap in uvMaps:
    count = 0
    for i in range(int(uvMap[0][1])):
      split = lines[uvMap[1]+1+count].split(":")
      output += "vt " + str(float(split[0].split(" ")[0])) + " " + str(float(split[0].split(" ")[1])) + "\n"
      count +=1

  #create Polygons
  for polygons in polyline:
    polys = []
    count = 0
    for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
      pts = lines[i].split(";;")[0].split(",")
      newpts = []
      #indices in an obj start at 1, so we gotta add one to each index
      for p in pts:
        if len(uvMaps) < 1:
          newpts.append(str(int(p) + 1))
        else:
          newpts.append(str(int(p) + 1) + "/" + str(count+1))
          count += 1
      output += "g " + lines[i].split(";;")[1].strip() + "\n"
      output += "usemtl " + lines[i].split(";;")[1].strip() + "\n"
      output += "f " + " ".join(newpts) + "\n"

  #writing output file
  f = open(outputfile, "w")
  f.write(output)
  f.close()

##########################################################
# Main Call (just vertices and polys for now, no uv yet) #
##########################################################

##### to convert vertex data to obj
outputfile = os.path.dirname(sys.executable) + os.sep + "1.OBJ"
vertDataToObj(outputfile)