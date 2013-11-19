# 

class ObjectInfo(object):
    """
    General description of a typical Game Object in 3D Space
    Meshes, Cameras, Particle Effects, Lights etc.
    
    """
    
    def __init__(self, name, typeInternal, typeCommon, pos=(0,0,0), rot=(0,0,0),
                 scale=(1,1,1), attrs={}):
        """       
        Arguments:
        - `name`: string, name of the object
        - `typeInternal`: string
        - `typeCommon`: string
        - `pos`: 3d tuple
        - `rot`: 3d tuple
        - `scale`: 3d tuple
        - `attrs`: dictionary with name:value pairs for additional attributes
        """
        self.name = name
        self.typeCommon = typeCommon
        self.typeInternal = typeInternal
        self.position = pos
        self.rotation = rot
        self.scale = scale
        self.attrs = attrs
        

class ComponentInfo(object):
    """
    """
    
    def __init__(self, name, typeInternal):
        """ 
        Arguments:
        - `name`:
        - `typeInternal`:
        """
        self.name = name
        self.typeInternal = typeInternal
