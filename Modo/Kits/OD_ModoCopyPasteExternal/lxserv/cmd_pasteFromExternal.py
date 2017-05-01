
################################################################################
#
# scriptname.py
#
# Version: 0.001
#
# Author: Oliver Hotz
#
# Description:
#
# Last Update:
#
################################################################################

import lx
import lxifc
import lxu.command
import modo, tempfile, os

class OD_PasteFromExternal(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
      scene = modo.Scene()
      #Read temporary Data File
      file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"
      if os.path.exists(file):
        f = open(file, "r")
        lines = f.readlines()
        f.close()

        vertline = []; polyline = []; uvMaps = []; morphMaps = []; weightMaps = []; count = 0
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

        # Add a new mesh object to the scene and grab the geometry object
        mesh = scene.selectedByType("mesh")
        if mesh:
          mesh = mesh[0]
          if len(mesh.geometry.vertices) > 0:
            mesh.geometry.internalMesh.Clear()
        else:
          mesh = scene.addMesh('ODCopy')

        #select new emply mesh
        scene.select(mesh)
        geo = mesh.geometry

        for verts in vertline:
          #generate points
          points = []
          for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
            x = lines[i].split(" ")
            points.append(geo.vertices.new((float(x[0]), float(x[1]), float(x[2].strip()))))

        #Query Existing Materials
        allsurfaces = []
        for material in scene.items('advancedMaterial'):
          allsurfaces.append(material.name)

        #generate Polys from the Points and assign materials
        for polygons in polyline:
          polys = []
          count = 0
          for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
            pts = []
            surf = (lines[i].split(";;")[1]).strip()
            ptch = (lines[i].split(";;")[2]).strip()
            if surf not in allsurfaces:
              allsurfaces.append(surf)
              scene.addMaterial(name=surf)
            for x in (lines[i].split(";;")[0]).strip().split(","):
              pts.append(int(x.strip()))
            ptype = lx.symbol.iPTYP_FACE
            if ptch == "CCSS": ptype = lx.symbol.iPTYP_PSUB
            elif ptch == "SUBD": ptype = lx.symbol.iPTYP_SUBD
            geo.polygons.new(vertices=(pts), reversed=False, polyType=ptype)
            geo.polygons[count].materialTag = surf
            count += 1

        #Apply Weights
        for weightMap in weightMaps:
          weight = geo.vmaps.addMap(lx.symbol.i_VMAP_WEIGHT, weightMap[0])
          for i in range(len(geo.vertices)):
            if lines[weightMap[1]+1+i].strip() != "None":
              weight[i] = float(lines[weightMap[1]+1+i].strip())

        #Apply Morphs
        for morphMap in morphMaps:
          mo = geo.vmaps.addMorphMap(morphMap[0], False)
          for i in range(len(geo.vertices)):
            if lines[morphMap[1]+1+i].strip() != "None":
              mo.setAbsolutePosition(i, [float(lines[i+1].split(" ")[0]) + float(lines[morphMap[1]+1+i].split(" ")[0]), float(lines[i+1].split(" ")[1]) + float(lines[morphMap[1]+1+i].split(" ")[1]), float(lines[i+1].split(" ")[2]) + float(lines[morphMap[1]+1+i].split(" ")[2])])

        #Apply UV Maps
        for uvMap in uvMaps:
          uvm = geo.vmaps.addMap(lx.symbol.i_VMAP_TEXTUREUV, uvMap[0][0])
          count = 0
          for i in range(int(uvMap[0][1])):
            line = lines[uvMap[1]+1+count]
            split = line.split(":")
            if len(split) > 3: #check the format to see if it has a point and poly classifier, determining with that, whether the uv is discontinuous or continuous
              geo.polygons[int(split[2])].setUV((float(split[0].split(" ")[0]), float(split[0].split(" ")[1])), geo.vertices[int(split[4])], uvm)
            else:
              pass
            count +=1

        geo.setMeshEdits()
      else:
        print "No Data File Available."


    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(OD_PasteFromExternal, "OD_PasteFromExternal")

