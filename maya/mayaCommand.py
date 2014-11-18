# maya commands, will maybe divided into several files, we will see

#print "maya command importing"

import time
import os

import pymel.core as pm
import pymel.api as mapi

import m2u
import m2u.helper as helper
#from m2u.maya import mayaObjectTracker
from m2u.helper.ObjectInfo import ObjectInfo


from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

RADIAN_TO_DEGR = 57.2957795
DEGR_TO_RADIAN = 0.0174532925

#note: using the following two functions in script jobs would require the full
# path to be specified, since we will eventually move them to udkCommand anyway,
# the functionality is currently inlined into the sj-functions
def rotationMayaToUDK(r):
    # udk has a different rotation order (ZXY), so we transform the stuff here
    global RADIAN_TO_DEGR
    global DEGR_TO_RADIAN
    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN, ry*DEGR_TO_RADIAN,
                               rz*DEGR_TO_RADIAN)
    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
    return rx,-ry,-rz

def translationMayaToUDK(t):
    tx,ty,tz = t
    return -tz,tx,ty #maya y-up
    #return tx,-ty,tz #maya z-up
    #return tx,tz,ty #maya y-up to udk-fbx-z-up?


# TODO: move this function to a program-specific pipeline module
# maybe it has to be split in one that is m2u specific and one that
# can be generalized (the importing itself, while still disabling m2u-syncing)
# on the other hand, if somebody provides his own pipeline for m2u, they
# should be able to do this from within those functions too.
def importFile(path):
    """ simply imports an FBX-file
    
    """
    prog = m2u.core.getProgram()
    # disable object tracking, because importing FBX files will cause
    # a lot of renaming and we don't want that to produce warnings
    wasSyncing = prog.isObjectSyncing()
    prog.setObjectSyncing(False)

    cmd = "FBXImport -f \""+ path.replace("\\","/") +"\""
    pm.mel.eval(cmd)

    prog.setObjectSyncing(wasSyncing) # restore syncing state


#def importAsset()
#def referenceAsset ??


# TODO: remove this function or move to UDK specific file
# it is UDK specific, ue4 uses another function.
# fetching is an editor-task, where the editor tells the program
# to import the fetched file, when it is done writing.
def fetchSelectedObjectsFromEditor():
    """ tell UDK to export the selected objects into a temporary FBX file
    and then maya will import that file.
    
    """
    ed = m2u.core.getEditor()
    prog = m2u.core.getProgram()
    path = m2u.core.getTempFolder()
    path = path + "\m2uTempExport.fbx"
    if os.path.exists(path):
        os.remove(path) # make sure there will be no "overwrite" warning from UEd
    # this is circumventing the interface!
    ed.udkCommand.exportSelectedToFile(path,False)
    status = helper.waitForFileToBecomeAvailable(path)
    if not status:
        _lg.error("Unable to import file: "+path)
        return

    # disable object tracking, because importing FBX files will cause
    # a lot of renaming and we don't want that to produce warnings
    wasSyncing = prog.isObjectSyncing()
    prog.setObjectSyncing(False)

    cmd = "FBXImport -f \""+ path.replace("\\","\\\\") +"\""
    pm.mel.eval(cmd)

    prog.setObjectSyncing(wasSyncing) # restore syncing state


# TODO: move to maya-specific pipeline file
def exportObjectAsAsset(name, path):
    """ export object `name` to FBX file specified by `path`
    
    :param name: objects name (name of the tranfsorm node)
    :param path: file path with extension, RELATIVE to the content root

    """
    pipe = m2u.core.getPipeline()
    contentRoot = pipe.getProjectExportDir()
    lpath,ext = os.path.splitext(path)
    if ext != ".fbx":
        ext = ".fbx"
    fullpath = contentRoot+"/"+lpath+ext
    exportObjectCentered(name, fullpath, center=True)


