# 

class ObjectInfo(object):
    """
    General description of a typical GameObject in 3D Space
    Meshes, Cameras, Particle Effects, Lights etc.
    """
    
    def __init__(self, name, pos, rot, scale, attrs):
        """
        
        Arguments:
        - `name`: string, name of the object
        - `pos`: 3d tuple
        - `rot`: 3d tuple
        - `scale`: 3d tuple
        - `attrs`: dictionary with name:value pairs for additional attributes
        """
        self._name = name
        self._pos = pos
        self._rot = rot
        self._scale = scale
        self._attrs = attrs
        
