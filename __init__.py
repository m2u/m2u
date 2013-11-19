""" m2u """
import m2u.core

def getVersion():
    return "v0.1"



# recursive reload used for easing up development
from types import ModuleType

def reloadAll():
    reload(m2u.core)
    
    reload(m2u.udk)
    reload(m2u.udk.udkUI)
    reload(m2u.udk.udkCommand)
    reload(m2u.udk.udkParser)
    reload(m2u.udk.udkComposer)
    reload(m2u.udk.udkTypes)
    

def rreload(module):
    """Recursively reload modules.
    
    taken from here: http://stackoverflow.com/questions/15506971/recursive-version-of-reload
    
    """
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if type(attribute) is ModuleType:
            rreload(attribute)
    try:
        reload(module)
    except ImportError as e:
        print e