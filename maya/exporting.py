"""Contains the class ExportOperation that should be used by the UI to
initiate a send-to-editor with export and optional level-assembly.

The UI needs to display data for editing and afterwards decide how to
proceed, depending on which button the user clicked.

"""

import os
import logging

import pymel.core as pm

import m2u
import m2u.helper as helper
from m2u.maya import commands
from m2u.helper.objects import ObjectInfo
from m2u.helper.assethelper import AssetListEntry

_lg = logging.getLogger(__name__)


class ExportOperation(object):

    auto_generated_name_suffix = "_AutoName"

    def __init__(self, do_overwrite=False, do_import=True, do_assemble=True):
        """
        Arguments:
        - `do_overwrite`: Overwrite files on disk
        - `do_import`: Import all exported meshes into the editor
        - `do_assemble`: Assemble the scene in the editor
        """

        self.do_overwrite = do_overwrite
        self.do_import = do_import
        self.do_assemble = do_assemble

        selected_meshes = self._get_selected_meshes()
        self._find_uniques(selected_meshes)

    def get_export_data(self):
        """ Collect the data that can be displayed in the UI for editing.

        The data returned will be in a program-independent format as a
        list of class`AssetListEntry`s.

        It is task of the caller to decide from the collected data,
        and the state of the UI, if and how the export process should
        proceed by calling the appropriate public functions of this
        object.

        :return: (assetList, untaggedUniquesDetected, taggedDiscrepancyDetected)
        """
        #selectedMeshes = self._getSelectedMeshes()
        #self._findUniques(selectedMeshes)
        return (self._asset_list,
                self._untagged_uniques_detected,
                self._tagged_discrepancy_detected)

    def set_edited_data(self, edited_asset_list):
        """ Use the user-edited data from the UI before proceeding with
        the export opertion.
        """
        self._asset_list = edited_asset_list

    def do_export(self):
        self._assign_data()
        self._export_to_files()
        if self.do_import:
            self._editor_import_assets()
        if self.do_assemble:
            self._editor_assemble_scene()

    def do_assign_only(self):
        self._assign_data()

    def _get_selected_meshes(self):
        """ Go through the selected objects and collect all of type 'mesh'
        """
        # 1. get selected objects (only transform nodes)
        selected_objects = pm.selected(type="transform")

        # filter out transforms that don't have a mesh-shape node
        selected_meshes = list()

        for obj in selected_objects:
            mesh_shapes = pm.listRelatives(obj, shapes=True, type="mesh")
            if len(mesh_shapes) > 0:
                selected_meshes.append(obj)

        _lg.debug("Found %i selected meshes" % len(selected_meshes))
        # TODO: maybe filter other transferable stuff like lights or so
        # and add to a nonMeshObjectsList or so
        return selected_meshes

    def _find_uniques(self, selected_meshes):
        """ Assemble the uniques_dict and discrepancy_list by checking
        the meshes for their assetPath attribute and geometric parity.
        """
        #2. for each object get the "AssetPath" attribute
        untagged_list = list()
        tagged_dict = {}
        for obj in selected_meshes:
            if obj.hasAttr("AssetPath"):
                asset_path_attr = obj.attr("AssetPath")
                asset_path_value = asset_path_attr.get()
                if len(asset_path_value) > 0:
                    tagged_dict.setdefault(asset_path_value, []).append(obj)
                else:
                    # If the asset path is empty, that is equal to the
                    # attribute not existing on the object.
                    untagged_list.append(obj)
            else:
                # unknown asset, we will handle those later
                untagged_list.append(obj)
        _lg.debug("found %i untagged" % len(untagged_list))
        _lg.debug("found %i tagged" % len(tagged_dict))

        #3. do the geometry check for tagged objects
        #   this assembles the tagged_unique_dict
        tagged_discrepancy_detected = False
        tagged_unique_dict = {}
        for lis in tagged_dict.values():
            while len(lis) > 0:
                obj = lis[0]
                tagged_unique_dict[obj]=[]
                # compare this object against all others in the list.
                for other_obj in lis[1:]:
                    if 0 == pm.polyCompare(obj, other_obj, vertices=True):
                        # If the geometry matches, add the other to the
                        # unique list with this object as key, and remove
                        # from the old list.
                        tagged_unique_dict[obj].append(other_obj)
                        lis.remove(other_obj)
                    else:
                        #TODO: create new unique for objects
                        # that have same path but different geometry!
                        tagged_discrepancy_detected = True
                lis.remove(obj)
        _lg.debug("found %i tagged uniques" % len(tagged_unique_dict))

        #3. do the geometry check for untagged objects
        untagged_uniques_detected = False
        while len(untagged_list)>0:
            obj = untagged_list[0]
            if not obj.hasAttr("AssetPath"):
                pm.addAttr(obj.name(), longName="AssetPath", dataType="string",
                           keyable=False)
            found_unique_for_me = False
            # compare against one of the tagged uniques
            for other in tagged_unique_dict.keys():
                # if that geometry matches, we found the unique for this obj
                if 0 == pm.polyCompare(obj, other, vertices=True):
                    tagged_unique_dict[other].append(obj)
                    # set "AssetPath" attr to match that of the unique
                    obj.attr("AssetPath").set(other.attr("AssetPath").get())
                    # we are done with this object
                    untagged_list.remove(obj)
                    found_unique_for_me = True
                    _lg.debug("found a unique key ({0}) for {1}"
                              .format(other.name(), obj.name()))
                    break

            if not found_unique_for_me:
                untagged_uniques_detected = True
                # Make this a new unique, simply take the objects name
                # as AssetPath but remove any trailing numbers for
                # convenience.
                npath = obj.shortName()
                npath = helper.remove_number_suffix(npath)
                npath = npath + self.auto_generated_name_suffix  # + ".fbx"
                obj.attr("AssetPath").set(npath)
                tagged_unique_dict[obj] = []
                untagged_list.remove(obj)
                _lg.debug("assuming new untagged unique: " + obj.shortName())
                # We will automatically compare to all other untagged
                # to find members for our new unique in the next loop
                # iteration
        _lg.debug("found %i uniques (with untagged)" % len(tagged_unique_dict))

        # Create a string-based asset list for the UI and further
        # operations this is not a dict because there may be tagged
        # discrepancies (dupl keys).
        asset_list = []
        for obj in tagged_unique_dict.keys():
            path = obj.attr("AssetPath").get()
            # new entry for that path with first object
            entry = AssetListEntry(path)
            entry.append((obj.shortName(), obj))
            # append all other objects that match the geo
            for sobj in tagged_unique_dict[obj]:
                entry.append((sobj.shortName(), sobj))
            asset_list.append(entry)

        self._asset_list = asset_list
        self._untagged_uniques_detected = untagged_uniques_detected
        self._tagged_discrepancy_detected = tagged_discrepancy_detected
        # Note: At this point control is technically returned to the
        #   caller all follow-up operations need to be initiated by the
        #   caller explicitly - this would normally be the UI.

    def _assign_data(self):
        """ Assign the (probably edited) data back to the actual objects
        in the scene. Aka setting the AssetPath attribute on the meshes.
        """
        for e in self._asset_list:
            path = e.assetPath
            for obj in e.getObjectReferencesList():
                obj.attr("AssetPath").set(path)

    def _export_to_files(self):
        """ #5. export the meshes marked for export to the file system
        """
        for obj in [e.getExportObject()[1] for e in self._asset_list]:
            commands.exportObjectAsAsset(obj.name(),
                                         obj.attr("AssetPath").get())
            # TODO: change to pipeline-call
            # TODO: what about self.do_overwrite or not?

    def _editor_import_assets(self):
        """ #6. tell the editor to import all the uniques
        """
        file_list = []
        for path in [e.assetPath for e in self._asset_list]:
            lpath,ext = os.path.splitext(path)
            if ext != ".fbx":
                ext = ".fbx"
            path_with_ext = lpath + ext
            # NOTE: We assume fbx, but a user-set asset path may not
            #   have a .fbx ending the file is definitely written as
            #   .fbx, but the editor may not be able to find the import
            #   file if the extension is missing, so make sure it is set
            file_list.append(path_with_ext)
        m2u.core.editor.import_assets_batch(file_list)

    def _editor_assemble_scene(self):
        """ #7. tell the editor to assemble the level
        """
        obj_info_list = []
        selected_meshes = []
        for e in self._asset_list:
            selected_meshes.extend( e.getObjectReferencesList() )

        for obj in selected_meshes:
            obj_transforms = m2u.maya.objects.get_transformation_from_obj(obj)
            obj_info = ObjectInfo(name=obj.shortName(), typeInternal="mesh",
                                  typeCommon="mesh")
            obj_info.pos = obj_transforms[0]
            obj_info.rot = obj_transforms[1]
            obj_info.scale = obj_transforms[2]
            path = obj.attr("AssetPath").get()
            obj_info.AssetPath = path
            obj_info_list.append(obj_info)

        m2u.core.editor.add_actor_batch(obj_info_list)
        # TODO: add support for lights and so on