identity = [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]
# TODO: move to maya-specific pipeline-file
def exportObjectCentered(name, path, center=True):
    """ export object `name` to FBX file specified by `path`
    
    :param name: objects name
    :param path: ABSOLUTE file path for the fbx file
    :param center: object transformation will be reset before export

    """
    prog = m2u.core.getProgram()
    wasSyncing = prog.isObjectSyncing()
    prog.setObjectSyncing(False) # so our move command won't be reflected in Ed

    pm.select(name, r=True)
    if center:
        mat = pm.xform(query=True, ws=True, m=True) # backup matrix
        piv = pm.xform (name, piv=True, q=True, ws=True) # backup pivot
        pm.xform(name, a=True, ws=True, m = identity)
        #pm.makeIdentity(name)

    exportSelectedToFBX(path)

    if center:
        pm.xform(name, a=True, ws=True, m=mat) # reset matrix
        pm.xform(name, ws=True, piv=(piv[0], piv[1], piv[2])) # reset pivot

    prog.setObjectSyncing(wasSyncing) # restore syncing state


# TODO: move to maya-specific pipeline-file
def exportSelectedToFBX(path):
    """ export selection to file specified by `path`

    fbx settings will be set from preset file
    """
    if os.path.exists(path):
        os.remove(path)
    # TODO: fbxExportPreset should be Editor-specific
    sfpath = m2u.core.getPipeline().getFBXSettingsFile()
    _lg.debug("settings file path is: "+sfpath)
    lsfcmd = "FBXLoadExportPresetFile -f \"%s\";" % sfpath.replace("\\","/")
    pm.mel.eval(lsfcmd)
    _lg.debug("Exporting File: "+path)
    # maya's FBX command is not able to create directories, so we let python do that
    directory = os.path.dirname(path)
    m2u.core.getPipeline().makeSurePathExists(directory)
    expcmd = "FBXExport -f \"%s\" -s;" % path.replace("\\","/")
    pm.mel.eval(expcmd)



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

