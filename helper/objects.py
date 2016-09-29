

class ObjectInfo(object):
    """
    General description of a typical Game Object in 3D Space
    Meshes, Cameras, Particle Effects, Lights etc.

    """

    def __init__(self, name, type_internal, type_common,
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), attrs={}):
        """
        Arguments:
        - `name`: string, name of the object
        - `type_internal`: string
        - `type_common`: string
        - `pos`: 3d tuple
        - `rot`: 3d tuple
        - `scale`: 3d tuple
        - `attrs`: dictionary with name:value pairs for additional attributes
        """
        self.name = name
        self.type_common = type_common
        self.type_internal = type_internal
        self.position = pos
        self.rotation = rot
        self.scale = scale
        self.asset_path = ''
        self.attrs = attrs


class ComponentInfo(object):
    """
    """

    def __init__(self, name, type_internal):
        """
        Arguments:
        - `name`:
        - `type_internal`:
        """
        self.name = name
        self.type_internal = type_internal
