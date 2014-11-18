"""
Contains the class ExportOperation that should be used by the UI to initiate a
send-to-editor with export and optional level-assembly. 
The UI needs to display data for editing and afterwards decide how to proceed,
depending on which button the user clicked.

Why use a class here (while the rest of m2u is so not-OO)? 
I just feel better about using a class when we have certain
states (bAssemble etc.) that can be set when creating the object and will always be
at a default state for a new export operation. The other option would be to use
module global variables to save that state. That wouldn't be better or worse, so
it is open for discussion :)
"""

import pymel.core as pm
import pymel.api as mapi

import m2u
import m2u.helper as helper
from m2u.helper.ObjectInfo import ObjectInfo
from m2u.helper.assetHelper import AssetListEntry

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

#program = m2u.core.getProgram()
#editor = m2u.core.getEditor()

class ExportOperation(object):
    
    def __init__(self, bOverwrite = False, bImport = True, bAssemble = True):
        """
        Arguments:
        - `bOverwrite`: overwrite files on disk 
        - `bImport`: import all exported meshes into the editor
        - `bAssemble`: assemble the scene in the editor
        """
        self._bOverwrite = bOverwrite
        self._bImport = bImport
        self._bAssemble = bAssemble

        selectedMeshes = self._getSelectedMeshes()
        self._findUniques(selectedMeshes)
        

    def getExportData(self):
        """ collect the data that can be displayed in the UI for editing.

        The data returned will be in a program-independent format as a
        list of class`AssetListEntry`s.

        It is task of the caller to decide from the collected data, 
        and the state of the UI, if and how the export process should
        proceed by calling the appropriate public functions of this object.

        :return: (assetList, untaggedUniquesDetected, taggedDiscrepancyDetected) 
        """
        #selectedMeshes = self._getSelectedMeshes()
        #self._findUniques(selectedMeshes)
        return (self._assetList, 
                self._untaggedUniquesDetected, 
                self._taggedDiscrepancyDetected)
        

    def setEditedData(self, editedAssetList):
        """ pass the user-edited data from the UI before proceeding with
        the export opertion.
        """
        self._assetList = editedAssetList

    def doExport(self):
        self._assignData()
        self._exportToFiles()
        if self._bImport:
            self._editorImportAssets()
        if self._bAssemble:
            self._editorAssembleScene()

    def doAssignOnly(self):
        self._assignData()

    def _getSelectedMeshes(self):
        """ go through the selected objects and collect all of type 'mesh'
        """
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
        # and add to a nonMeshObjectsList or so
        return selectedMeshes


    def _findUniques(self, selectedMeshes):
        """ assemble the uniquesDict and discrepancyList by checking the meshes for
        their assetPath attribute and geometric parity
        """
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
                        #TODO: create new unique for objects
                        # that have same path but different geometry!
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

        # create a string-based asset list for the UI and further operations
        # this is not a dict because there may be tagged discrepancies (dupl keys)
        assetList=[]
        for obj in taggedUniqueDict.keys():
            path = obj.attr("AssetPath").get()
            # new entry for that path with first object
            entry = AssetListEntry(path)
            entry.append( (obj.shortName(), obj) )
            # append all other objects that match the geo
            for sobj in taggedUniqueDict[obj]:
                entry.append( (sobj.shortName(), sobj) )
            assetList.append(entry)
        
        self._assetList = assetList
        self._untaggedUniquesDetected = untaggedUniquesDetected
        self._taggedDiscrepancyDetected = taggedDiscrepancyDetected
        # Note: at this point control is technically returned to the caller
        # all following operations need to be initiated by the caller explicitly
        # this would normally be the UI
        

    def _assignData(self):
        """ assign the (probably edited) data back to the actual objects in the
        scene. Aka setting the AssetPath attribute on the meshes.
        """
        for e in self._assetList:
            path = e.assetPath
            for obj in e.getObjectReferencesList():
                obj.attr("AssetPath").set(path)

    def _exportToFiles(self):
        """ #5. export the meshes marked for export to the file system
        """
        for obj in [e.getExportObject()[1] for e in self._assetList]:
            program = m2u.core.getProgram()
            program.mayaCommand.exportObjectAsAsset(obj.name(), 
                                                    obj.attr("AssetPath").get())
            #TODO: change to pipeline-call
            #TODO: what about self._bOverwrite or not?

    def _editorImportAssets(self):
        """ #6. tell the editor to import all the uniques
        """
        fileList = []
        for path in [e.assetPath for e in self._assetList]:
            fileList.append(path)
        m2u.core.getEditor().importAssetsBatch(fileList)

    def _editorAssembleScene(self):
        """ #7. tell the editor to assemble the level
        """
        objInfoList = []
        selectedMeshes = []
        for e in self._assetList:
            selectedMeshes.extend( e.getObjectReferencesList() )

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