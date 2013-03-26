# This module is responsible to install/remove a selectionSetChanged callback
# and collect PRS data from objects that have been moved, where movement
# is detected using changehandlers. Then sync that with objects in the UDK

# VLLT AUCH EINFACH PER BUTTON ODER MOUSE UP RUEBERSCHICKEN
# OHNE CHANGE HANDLER ODER EIN CHANGE HANDLER FUER AKTUELLE SELEKTION
# SODASS EGAL IST WELCHES OBJEKT VERAENDERT WURDE
# AUCH AN SIMULATION DENKEN WO WAHRSCHEINLICH DER CHANGE HANDLER NICH ANSPRINGEN WUERDE

from Py3dsMax import mxs


# only keep one changehandler for the current selection as a whole
# we need to keep reference to dismiss properly
changeHandler = None 


def addCallback():
	mxs.callbacks.addScript(mxs.pyhelper.namify("selectionSetChanged"), "python.exec(\"objectWatcher.addChangeHandler()\")", id = mxs.pyhelper.namify("objectWatcher"))
	print "OW: Callback added"
	# apply an initial changeHandler to the current selection:
	from max import objectWatcher
	objectWatcher.addChangeHandler()

def removeCallback():
	mxs.callbacks.removeScripts(mxs.pyhelper.namify("selectionSetChanged"), id = mxs.pyhelper.namify("objectWatcher"))
	print "OW: Callback removed"

def onChanged():
	""" Called by changehandlers from 3ds Max """
	getObjectData()

def getObjectData():
	print "OW: Changehandler triggered"
	# it collects the transform data of the objects in selection
	pass

def addChangeHandler():
	""" Adds changehandler to the current selection in 3ds Max """
	# first, reset list
	from max import objectWatcher
	objectWatcher.removeChangeHandler()
	# # add one changehandler for the whole selection to detect transform changes
	# # changeHandler = mxs.execute( "when transform selection changes handleAt:#redrawViews obj do ( python.exec(\"objectWatcher.onChanged( obj )\"))" )
	if len(mxs.selection) > 0:
		global changeHandler
		changeHandler = mxs.execute( "when transform selection changes handleAt:#redrawViews do ( python.exec(\"objectWatcher.onChanged()\"))" )
		print "OW: Adding change handler to selection"
	else:
		print "OW: Nothing selected, no changehandler added"

def removeChangeHandler():
	""" Removes changehandlers from prior selection in 3ds Max """
	global changeHandler
	if changeHandler != None:
		mxs.deleteChangeHandler(changeHandler)
		print "OW: Deleting changehandler"

def syncObjects():
	pass
"""
# uses static methods
class ObjectWatcher(Watcher):
	
	# we need to keep changehandler references to dismiss them properly
	changeHandlers = [] # static attribute
	
	# most methods here are static so we dont need to know the instance to use the functionality
	# BUT we use the constructor to "initialize" the selectionSetChanged callback
	def __init__(self):
		Watcher.__init__(self)		
		# delete all prior callbacks by id (need namify helper cause we cant write # for callback name and id)
		mxs.callbacks.removeScripts(mxs.pyhelper.namify("selectionSetChanged"), id = mxs.pyhelper.namify("objectWatcher"))
		# install selectionChanged callback
		# we cannot (afaik) define our python function as a global mxs function, which is what the callback expects
		# so instead we make it a static python function, that can then be called from the callback
		mxs.callbacks.addScript(mxs.pyhelper.namify("selectionSetChanged"), "python.exec(\"ObjectWatcher.addChangeHandlersToSelected()\")", id = mxs.pyhelper.namify("objectWatcher"))
		print "selectionSetChanged callback installed"
		
	# called to reset changehandler list at refresh and deletion
	def removeChangeHandlers():
		for ch in ObjectWatcher.changeHandlers:
			mxs.removeChangeHandler(ch)
	removeChangeHandlers = staticmethod(removeChangeHandlers)
		
	# called by changehandlers
	def sendObjectData():
		print ("data will be sent")
		# it collects the transform data of the object is has been triggered from
		# and sends it to the "Core" <-- need to find a standardization for the format
	sendObjectData = staticmethod(sendObjectData)	
		
	# define function that is called on selection change
	def addChangeHandlersToSelected():
		print "adding change handlers"
		# first, reset list
		ObjectWatcher.removeChangeHandlers()
		# assign a changehandler to each selected object and add the reference to our list
		sel = mxs.selection 
		for o in sel:
			ch = mxs.execute( "when transform selection[1] changes handleAt:#redrawViews obj do ( python.exec(\"ObjectWatcher.sendObjectData( obj )\"))" )
		
			
		# maybe add some kind of class check, e.g. only geometry objects
		# the changehandlers then call some other function below
	# make this a STATIC method to be used without needing an instance of its class
	addChangeHandlersToSelected = staticmethod(addChangeHandlersToSelected) 
	
	def __del__(self):
		# on object deletion, make sure all depending changehandlers are removed from the 3ds Max scene
		self.removeChangeHandlers()
		# remove callbacks by id
		mxs.callbacks.removeScripts( id = mxs.pyhelper.namify("objectWatcher") )
		"""