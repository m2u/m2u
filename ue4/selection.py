
import logging
from . import connection

_lg = logging.getLogger(__name__)


def select_by_names(names_list):
    """Add objects to the current selection."""
    names = "[" + (','.join(names_list)) + "]"
    msg = "SelectByNames " + names
    connection.send_message(msg)


def deselect_all():
    """Clear the current selection."""
    connection.send_message("DeselectAll")


def deselect_by_names(names_list):
    """Remove objects from the current selection."""
    names = "[" + (','.join(names_list)) + "]"
    msg = "DeselectByNames " + names
    connection.send_message(msg)
