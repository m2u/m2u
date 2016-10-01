"""
m2u minimal pipeline

This module contains the necessary pipeline tasks for m2u to function
correctly.
These are mainly operations on the file-system.

There are also Program- and maybe Editor- specific pipeline tasks,
which will reside in their own modules, but are referenced through here.

The minimal pipeline is a simple implementation of only the necessary
tasks. The pipeline module can be replaced as long as you provide the
required interface for m2u. To strap your own pipeline into m2u, set
the "[General] PipelineModule" value in the settings file to point to
your pipelines interface-module for m2u.
(make sure it is on the python-path)
Alternatively you can overwrite the init_pipeline() function in core.py
or load m2u from within your pipeline and do the whole initialization
yourself.

"""

import os

import m2u
from .filesystem import (
    get_temp_folder, get_project_export_dir, make_sure_path_exists
)


def get_fbx_settings_file_path():
    """ Get the fbx-settings file path for the currently used editor.
    """
    # TODO: move to editor-specific pipeline file
    editor = m2u.core.editor
    editor_dir = os.path.dirname(os.path.abspath(editor.__file__))
    fbxpresetpath = os.path.join(editor_dir, "ue4FBXSettings.fbxexportpreset")
    return fbxpresetpath


def get_specific_pipeline_for_program(program_name):
    """ Get the module with program-specific pipeline tasks for the
    given program.

    Program-specific pipeline tasks are importing and exporting of files,
    adding attributes to objects etc.

    """
    # TODO: implement program and editor specific pipeline modules
