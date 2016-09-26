

class AssetListEntry(object):
    """Convenience class to lighten up asset list complexity during
    export operations.

    Each AssetListEntry stands for a single asset (asset_path) and all
    the corresponding asset instances (objects). Each instance entry
    must be a 2tuple of the objects name as a string and an optional
    program-specific reference to the object - provided for convenience.
    The reference may be used to simplify followup select-operations etc.
    """
    def __init__(self, asset_path):
        self.asset_path = asset_path
        self.obj_list = []

    def append(self, entry):
        """Expects tuple of (obj_name, obj_ref)
        """
        self.objList.append(entry)

    def get_export_object(self):
        # TOOD: better docstring. What is this used for, why use a func
        #   for this?
        """return the first object in the list"""
        return self.obj_list[0]

    def get_object_names_list(self):
        names = [entry[0] for entry in self.obj_list]
        return names

    def get_object_references_list(self):
        references = [entry[1] for entry in self.obj_list]
        return references
