

#class AssetList(object):
#    pass

class AssetListEntry(object):
    """convenience class to lighten up asset list complexity during export operations
    each AssetListEntry stands for a single asset (assetPath) and all the corresponding
    asset instances (objects). Each instance entry must be a 2tuple of the objects name
    as a string and an optional program-specific reference to the object, provided
    for convenience to simplify followup select-operations etc.
    """
    def __init__(self, assetPath):
        self.assetPath = assetPath
        self.objList = []

    def append(self,t):
        """ expects tuple of (objName, objRef)
        """
        self.objList.append(t)

    def getExportObject(self):
        """return the first object in the list"""
        return self.objList[0]

    def getObjectNamesList(self):
        l = [t[0] for t in self.objList]
        return l

    def getObjectReferencesList(self):
        l = [t[1] for t in self.objList]
        return l
        
        