"""
this is the simple fallback-ui for maya for the case that no PySide is installed.
It should provide the common functionality but I won't invest much time into
layout.

This UI is mainly used for testing and may do stuff that Editor-specific UI parts
would do in a regular (PyQt or PySide based) UI.
This UI may contain UE4 specific code!

"""

import pymel.core as pm
import m2u

def cbConnect(*args):
    m2u.core.getEditor().connectToInstance()

def cbSetupCamera(*args):
    m2u.core.getProgram().setupCamera()

def cbSyncCamera(*args):
    m2u.core.getProgram().setCameraSyncing(True)

def cbSyncCameraOff(*args):
    m2u.core.getProgram().setCameraSyncing(False)

def cbSyncObjects(*args):
    m2u.core.getProgram().setObjectSyncing(True)

def cbSyncObjectsOff(*args):
    m2u.core.getProgram().setObjectSyncing(False)

def cbSyncVisibility(*args):
    m2u.core.getProgram().setVisibilitySyncing(True)

def cbSyncVisibilityOff(*args):
    m2u.core.getProgram().setVisibilitySyncing(False)

def cbSyncLayers(*args):
    m2u.core.getProgram().setLayerSyncing(True)

def cbSyncLayersOff(*args):
    m2u.core.getProgram().setLayerSyncing(False)

def cbFetchSelected(*args):
    # this is circumventing the interface
    #m2u.maya.mayaCommand.fetchSelectedObjectsFromEditor()
    m2u.core.getEditor().ue4Export.fetchSelectedObjects()

def cbSendSelectedToEd(*args):
    m2u.core.getProgram().mayaCommand.sendSelectedToEd()

def cbSendSelectedToEdExportOnly(*args):
    m2u.core.getProgram().mayaCommand.sendSelectedToEdExportOnly()
    
def cbUDKImportContent(*args):
    m2u.udk.udkUI.callImportContent("C:\\temp\\mp7_compact_export.fbx",None)

m2uwin = None
def createUI():
    global m2uwin
    if m2uwin is not None:
        pm.deleteUI(m2uwin, window=True)
        m2uwin = None
    
    v = m2u.getVersion()
    m2uwin = pm.window( title="m2u "+v+" (maya)", iconName='m2u',
                        widthHeight=(150, 300) )
    pm.columnLayout()
    pm.rowLayout(numberOfColumns = 2)
    pm.button( label='Connect', c=cbConnect )
    pm.button( label='Setup Cameras', c=cbSetupCamera )
    pm.setParent('..')
    pm.checkBox( label='Sync Camera', onc = cbSyncCamera,
                 ofc = cbSyncCameraOff, v = False)
    pm.checkBox( label='Sync Objects', onc = cbSyncObjects,
                 ofc = cbSyncObjectsOff, v = False)
    pm.checkBox( label='Sync Visibility', onc = cbSyncVisibility,
                 ofc = cbSyncVisibilityOff, v = False)
    pm.checkBox( label='Sync Layers', onc = cbSyncLayers,
                 ofc = cbSyncLayersOff, v = False)
    pm.separator()
    pm.button( label='Fetch Selected', c = cbFetchSelected)
    pm.button( label='Send Selected To Editor', c = cbSendSelectedToEd)
    pm.button( label='Export Selected To Editor', c = cbSendSelectedToEdExportOnly)
    #pm.button( label='Import Content Test', c = cbUDKImportContent)
    pm.setParent( '..' )
    pm.showWindow( m2uwin )