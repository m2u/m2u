# All functions in here should have an equivalent of the same name in the maya
# module.__init__.py to make things program-independent

from Py3dsMax import mxs


def setViewFOV( degrees ):
	"""
	Resets the viewport camera FOV to the given value in degrees 
	(or to default value of program	if degrees == `default`)
	"""
	if degrees == "default":
		degrees = 45 # 3ds Max default view FOV	
	mxs.viewport.setFOV( degrees )
	mxs.completeRedraw()

def toggleSync( checkbutton ):
	"""
	Toggles synchronization with UDK on/ff depending on button state.
	"""
	from core import hub
	from max import viewWatcher

	if checkbutton.isChecked(): # sync
		hub.editor.connectToInstance() # editor might change, so keep it general
		viewWatcher.addCallback()
	else: # do not sync
		viewWatcher.removeCallback()


