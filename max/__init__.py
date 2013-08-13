# Max module init
# All functions in here should have an equivalent of the same name in the maya
# module.__init__.py to make things program-independent
import m2u
from Py3dsMax import mxs 

defaultFov = 45 # 3ds Max default view FOV
udkFov = 90 # UDK's default view FOV

def setViewFOV( degrees ):
	"""
	Resets the viewport camera FOV to the given value in degrees 
	(or to default value of program	if degrees == `default`)
	"""
	if degrees == "default":
		global defaultFov
		degrees = defaultFov 	
	elif degrees == "udk":
		global udkFov
		degrees = udkFov
	mxs.viewport.setFOV(degrees)
	mxs.completeRedraw()

def toggleSync( checkbutton ):
	"""
	Toggles synchronization with UDK on/ff depending on button state.
	"""
	from m2u.max import maxGUI
	from m2u.max import viewWatcher
	from m2u.max import objectWatcher

	if checkbutton.isChecked():  # Sync
		editor = m2u.core.getEditor()
		editor.connectToInstance()  # Editor might change, so keep it general

		if checkbutton.text() == "Sync Interactive":
			viewWatcher.addCallback() # interactive sync
			
			# objectWatcher.addCallback()

			viewWatcher.removeTimer()  
			maxGUI.guiInstance.ckbToggleSyncTimebased.setChecked(False)  # Uncheck other btn
			maxGUI.guiInstance.toggleSpinner(False)

		# HOW TO TIME SYNC ONLY WHEN VIEW HAS CHANGED?
		elif checkbutton.text() == "Sync Timebased":
			from m2u.max import maxGUI
			interval = maxGUI.guiInstance.spnInterval.value()
			viewWatcher.addTimer(interval)  # Timed sync

			viewWatcher.removeCallback() 
			maxGUI.guiInstance.ckbToggleSyncInteractive.setChecked(False)  # Uncheck other btn

	else:  # Do not sync
		# Make sure stuff is removed
		viewWatcher.removeCallback() 
		viewWatcher.removeTimer() 

		objectWatcher.removeCallback()
		objectWatcher.removeChangeHandler()


		
		




