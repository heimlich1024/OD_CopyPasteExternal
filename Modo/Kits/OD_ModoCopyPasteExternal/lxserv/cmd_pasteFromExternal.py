################################################################################
#
# cmd_pasteFromExternal
#
# Author: Oliver Hotz | Chris Sprance
#
# Description: Pastes Geo/Weights/Morphs/UV's from external file
#
# Last Update:
#
################################################################################

import lx
import lxifc
import lxu.command
from od_copy_paste_external import paste_from_external


class ODPasteFromExternal(lxu.command.BasicCommand):

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
        reload(paste_from_external)
        paste_from_external.execute()

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(ODPasteFromExternal, "OD_PasteFromExternal")
