#
# this is the simple fallback-ui for maya for the case that no pyQt is installed
# it should provide the common functionality but I won't invest much time into layout

import pymel.core as pm
import m2u

def cbConnect(*args):
    m2u.core.getEditor().connectToInstance()

def cbSetupCamera(*args):
    m2u.core.getProgram().setupCamera()

def cbSyncCamera(*args):
    m2u.core.getProgram().setCameraSyncing(True)

def cbSyncObjects(*args):
    m2u.core.getProgram().setObjectSyncing(True)

def createUI():
    m2uwin = pm.window( title="m2u maya", iconName='m2u', widthHeight=(100, 400) )
    pm.columnLayout()
    pm.button( label='Connect', c=cbConnect )
    pm.button( label='Setup Cameras', c=cbSetupCamera )
    pm.button( label='Sync Camera', c = cbSyncCamera)
    pm.button( label='Sync Objects', c = cbSyncObjects)
    pm.setParent( '..' )
    pm.showWindow( m2uwin )