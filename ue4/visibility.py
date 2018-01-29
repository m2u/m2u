"""Commands for object visibility.

"""

import logging

from . import connection

_lg = logging.getLogger(__name__)


def hide_selected():
    """Hide currently selected objects."""
    msg = "HideSelected"
    return connection.send_message(msg)


def unhide_selected():
    """Show currently selected objects."""
    msg = "UnhideSelected"
    return connection.send_message(msg)


def isolate_selected():
    """Hide all but the currently selected objects."""
    msg = "IsolateSelected"
    return connection.send_message(msg)


def unhide_all():
    """Show all hidden objects."""
    msg = "UnhideAll"
    return connection.send_message(msg)


def hide_by_names(names_list):
    """Hide all objects in the names_list."""
    msg = "HideByNames " + " ".join(names_list)
    return connection.send_message(msg)


def unhide_by_names(names_list):
    """Show all objects in the names_list."""
    msg = "UnhideByNames " + " ".join(names_list)
    return connection.send_message(msg)
