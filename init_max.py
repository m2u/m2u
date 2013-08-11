# Called by a macroscript from 3ds Max

import sys, os
baseDir = os.path.join(
	os.path.dirname(os.path.realpath(__file__)), ".."
)
sys.path.append(baseDir)
print "BASEDIR", baseDir
import m2u

def startup():
	# THIS ADDS THEM TO THE GLOBAL SCOPE SO IT CAN BE ACCESSED BY MXS CALLBACKS!
	from m2u.max import viewWatcher
	reload(viewWatcher) # for testing

	from m2u.max import objectWatcher
	reload(objectWatcher) # for testing

	from m2u.core import hub
	reload(hub) # for testing

	hub.initialize("max")

# do it
startup()
