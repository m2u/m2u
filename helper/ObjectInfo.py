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
        self.name = name
        self.position = pos
        self.rotation = rot
        self.scale = scale
        self.attrs = attrs
        
