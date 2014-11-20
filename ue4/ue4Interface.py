"""
the programs interface file, providing all the functionality external modules
need to know.

You might expect to find the content of this file directly in the __init__ file
of the package instead. But __init__ is a stupid name and package layout might
change. Instead __init__ will import everything from this file.

The Interface may be split up into "from" and "to" separate files, but that
depends on the ammount of stuff herein.

The Interface provides the common functionality that the general UI and other
Prorams needs to access. If you provide a custom UI in full or partially,
you may access functionality in submodules instead and circumvent the Interface.

"""

from m2u.ue4 import ue4Conn as _u
from m2u.ue4 import ue4Command
from m2u.ue4 import ue4Selection as _s #selection
from m2u.ue4 import ue4Command as _a #editing
from m2u.ue4 import ue4Visibility as _v #visibility
from m2u.ue4 import ue4Command as _c #other commands
from m2u.ue4 import ue4Layer as _l #layer
from m2u.ue4 import ue4Export
from m2u.ue4 import ue4Import as _i

# the ue4 ui module, referenced by other modules through here!
from m2u.ue4 import ui

# -- General --
def getName():
    return "UE4"

def supportsParenting():
    """ if this Engine supports parenting of objects
    aka nesting of transforms or attaching
    """
    # TODO: parenting, enable when I've got an option for empty transforms in UE4
    return False


# TODO: maybe this shouldn't be necessary
# instead it would be better if all functions that generally could
# be batch-operations always take a list. If the specific engine-implementation
# cannot operate on lists, it must go through the list in the python function
# and call the single-shot function internally for each list item
def supportsBatchOperations():
    """ if this Engine-implementation supports function that
    operate on lists of objects, for example duplicating multiple
    objects at once.
    """
    return True

# TODO: move those things to pipeline-files maybe?
importAssetsBatch = _i.importAssetsBatch
addActorBatch = _c.addActorBatch

connectToInstance = _u.connectToUEd
disconnect = _u.closeConnection

# -- Selection --
selectByNames = _s.selectByNames
deselectAll = _s.deselectAll
#deselectByNames = _s.deselectByNames

# -- editing --
transformObject = _a.transformObject
deleteSelected = _a.deleteSelected
#duplicateSelected = _a.duplicateSelected
renameObject = _a.renameObject
#insertNewObject = _a.insertNewObject
duplicateObject = _a.duplicateObject
deleteObject = _a.deleteObject
parentChildTo = _a.parentChildTo

# -- Visibility --
hideSelected = _v.hideSelected
unhideSelected = _v.unhideSelected
isolateSelected = _v.isolateSelected
unhideAll = _v.unhideAll
hideByNames = _v.hideByNames
#unhideByNames = _v.unhideByNames

# -- Layer --
addObjectsToLayer = _l.addObjectsToLayer
removeObjectsFromAllLayers = _l.removeObjectsFromAllLayers
renameLayer = _l.renameLayer
deleteLayer = _l.deleteLayer
hideLayer = _l.hideLayer
unhideLayer = _l.unhideLayer

# -- Camera --
transformCamera = _c.transformCamera

# -- Other --
undo = _c.undo
redo = _c.redo
getFreeName = _c.getFreeName