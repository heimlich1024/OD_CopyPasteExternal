################################################################################
#
# cmd_copyToExternal.py
#
# Author: Oliver Hotz | Chris Sprance
#
# Description: Copies Geo/Weights/Morphs/UV's to External File
#
# Last Update:
#
################################################################################

import lx
import lxifc
import lxu.command
from od_copy_paste_external import copy_to_external


class ODCopyToExternal(lxu.command.BasicCommand):

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        # TODO: Disable reload for release
        reload(copy_to_external)
        copy_to_external.execute()

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(ODCopyToExternal, "OD_CopyToExternal")
