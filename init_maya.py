# maya startup file, called by a shelf button or so
# will initialize the system to use the maya program modules
# and create the UI attached to maya

import m2u

m2u.core.initialize("maya")

# create UI here, send the initialized m2u module to the ui

#createUI(m2u)