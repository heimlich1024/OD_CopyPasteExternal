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
__lwver__      = "2015"

try:
  import lwsdk, os, tempfile, sys, time
except ImportError:
    raise Exception("The LightWave Python module could not be loaded.")

##########################################################################
#  copys current mesh to temporary file for data exchange                #
##########################################################################

class OD_LWCopyToExternal(lwsdk.ICommandSequence):
  def __init__(self, context):
    super(OD_LWCopyToExternal, self).__init__()
    self.pidx=0
    self.poidx=0
    self.pointidxmap = {}
    self.polyidxmap = {}

  def fast_point_scan(self, point_list, point_id):
    point_list.append(point_id)
    self.pointidxmap[str(point_id)] = self.pidx
    self.pidx+=1
    return lwsdk.EDERR_NONE

  def fast_poly_scan(self, poly_list, poly_id):
    poly_list.append(poly_id)
    self.polyidxmap[str(poly_id)] = self.poidx
    self.poidx+=1
    return lwsdk.EDERR_NONE

  # LWCommandSequence -----------------------------------
  def process(self, mod_command):

    #deselect any Morph Targets
    command = mod_command.lookup(mod_command.data, "SELECTVMAP")
    cs_options = lwsdk.marshall_dynavalues(("MORF"))
    result = mod_command.execute(mod_command.data, command, cs_options, lwsdk.OPSEL_USER)

    file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"

    #find existing Vmaps
    loaded_weight = []; loaded_uv = []; loaded_morph = []
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_WGHT )):
      loaded_weight.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_WGHT, u))
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_TXUV )):
      loaded_uv.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_TXUV, u))
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_MORF )):
      loaded_morph.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_MORF, u))

    mesh_edit_op = mod_command.editBegin(0, 0, lwsdk.OPLYR_FG)
    if not mesh_edit_op:
      print >>sys.stderr, 'Failed to engage mesh edit operations!'
      return lwsdk.AFUNC_OK

    try:
      # Getting Point ID of selected Point
      points = []
      edit_op_result = mesh_edit_op.fastPointScan(mesh_edit_op.state, self.fast_point_scan, (points,), lwsdk.OPLYR_FG, 0)
      if edit_op_result != lwsdk.EDERR_NONE:
        mesh_edit_op.done(mesh_edit_op.state, edit_op_result, 0)
        return lwsdk.AFUNC_OK
      point_count = len(points)
      edit_op_result = lwsdk.EDERR_NONE


      polys = []
      edit_op_result = mesh_edit_op.fastPolyScan(mesh_edit_op.state, self.fast_poly_scan, (polys,), lwsdk.OPLYR_FG, 0)
      if edit_op_result != lwsdk.EDERR_NONE:
        mesh_edit_op.done(mesh_edit_op.state, edit_op_result, 0)
        return lwsdk.AFUNC_OK
      poly_count = len(polys)
      edit_op_result = lwsdk.EDERR_NONE

      #if there's no points, then we dont need to do anything
      if point_count == 0:
        lwsdk.LWMessageFuncs().info("No Points.", "")
        return lwsdk.AFUNC_OK

      f = open(file, "w")
      f.write ("VERTICES:" + str(point_count) + "\n")

      positions = []
      uvMaps = []
      weightMaps = []
      morphMaps = []
      # Filling Position Array for Selected Point
      for point in points:
        pos = mesh_edit_op.pointPos(mesh_edit_op.state, point)
        f.write(str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]*-1) + "\n")
      #write polygons-point connection for poly reconstruction
      f.write("POLYGONS:" + str(len(polys)) + "\n")
      x =0
      for poly in polys:
        surf = mesh_edit_op.polySurface(mesh_edit_op.state,poly)
        ppoint = ""
        for point in reversed(mesh_edit_op.polyPoints(mesh_edit_op.state,poly)):
          ppoint += "," + str(self.pointidxmap[str(point)])
        polytype = "FACE"
        subD = mesh_edit_op.polyType(mesh_edit_op.state, poly)# & lwsdk.LWPOLTYPE_SUBD
        if subD == lwsdk.LWPOLTYPE_SUBD:
          polytype = "CCSS"
        elif subD == lwsdk.LWPOLTYPE_PTCH:
          polytype = "SUBD"
        f.write(ppoint[1:] + ";;" + surf + ";;" + polytype + "\n")
      #grab all weights
      for weight in loaded_weight:
        mesh_edit_op.vMapSelect(mesh_edit_op.state, weight, lwsdk.LWVMAP_WGHT, 1)
        f.write("WEIGHT:" + weight + "\n")
        for point in points:
          if (mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1]) != None:
            f.write(str(mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1]) + "\n")
          else:
            f.write("0.0\n")
      #grab all UVs
      for uvs in loaded_uv:
        cont = []
        discont = []
        c = 0
        #selecting uv map
        mesh_edit_op.vMapSelect(mesh_edit_op.state, uvs, lwsdk.LWVMAP_TXUV, 2)
        #check whether we are dealing with continuous or discontinous UVs, we have to look at points per poly for this
        for poly in polys:
          for point in mesh_edit_op.polyPoints(mesh_edit_op.state,poly):
            #vpget gets uv coordinates based on point in poly, if that has a value, the uv is discontinuous.. if it doesnt, its continuous.
            pInfo = mesh_edit_op.pointVPGet(mesh_edit_op.state,point, poly)[1]
            if pInfo != None: #check if discontinous
              curPos = [pInfo[0], pInfo[1]]
              #print "oh:", self.polyidxmap[str(poly)]
              discont.append([curPos, str(self.polyidxmap[str(poly)]), str(self.pointidxmap[str(point)])])
              #discont.append([curPos, str(1), str(self.pointidxmap[str(point)])])
              c+= 1
            else: #otherwise, the uv coordinate is continuous
              if mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1] != None:
                curPos = [mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1][0], mesh_edit_op.pointVGet(mesh_edit_op.state, point)[1][1]]
                cont.append([curPos, str(self.pointidxmap[str(point)])])
                c+= 1

        f.write("UV:" + uvs + ":"+str(c) + "\n")
        for uvpos in discont:
          f.write(str(uvpos[0][0]) + " " + str(uvpos[0][1]) + ":PLY:" + str(uvpos[1]) + ":PNT:" + str(uvpos[2]) + "\n")
        for uvpos in cont:
          f.write(str(uvpos[0][0]) + " " + str(uvpos[0][1]) + ":PNT:" + str(uvpos[1]) + "\n")

      #grab all Morphs
      for morph in loaded_morph:
        mesh_edit_op.vMapSelect(mesh_edit_op.state, morph, lwsdk.LWVMAP_MORF, 3)
        f.write("MORPH:" + morph + "\n")
        for point in points:
          if (mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1]) != None:
            ms = mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1]
            f.write(str(ms[0]) + " " + str(ms[1]) + " " + str(ms[2]) + "\n")
          else:
            f.write("None\n")
    except:
      edit_op_result = lwsdk.EDERR_USERABORT
      raise
    finally:
      mesh_edit_op.done(mesh_edit_op.state, edit_op_result, 0)

    f.close()

    return lwsdk.AFUNC_OK


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

    #find existing Vmaps
    loaded_weight = []; loaded_uv = []; loaded_morph = []
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_WGHT )):
      loaded_weight.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_WGHT, u))
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_TXUV )):
      loaded_uv.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_TXUV, u))
    for u in range(0, lwsdk.LWObjectFuncs().numVMaps( lwsdk.LWVMAP_MORF )):
      loaded_morph.append(lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_MORF, u))

    #check if we are in modeler, if so, clear polys
    if cmd == "":
      #Remove Current mesh from layer
      command = mod_command.lookup(mod_command.data, "CUT")
      result = mod_command.execute(mod_command.data, command, None, lwsdk.OPLYR_FG)

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
            #pts.append(points[int(x.strip())])
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

