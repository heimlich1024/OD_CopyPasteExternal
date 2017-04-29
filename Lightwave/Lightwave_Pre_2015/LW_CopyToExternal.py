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
__lwver__      = "9.6"

try:
  import lwsdk, os, tempfile, sys
except ImportError:
    raise Exception("The LightWave Python module could not be loaded.")

##########################################################################
#  copys current mesh to temporary file for data exchange                #
##########################################################################

class OD_LWCopyToExternal(lwsdk.ICommandSequence):
  def __init__(self, context):
    super(OD_LWCopyToExternal, self).__init__()

  def fast_point_scan(self, point_list, point_id):
    point_list.append(point_id)
    return lwsdk.EDERR_NONE

  def fast_poly_scan(self, poly_list, poly_id):
    poly_list.append(poly_id)
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
      edit_op_result = mesh_edit_op.fastPolyScan(mesh_edit_op.state, self.fast_point_scan, (polys,), lwsdk.OPLYR_FG, 0)
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
        f.write(str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + "\n")
      #write polygons-point connection for poly reconstruction
      f.write("POLYGONS:" + str(len(polys)) + "\n")
      for poly in polys:
        surf = mesh_edit_op.polySurface(mesh_edit_op.state,poly)
        ppoint = ""
        for point in mesh_edit_op.polyPoints(mesh_edit_op.state,poly):
          ppoint += "," + str(points.index(point))
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
              discont.append([curPos, polys.index(poly), points.index(point)])
              c+= 1
            else: #otherwise, the uv coordinate is continuous
              if mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1] != None:
                curPos = [mesh_edit_op.pointVGet(mesh_edit_op.state,point)[1][0], mesh_edit_op.pointVGet(mesh_edit_op.state, point)[1][1]]
                cont.append([curPos, points.index(point)])
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


ServerTagInfo_OD_LWCopyToExternal = [
  ( "OD_LWCopyToExternal", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
  ( "OD_LWCopyToExternal", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]

ServerRecord = { lwsdk.CommandSequenceFactory("OD_LWCopyToExternal", OD_LWCopyToExternal) : ServerTagInfo_OD_LWCopyToExternal }