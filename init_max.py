# max startup file, called by a macroscript
# will initialize the system to use the max program modules
# and create the UI attached to max

# needed to work when triggered from max wtf??
import sys
sys.path.append( r"C:\Users\Christoph\Desktop\Unreal Level Builder\m2u" ) # our modules
sys.path.append( r"C:\Python26\Lib\site-packages" ) # to get blurdev stuff

from core import hub

def startup():
    hub.initialize("max")

# do it
startup()

