# max module init
# All functions in here should have an equivalent of the same name in the maya
# module.__init__.py to make things program-independent

from Py3dsMax import mxs 

default_fov = 45 # 3ds Max default view FOV
udk_fov = 90 # UDK's default view FOV

def setViewFOV( degrees ):
	"""
	Resets the viewport camera FOV to the given value in degrees 
	(or to default value of program	if degrees == `default`)
	"""
	if degrees == "default":
		global default_fov
		degrees = default_fov 	
	elif degrees == "udk":
		global udk_fov
		degrees = udk_fov
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

		if checkbutton.text() == "Sync Interactive":
			viewWatcher.addCallback() # interactive sync

		# HOW TO TIME SYNC ONLY WHEN VIEW HAS CHANGED?
		elif checkbutton.text() == "Sync Timebased":
			viewWatcher.addTimer( 0.000001 ) # timed sync

	else: # do not sync
		# make sure stuff is removed
		viewWatcher.removeCallback() # interactive sync
		viewWatcher.removeTimer() # timed sync


		
		




