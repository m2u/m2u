"""
The programs interface file, providing all the functionality external
modules need to know.

The Interface provides the common functionality that the general UI and
other Prorams needs to access. If you provide a custom UI in full or
partially, you may access functionality in submodules instead and
circumvent the interface.

"""

from .connection import *
from .commands import *
from .selection import *
from .visibility import *
from .layers import *
from .assets import *
from . import ui


def get_name():
    return "ue4"


def supports_parenting():
    """Does this Engine support parenting of objects, aka nesting of
    transforms or attaching objects.

    This is important when sending transformation values.
    """
    return False