################################################################
#  Layout Surface Extraction geometry                          #
################################################################

class OD_LayoutPasteFromExternal(lwsdk.IGeneric):
  def __init__(self, context):
    super(OD_LayoutPasteFromExternal, self).__init__()
    return

  def process(self, ga):
    lwsdk.command('AddNull ODCopy')
    lwsdk.command('ModCommand_OD_LWPasteFromExternal Layout')
    return lwsdk.AFUNC_OK

ServerTagInfo_OD_LWCopyToExternal = [
  ( "OD_LWCopyToExternal", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
  ( "OD_LWCopyToExternal", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]

ServerTagInfo_OD_LWPasteFromExternal = [
  ( "OD_LWPasteFromExternal", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
  ( "OD_LWPasteFromExternal", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]

ServerTagInfo_OD_LayoutPasteFromExternal = [
  ( "OD_LayoutPasteFromExternal", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
  ( "OD_LayoutPasteFromExternal", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]

ServerRecord = { lwsdk.CommandSequenceFactory("OD_LWPasteFromExternal", OD_LWPasteFromExternal) : ServerTagInfo_OD_LWPasteFromExternal,
                 lwsdk.CommandSequenceFactory("OD_LWCopyToExternal", OD_LWCopyToExternal) : ServerTagInfo_OD_LWCopyToExternal,
                 lwsdk.GenericFactory("OD_LayoutPasteFromExternal", OD_LayoutPasteFromExternal) : ServerTagInfo_OD_LayoutPasteFromExternal }