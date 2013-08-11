# This module is responsible to install/remove a view callback
# and collect the current view transform data when it changes
# so we can sync the UDK view to our 3ds Max view

from Py3dsMax import mxs

syncTimer = None # to stop and delete our timer later

def addCallback():
	"""
	Installs viewportChange callback from the current 3ds Max session
	"""
	mxs.callbacks.addScript(mxs.pyhelper.namify("viewportChange"), "python.exec(\"viewWatcher.syncView()\")", id = mxs.pyhelper.namify("viewWatcher"))
	print "VW: Viewport change callback added"

def removeCallback():
	"""
	Remove viewportChange callback from the current 3ds Max session
	"""
	mxs.callbacks.removeScripts( id = mxs.pyhelper.namify("viewWatcher") )
	print "VW: Viewport change callback removed"

def addTimer(interval):
	"""
	Instead of syncing on view change (using a callback),
	installs a timer that syncs view every given interval
	"""
	from core.repeatTimer import RepeatTimer
	from max import viewWatcher
	global syncTimer
	syncTimer = RepeatTimer( viewWatcher.syncView, interval )
	syncTimer.start()

	print "VW: Timer added"

def removeTimer():
	"""
	Stop and remove the timer to stop sync
	"""
	global syncTimer
	if syncTimer != None:
		syncTimer.stop()
		syncTimer = None

	print "VW: Timer removed"

def getViewData():
	""""
	Gets current viewport transform matrix and returns a list of position and rotation values
	"""
	data = []
	
	vp = mxs.activeViewport
	viewTM = mxs.viewport.getTM()
	# We need to invert 
	inverseViewTM = mxs.Inverse(viewTM)
	
	# MAKE THIS MORE EFFECTIVE; DONT CONVERT TO STRING AND BACK	
	# get rotation data 
	rot = inverseViewTM.rotationPart
	ea_rot_str = str(mxs.execute(str(rot) + " as EulerAngles")) # converting to euler angles
	ea_rot_xyz = ea_rot_str.split(" ")[1:] # split by space and skip "eulerAngles"
	ea_rot_xyz[2] = ea_rot_xyz[2][:-1] # then skip ")" at last element
		
	# order data to match persp view axes
	# default order of data 0-5 is: posX, posY, posZ, rotX, rotY, rotZ
	# http://forums.epicgames.com/threads/712799-Convert-3dsmax-rotation-to-Unreal-Rotation
	# UDK rotation order: pitch(rotY in Max), yaw(rotZ in Max), roll(rotX in Max)
	# pitch and roll are swapedp, and yaw is inverted
	# this works for PERSPECTIVE and CAMERA views, but only when we subtract 90 degrees from the x rotation later
	# the following order can be used for reordering from the default order (see above), 
	# deprecated now as we built up data this way from the start now
	# return [ data[1], data[0], data[2], data[3], -data[5], data[4] ] 
	
	# append position to data list
	data.append(inverseViewTM.position.y)
	data.append(inverseViewTM.position.x)
	data.append(inverseViewTM.position.z)

	# append rotation to data list 
	# TEMP CONVERSION TO UDK ROTATION VALUES HERE (MOVE TO UDKTRANSLATOR THEN)

	# passiert jetz in udkCommand.py
	DegToUnrRot = 182.0444

	# data.append( int( ((float( ea_rot_xyz[0] )) - 90 ) * DegToUnrRot) % 65536 ) 
	# data.append( int( float( ea_rot_xyz[2] ) * -1 * DegToUnrRot) % 65536 ) 
	# data.append( int( float( ea_rot_xyz[1] ) * DegToUnrRot) % 65536 )

	# this had worked a few months ago
	# data.append( (((float( ea_rot_xyz[0] )) - 90 ) * DegToUnrRot) % 65536 ) 
	# data.append( (float( ea_rot_xyz[2] ) * -1 * DegToUnrRot) % 65536 ) 
	# data.append( (float( ea_rot_xyz[1] ) * DegToUnrRot) % 65536 )	

	data.append( (((float( ea_rot_xyz[0] )) - 90 ) * DegToUnrRot) % 65536 ) 
	data.append( (float( ea_rot_xyz[2] ) * -1 * DegToUnrRot) % 65536 ) 
	data.append( (float( ea_rot_xyz[1] ) * DegToUnrRot) % 65536 )

	# print data
	return data

def syncView():
	"""
	Constantly synchronizes the UDK viewport to the 3ds Max viewport when the view changes
	"""
	# Reset FOV if it is wrong in persp mode (may have been changed by orthographic view)
	from m2u import max
	if str(mxs.viewport.getType()) == "view_persp_user" and mxs.viewport.GetFOV() != max.udk_fov:
		max.setViewFOV("udk")

	# Collect view data and send to hub
	from max import viewWatcher
	d = viewWatcher.getViewData()
	from core import hub
	hub.editor.setCamera(d[0], d[1], d[2], d[3], d[4], d[5])

	# print "VW: Synching..."