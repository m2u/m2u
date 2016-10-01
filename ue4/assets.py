""" Import and export commands for assets.

"""

import os
import logging

from m2u import core
from m2u import pipeline
from . import connection

_lg = logging.getLogger(__name__)


def fetch_selected_objects():
    """ Fast-fetch all selected actors by exporting them into an
    FBX-File and importing that file into the Program.
    Only one file containing all objects is created.
    This should not be used for creating reusable assets!

    """
    path = pipeline.get_temp_folder()
    path = os.path.join(path, "m2uTempExport.fbx")

    msg = ("FetchSelected \""+path+"\"")
    result = connection.send_message(msg)
    core.program.import_file(path)


def import_assets_batch(rel_file_path_list):
    """ Import all the asset files in the list the files paths have to
    be relative to the current  project's content_root.

    This function will create a matching destination path for each
    file path.

    """
    if len(rel_file_path_list) < 1:
        return

    msg = 'ImportAssetsBatch'
    content_root = pipeline.get_project_export_dir()
    for path in rel_file_path_list:
        if not path.startswith("/") and len(path) > 0:
            path = "/"+path

        filepath = content_root + path
        directory = os.path.dirname(path)
        # The import destination has to be without the asset-name.
        # It will be auto-generated from the file-name by UE4.

        asset_path = "/Game" + directory.replace("\\", "/")
        asset_path = asset_path.replace("//", "/")
        if asset_path.endswith("/"):
            asset_path = asset_path[:-1]

        msg = msg + ' "' + asset_path + '" "' + filepath + '"'
    result = connection.send_message(msg)
