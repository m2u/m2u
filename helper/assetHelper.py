

class AssetListEntry(object):
    """Convenience class to lighten up asset list complexity during
    export operations.

    Each AssetListEntry stands for a single asset (asset_path) and all
    the corresponding asset instances (objects). Each instance entry
    is stored as a 2-tuple of the objects name as a string and an
    optional program-specific reference to the object - provided for
    convenience.

    The reference may be used to simplify followup select-operations etc.

    The "AssetPath" is supposed to be the file path, including the
    file-extension, relative to the current projects Art-Source
    folder. No absolute paths, but that is depending on the actual
    pipeline-implementation, since all functions that deal with file
    paths will be delegated to a pipeline module, and that may be
    replaced by the user.

    """
    def __init__(self, asset_path):
        self.asset_path = asset_path
        self.obj_list = []

    def append(self, obj_name, obj_ref=None):
        """Add an instance-entry for this asset.

        Args:
            obj_name (str): Name of the instance node.
            obj_ref: A program-specific reference to the object, which
                can be used to easily access the object again later.
        """
        self.obj_list.append((obj_name, obj_ref))

    def get_export_object(self):
        """Get the instance-entry that should be used to export the
        geometry of this asset.

        This is simply the first entry in the list.
        """
        try:
            return self.obj_list[0]
        except IndexError:
            return None

    def get_object_names_list(self):
        names = [entry[0] for entry in self.obj_list]
        return names

    def get_object_references_list(self):
        references = [entry[1] for entry in self.obj_list]
        return references
