"""
m2u minimal pipeline

This module contains the necessary pipeline tasks for m2u to function correctly.
These are mainly operations on the file-system.

There are also Program- and maybe Editor- specific pipeline tasks, which will
reside in their own modules, but are referenced through here.

The minimal pipeline is a simple implementation of only the necessary tasks.
The pipeline module can be replaced as long as you provide the required interface
for m2u. To strap your own pipeline into m2u, set the "[General] PipelineModule"
value in the settings file to point to your pipelines interface-module for m2u.
(make sure it is on the python-path)
Alternatively you can overwrite the _initPipeline() function in core.py or load
m2u from within your pipeline and do the whole initialization yourself.

"""

import os
import m2u
from m2u.pipeline import pipeFileSystem as _fs

getTempFolder = _fs.getTempFolder
getProjectExportDir = _fs.getProjectExportDir

def makeSurePathExists(path):
    # http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
    if not os.path.exists(path):
        try: 
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise


def getFBXSettingsFile():
    """ return the fbx-settings file path for the current used editor
    """
    ed = m2u.core.getEditor()
    eddir = os.path.abspath(ed.__file__)
    eddir = os.path.dirname(eddir)
    return eddir+"/ue4FBXSettings.fbxexportpreset"


def getSpecificPipelineFor(programName):
    """ returns a module with program-specific pipeline tasks for the given
    program.

    Program-specific pipeline tasks are importing and exporting of files,
    adding attributes to objects etc.

    """

    pass