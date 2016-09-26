"""
m2u minimal pipeline

Tasks that operate on the File-System like creating, deleting, checking
files and folders.

"""

import os
import tempfile
import logging

from m2u import settings

_lg = logging.getLogger(__name__)


def get_temp_folder():
    """ Get the Tempdir path from the settings or use the os-default
    if not set in settings file

    """
    tmpdir = tempfile.gettempdir()
    path = settings.get_or_default(
        "General", "Tempdir", tmpdir, write_to_file=False)
    return path


def get_project_export_dir():
    """ Get the base directory for content of the current user's project
    folder. Used when exporting and importing mesh-files.

    """
    default_export_folder = os.path.join(get_temp_folder(), "m2u_export")
    path = settings.get_or_default(
        "General", "ProjectExportDir", default_export_folder,
        write_to_file=False)
    return path