def sendSelectedToEdAsNew():
    """ send selected as new assets.
    This will ignore any "AssetPath" attribute on the objects
    and instead ask the user how to name the new object(s).

    Objects will be grouped by shared properties like vertex-count and uv-count.
    The UI should give the user the option to seperate that auto-collection again.

    """
    # the most simple approach for now is to empty the "AssetPath" attribute
    # on all the selected objects and call sendSelectedToEd. The automation
    # will then do what we want. (as soon as it checks for existing files)
    # TODO: integrate that functionality in the sendSelecteToEd function, because
    # that will loop over all selected objects anyway.
    selectedObjects = pm.selected(type="transform")

    pass



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
    
    #selectedMeshes = getSelectedMeshes()
    
    #2. for each object get the "AssetPath" attribute
    untaggedList = list()
    taggedDict = {}
    for obj in selectedMeshes:
        if obj.hasAttr("AssetPath"):
            assetPathAttr = obj.attr("AssetPath")
            assetPathValue = assetPathAttr.get()
            if len(assetPathValue)>0:
                taggedDict.setdefault(assetPathValue,[]).append(obj)
            else:
                # if the ass path is empty, that is equal to the attr not being there
                untaggedList.append(obj)
        else:
            # unknown asset, we will handle those later
            untaggedList.append(obj)
    _lg.debug("found %i untagged" % len(untaggedList))
    _lg.debug("found %i tagged" % len(taggedDict))
    
    #3. do the geometry check for tagged objects
    #   this assembles the taggedUniqueDict
    taggedDiscrepancyDetected = False
    taggedUniqueDict = {}
    for lis in taggedDict.values():
        #for obj in lis: #we modify lis, so iterator won't work
        while len(lis)>0: # use while instead
            obj = lis[0]
            taggedUniqueDict[obj]=[]
            # compare this object against all others in the list.
            for otherObj in lis[1:]:
                if 0 == pm.polyCompare(obj, otherObj, vertices=True):
                    # if the geometry matches, add the other to the unique list
                    # with this object as key, and remove from the old list
                    taggedUniqueDict[obj].append(otherObj)
                    lis.remove(otherObj)
                else:
                    taggedDiscrepancyDetected = True
            lis.remove(obj) # we are done with this object too
    _lg.debug("found %i tagged uniques" % len(taggedUniqueDict))
    
    #3. do the geometry check for untagged objects
    untaggedUniquesDetected = False
    while len(untaggedList)>0:
        obj = untaggedList[0]
        if not obj.hasAttr("AssetPath"):
            pm.addAttr(obj.name(), longName="AssetPath", dataType="string",
                       keyable=False)
        foundUniqueForMe = False
        # compare against one of the tagged uniques
        for other in taggedUniqueDict.keys():
            # if that geometry matches, we found the unique for this obj
            if 0 == pm.polyCompare(obj, other, vertices=True):
                taggedUniqueDict[other].append(obj)
                # set "AssetPath" attr to match that of the unique
                obj.attr("AssetPath").set(other.attr("AssetPath").get())
                # we are done with this object
                untaggedList.remove(obj)
                foundUniqueForMe = True
                _lg.debug("found a unique key (%s) for %s" %(other.name(), obj.name()))
                break
                
        if not foundUniqueForMe:
            untaggedUniquesDetected = True
            # make this a new unique, simply take the objects name as AssetPath
            npath = obj.shortName() + "_AutoExport" + ".fbx"
            obj.attr("AssetPath").set(npath)
            taggedUniqueDict[obj]=[]
            untaggedList.remove(obj)
            _lg.debug("assuming new untagged unique: "+obj.shortName())
            # we will automatically compare to all other untagged to find
            # members for our new unique in the next loop iteration
    _lg.debug("found %i uniques (with untagged)" % len(taggedUniqueDict))
    
    # TODO: 4. UI-stuff...
    #4. if taggedDiscrepancy or untaggedUniques were detected,
    # list all uniques in the UI and let the user change names
    # force him to change names for taggedUniques with same AssetPath of course
    # if taggedDiscrepancyDetected:
        #for unique in taggedUniqueDict.keys():
            # it is up to the UI to do that and let the user
            # set a new assetPath on any of those unique guy's lists
    
    #5. export files stuff
    for obj in taggedUniqueDict.keys():
        exportObjectAsAsset(obj.name(), obj.attr("AssetPath").get())
        
    #6. tell the editor to import all the uniques
    fileList = []
    for obj in taggedUniqueDict.keys():
        fileList.append(obj.attr("AssetPath").get())
    m2u.core.getEditor().importAssetsBatch(fileList)


def sendSelectedToEd():
    selectedMeshes = getSelectedMeshes()
    sendSelectedToEdExportOnly(selectedMeshes)
    assembleScene(selectedMeshes)


def getSelectedMeshes():
    # 1. get selected objects (only transform nodes)
    selectedObjects = pm.selected(type="transform")

    # filter out transforms that don't have a mesh-shape node
    selectedMeshes = list()

    for obj in selectedObjects:
        meshShapes = pm.listRelatives(obj, shapes=True, type="mesh")
        if len(meshShapes) > 0:
            selectedMeshes.append(obj)

    _lg.debug("found %i selected meshes" % len(selectedMeshes))
    # TODO: maybe filter other transferable stuff like lights or so
    return selectedMeshes


def assembleScene(selectedMeshes):
    objInfoList = []

    for obj in selectedMeshes:
        objTransforms = m2u.maya.mayaObjectTracker.getTransformationFromObj(obj)
        objInfo = ObjectInfo(name=obj.shortName(), typeInternal="mesh",
                             typeCommon="mesh")
        objInfo.pos = objTransforms[0]
        objInfo.rot = objTransforms[1]
        objInfo.scale = objTransforms[2]
        objInfo.AssetPath = obj.attr("AssetPath").get()
        objInfoList.append(objInfo)

    m2u.core.getEditor().addActorBatch(objInfoList)
    # TODO: add support for lights and so on
