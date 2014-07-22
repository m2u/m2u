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


A Program Interface provides the following functionality:

General Functionality
---------------------
- getName

Camera
------
- setCameraSyncing
- isCameraSyncing
- setupCamera
- setCameraFOV

Objects
-------
- setObjectSyncing
- isObjectSyncing

"""

# note: import m2u.maya.mayaCommand as _cmd
# will give attribute error on m2u module. strange system
from m2u.maya import mayaCommand as _cmd
from m2u.maya import mayaCamera as _cam
from m2u.maya import mayaObjectTracker as _obj

# -- General --
def getName():
    return "maya"

# -- Camera --
setCameraSyncing = _cam.setCameraSyncing
isCameraSyncing = _cam.isCameraSyncing
setupCamera = _cam.setupCamera
setCameraFOV = _cam.setCameraFOV

# -- Objects --
setObjectSyncing = _obj.setObjectSyncing
isObjectSyncing = _obj.isObjectSyncing

# TODO: move to pipeline file or so
importFile = _cmd.importFile