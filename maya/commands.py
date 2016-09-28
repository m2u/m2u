""" Commands for operating in maya.

"""

# TODO: Delete file

#TODO: remove
def sendSelectedToEdOverwrite():
    """ send selected by exporting them again over their
    AssetPath file and import that again in the Editor.
    This is useful to propagate mesh changes to the Editor.

    If there are objects with the same "AssetPath" but different
    geometry, the user will be asked about them.

    If there are objects without an "AssetPath" the user will
    be asked about them.

    : we might do a file-date check bevor overwrite?
    does that make sense?

    we should replace all geometry in maya of objects with the same
    asset path with the geometry of the new object after the export

    """
    pass

#TODO: remove
def sendSelectedToEdAddMissingOnly():
    """ send selected by telling the editor to add assets with
    "AssetPath" to the level. Do as little exporting and importing
    as possible.

    If one of the objects is not known by the editor, the editor
    will import the file.

    If for one of the objects a file does not exist, it will be
    exported from maya.

    If one of the objects has no "AssetPath", the user will be asked
    about those objects.

    If there are objects that have the same "AssetPath" but differ by
    Geometry, the user will be asked about those objects.

    """
    pass



#TODO: remove
def sendSelectedToEdExportOnly(selectedMeshes):
    """
    there is the special case where there is one type of mesh in the scene
    with edited geometry but an AssetPath pointing to the unedited file
    if the user wants that object to be exported as a new asset and don't
    overwrite the existing asset, (our automation couldn't detect that, because
    all assets with same path have same geometry)
    the user would have to call sendSelectedAsNew in that case?
    Then we would make sure that the user is provided with the UI to change the
    assetPath of those objects on export.
    If the user does not choose sendAsNew, we assume he wants to overwrite any
    files on disk for sure.
    There is also the case where we don't want to export objects that are already
    in the editor, because reimporting takes time, if we didn't change the asset,
    don't ask. Also, we maybe don't want to overwrite files that already are on
    disk, because that takes time.
    We only want to create the map from the objects we have and add those objects
    that we don't have.
    So we need a third option "sendSelectedAddMissingOnly"
    We might intelligently do a check on file-date, import-date in editor
    and maybe a import-date in program for one or the other case to determine
    if a reimport or a file overwrite is necessary or not

    What is the "AssetPath" supposed to be?
    It is the file path, including the file-extension, relative to the current
    projects Art-Source folder. No absolute paths, but that is depending on the
    actual pipeline-implementation, since all functions that deal with
    file paths will be delegated to a pipeline module, and that may be replaced
    by the user.

    1. get selected objects
    2. for each object, get the "AssetPath" attribute
    3. if the object has no such attribute, save it in a untagged list
       if it has, save it in a tagged list entry (filepath:[objects])
    4. for each object in the tagged list, check if the file exists on disk
       fancy: check each object with same file if the gemometry is same
       - if not, tell user that objects with same file path differ and that he should
       export as new.
       - do that by adding all objects with same geometry to a list
       - then ask the user how to rename that asset
       - replace the assetPath value on all assets in that list and add
         them to the tagged unique list
    5. if it does not, export one of the associated objects as asset
    (overwrite any file found)
    6. for each object in the untagged list
       fancy: check all other objects in the untagged list if the geometry is same
       for each where it is same, insert in an association list
       (firstObject:[matchingObjects])
       fancy2: ask the user if the "unique" objects as found are ok,
               if not, he has to split objects into a new "unique" group
       for each first object in that association list
       check if the geometry is the same as in any of the tagged list uniques
       if it is, set the AssetPath attrib on all matching objects to that of the unique
       if it is not, export it as a new Asset and set the AssetPath attrib on
       all matching objects
       add all those to the tagged association list
    7. for each unique object in the tagged list
       tell the editor to import the associated file
    8. for each selected object
       tell the editor to add an actor with the AssetPath as asset
    extend to send lights and stuff like that

    this function will perform something between O(n) and O(n^2) would need to analyze this a little more
    only counting objects... vertex count may be different in scenes, and the heavier
    the vert count, again the heavier the check will be...
    """
