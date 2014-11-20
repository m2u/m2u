import re

from systemHelper import *

def removeNumberSuffix(name):
    g = re.match("(.+?)(\d*)$",str(name))
    rawName = g.group(1)
    return rawName