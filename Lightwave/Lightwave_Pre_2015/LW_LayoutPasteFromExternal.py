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

ServerTagInfo_OD_LayoutPasteFromExternal = [
  ( "OD_LayoutPasteFromExternal", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
  ( "OD_LayoutPasteFromExternal", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]

ServerRecord = { lwsdk.GenericFactory("OD_LayoutPasteFromExternal", OD_LayoutPasteFromExternal) : ServerTagInfo_OD_LayoutPasteFromExternal }