# All functions in here should have an equivalent of the same name in the maya
# module.__init__.py to make things program-independent

def setViewFOV( degrees ):
	"""
	Resets the viewport camera FOV to the given value in degrees 
	(or to default value of program	if degrees == `default`)
	"""
	if degrees == "default":
		degrees = 45 # 3ds Max default view FOV
	print "Setting 3dsMax Viewport FOV to:", degrees

def toggleSync( checkbutton ):
	"""
	Toggles synchronization with UDK on/ff depending on button state.
	"""
	print "Checkbutton is checked:", checkbutton.isChecked()
