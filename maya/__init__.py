"""
The programs interface file, providing all the functionality external
modules need to know.

The interface provides the common functionality that the general UI and
other modules needs to access. If you provide a custom UI in full or
partially, you may access functionality in submodules instead and
circumvent the interface.

"""

from . import ui
from .cameras import (
    set_camera_syncing, is_camera_syncing, set_fov
)
from .objects import (
    set_object_syncing, is_object_syncing
)
from .visibility import (
    set_visibility_syncing, is_visibility_syncing
)
from .layers import (
    set_layer_syncing, is_layer_syncing
)
from .exporting import (
    ExportOperation
)
from .importing import (
    import_file
)


def get_name():
    return "maya"
