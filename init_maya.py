# maya startup file, called by a shelf button or so
# will initialize the system to use the maya program modules
# and create the UI attached to maya

from core import hub;

def startup():
    hub.initialize("maya");


# do it
startup();
