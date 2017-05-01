#! /usr/bin/env python
# -*- Mode: Python -*-
# -*- coding: ascii -*-

__author__     = "Oliver Hotz"
__date__       = "April 27, 2017"
__copyright__  = ""
__version__    = "1.0"
__maintainer__ = "Oliver Hotz"
__email__      = "oliver@origamidigital.com"
__status__     = "Copies / Pastes Objects between various 3d applications"
__lwver__      = "11"

try:
  import lwsdk, os, tempfile, sys
except ImportError:
    raise Exception("The LightWave Python module could not be loaded.")

##########################################################################
#  Pastes temporary data exchange file to current layer                  #
##########################################################################

class OD_LWPasteFromExternal(lwsdk.ICommandSequence):
  def __init__(self, context):
      super(OD_LWPasteFromExternal, self).__init__()

  def fast_point_scan(self, point_list, point_id):
    point_list.append(point_id)
    return lwsdk.EDERR_NONE

  # LWCommandSequence -----------------------------------
  def process(self, mod_command):

    #get the command arguments (so that we can also run this from layout)
    cmd = mod_command.argument.replace('"', '')

    file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"

    #open the temp file
    if os.path.exists(file):
      f = open(file)
      lines = f.readlines()
      f.close()
    else:
      lwsdk.LWMessageFuncs().info("Storage File does not exist.  Needs to be created via the Layout CopyTransform counterpart", "")
      return 0

    #get the pointcount from the file
    pntCount = int(lines[0].split(":")[1].strip())

    #find existing Vmaps
    loaded_weight = []; loaded_uv = []; loaded_morph = []
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_WGHT )):
      loaded_weight.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_WGHT, u))
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_TXUV )):
      loaded_uv.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_TXUV, u))
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_MORF )):
      loaded_morph.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_MORF, u))

    #check if we are in modeler, if so, clear polys
    # if cmd == "":
    #   #Remove Current mesh from layer
    #   command = mod_command.lookup(mod_command.data, "CUT")
    #   result = mod_command.execute(mod_command.data, command, None, lwsdk.OPLYR_FG)

    edit_op_result = lwsdk.EDERR_NONE
    mesh_edit_op = mod_command.editBegin(0, 0, lwsdk.OPSEL_USER)
    if not mesh_edit_op:
      print >>sys.stderr, 'Failed to engage mesh edit operations!'
      return lwsdk.AFUNC_OK

    try:
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
      for verts in vertline:
        points = []
        for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
          x = lines[i].split(" ")
          pt = [ float(x[0]), float(x[1]), float(x[2].strip())*-1 ]
          points.append(mesh_edit_op.addPoint(mesh_edit_op.state, pt))
      #create Polygons
      for polygons in polyline:
        polys = []
        for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
          pts = []
          surf = (lines[i].split(";;")[1]).strip()
          polytype = (lines[i].split(";;")[2]).strip()
          for x in (lines[i].split(";;")[0]).strip().split(","):
            pts.insert(0, (points[int(x.strip())]))
          ptype = lwsdk.LWPOLTYPE_FACE
          if polytype == "CCSS": ptype = lwsdk.LWPOLTYPE_SUBD
          elif polytype == "SUBD": ptype = lwsdk.LWPOLTYPE_PTCH
          polys.append(mesh_edit_op.addPoly(mesh_edit_op.state, ptype, None, surf, pts))
      #setup  weightmaps
      for weightMap in weightMaps:
        mesh_edit_op.vMapSelect(mesh_edit_op.state, weightMap[0], lwsdk.LWVMAP_WGHT, 1)
        count = 0
        for point in points:
          if lines[weightMap[1]+1+count].strip() != "None":
            mesh_edit_op.pntVMap(mesh_edit_op.state, point, lwsdk.LWVMAP_WGHT, weightMap[0], [float(lines[weightMap[1]+1+count].strip())])
          count += 1
      #Set Mprph Map Values
      for morphMap in morphMaps:
        mesh_edit_op.vMapSelect(mesh_edit_op.state, morphMap[0], lwsdk.LWVMAP_MORF, 3)
        count = 0
        for point in points:
          if lines[morphMap[1]+1+count].strip() != "None":
            mesh_edit_op.pntVMap(mesh_edit_op.state, point, lwsdk.LWVMAP_MORF, morphMap[0], [float(lines[morphMap[1]+1+count].split(" ")[0]), float(lines[morphMap[1]+1+count].split(" ")[1]), float(lines[morphMap[1]+1+count].split(" ")[2])])
          count += 1
      #Set UV Map Values
      for uvMap in uvMaps:
        mesh_edit_op.vMapSelect(mesh_edit_op.state, uvMap[0][0], lwsdk.LWVMAP_TXUV, 2)
        count = 0
        for i in range(int(uvMap[0][1])):
          line = lines[uvMap[1]+1+count]
          split = line.split(":")
          if len(split) > 3: #check the format to see if it has a point and poly classifier, determining with that, whether the uv is discontinuous or continuous
            mesh_edit_op.pntVPMap(mesh_edit_op.state, points[int(split[4])], polys[int(split[2])], lwsdk.LWVMAP_TXUV, uvMap[0][0], [float(split[0].split(" ")[0]), float(split[0].split(" ")[1])])
          else:
            mesh_edit_op.pntVMap(mesh_edit_op.state, points[int(split[2])], lwsdk.LWVMAP_TXUV, uvMap[0][0], [float(split[0].split(" ")[0]), float(split[0].split(" ")[1])])
          count +=1

      # #remove unused UVMaps
      # for m in loaded_uv:
      #   if m not in str(uvMaps):
      #     mesh_edit_op.vMapSelect(mesh_edit_op.state,  m, lwsdk.LWVMAP_TXUV, 2)
      #     mesh_edit_op.vMapRemove(mesh_edit_op.state)

      # # #remove unused UVMaps
      # for m in loaded_weight:
      #   if m not in str(weightMaps):
      #     mesh_edit_op.vMapSelect(mesh_edit_op.state,  m, lwsdk.LWVMAP_WGHT, 1)
      #     mesh_edit_op.vMapRemove(mesh_edit_op.state)

      # # #remove unused UVMaps
      # for m in loaded_morph:
      #   if m not in str(morphMaps):
      #     mesh_edit_op.vMapSelect(mesh_edit_op.state,  m, lwsdk.LWVMAP_MORF, 3)
      #     mesh_edit_op.vMapRemove(mesh_edit_op.state)

    except:
      edit_op_result = lwsdk.EDERR_USERABORT
      raise
    finally:
      mesh_edit_op.done(mesh_edit_op.state, edit_op_result, 0)

    return lwsdk.AFUNC_OK

ServerTagInfo_OD_LWPasteFromExternal = [
  ( "OD_LWPasteFromExternal", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
  ( "OD_LWPasteFromExternal", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]

ServerRecord = { lwsdk.CommandSequenceFactory("OD_LWPasteFromExternal", OD_LWPasteFromExternal) : ServerTagInfo_OD_LWPasteFromExternal }