import os
import logging

import pymel.core as pm

import m2u
import m2u.helper as helper
from m2u.helper.objects import ObjectInfo
from m2u.helper.assethelper import AssetListEntry

_lg = logging.getLogger(__name__)


class ExportOperation(object):
    """An ExportOperation should be used by the UI to initiate a send-
    to-editor process with asset export and optional level-assembly.

    The data gathered will be in a program-independent format as a list
    of `AssetListEntry`s.

    Data gathered initially can be modified by the UI, by modifying the
    `asset_list`, before further processing it with either `do_export()`
    or `do_assign_only()`.

    It is task of the caller to decide from the collected data, and the
    state of the UI, if and how the export process should proceed by
    calling the appropriate public functions of this object.
    """

    def __init__(self, do_overwrite=False, do_import=True, do_assemble=True):
        """Collect data for exporting, based on the selected objects in
        the scene.

        Args:
            do_overwrite (bool): Overwrite files on disk when exporting.
            do_import (bool): Import all exported meshes into the editor.
            do_assemble (bool): Assemble the scene in the editor.
        """

        self.do_overwrite = do_overwrite
        self.do_import = do_import
        self.do_assemble = do_assemble

        selected_meshes = self._get_selected_meshes()
        self._find_uniques(selected_meshes)

    def set_edited_data(self, edited_asset_list):
        """Use the user-edited data - from the UI - before proceeding
        with the export opertion.
        """
        self.asset_list = edited_asset_list

    def do_export(self):
        """Execute a complete export process, based on the current data.

        This will assign the data to the objects in the scene, then
        export and - depending on settings - tell the Editor to import
        and assemble the scene.
        """
        self._assign_data()
        self._export_to_files()
        if self.do_import:
            self._editor_import_assets()
        if self.do_assemble:
            self._editor_assemble_scene()

    def do_assign_only(self):
        """Only assign the current data to the objects in the scene.
        """
        self._assign_data()

    def _get_selected_meshes(self):
        """Go through the selected objects and collect all of type 'mesh'
        """
        # We are only interested in selected transform nodes.
        selected_objects = pm.selected(type="transform")

        # Filter out transforms that don't have a mesh-type shape node.
        selected_meshes = list()
        for obj in selected_objects:
            mesh_shapes = pm.listRelatives(obj, shapes=True, type="mesh")
            if len(mesh_shapes) > 0:
                selected_meshes.append(obj)

        _lg.debug("Found {0} selected meshes.".format(len(selected_meshes)))
        # TODO: filter other transferable stuff like lights etc.
        return selected_meshes

    def _find_uniques(self, selected_meshes):
        """Assemble the `asset_list` and detect `tagged_discrepancy`
        by checking the meshes for their `AssetPath` attribute and
        geometric parity.

        Uniques here means geometric objects that have the same geometry
        even if they are not instantiated. When normally duplicating
        objects in Maya, the copy will be a different geometry object,
        but both, original and copy, will come down to the same 'unique'
        mesh by comparing their geometry.
        """
        # For each object check the "AssetPath" attribute. Those which
        # have one are considered 'tagged'.
        untagged_list = list()
        tagged_dict = {}  # Map AssetPath strings to all objects using it
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
                # Unknown asset, we will handle those later.
                untagged_list.append(obj)

        _lg.debug("Found %i untagged objects." % len(untagged_list))
        _lg.debug("Found %i tagged objects." % len(tagged_dict))

        # Do the geometry check for 'tagged' objects:
        # Assemble the `tagged_unique_dict`, which maps an object to a
        # list of all other objects that have the same geometry.
        # A 'tagged discrepancy' is when objects sharing the same
        # geometry have different "AssetPath" values.
        tagged_discrepancy_detected = False
        tagged_unique_dict = {}
        for object_list in tagged_dict.values():
            while len(object_list) > 0:
                obj = object_list[0]
                tagged_unique_dict[obj] = []
                # Compare this object against all others in the list.
                for other_obj in object_list[1:]:
                    have_same_geometry = (
                        pm.polyCompare(obj, other_obj, vertices=True) == 0)
                    if have_same_geometry:
                        # If the geometry matches, add the other to the
                        # unique list with this object as key, and remove
                        # from the old list.
                        tagged_unique_dict[obj].append(other_obj)
                        object_list.remove(other_obj)
                    else:
                        # TODO: Create new unique for objects that have
                        #   same AssetPath but different geometry.
                        tagged_discrepancy_detected = True
                object_list.remove(obj)

        _lg.debug("Found %i tagged uniques." % len(tagged_unique_dict))

        # Do the geometry check for 'untagged' objects:
        # If tagged objects with the same geometry exist, add the object
        # to the respective list and use their AssetPath.
        # If there is no unique yet for the geometry, use the first
        # object with that geometry as a new unique, and use its name as
        # AssetPath.
        untagged_uniques_detected = False
        while len(untagged_list) > 0:
            obj = untagged_list[0]
            if not obj.hasAttr("AssetPath"):
                pm.addAttr(obj.name(), longName="AssetPath", dataType="string",
                           keyable=False)
            found_unique_for_me = False
            # Compare against one of the tagged uniques.
            for unique_obj in tagged_unique_dict.keys():
                have_same_geometry = (
                    pm.polyCompare(obj, unique_obj, vertices=True) == 0)
                if have_same_geometry:
                    # If that geometry matches, we found the unique to
                    # use for this obj.
                    tagged_unique_dict[unique_obj].append(obj)
                    asset_path = unique_obj.attr("AssetPath").get()
                    obj.attr("AssetPath").set(asset_path)
                    found_unique_for_me = True
                    untagged_list.remove(obj)
                    _lg.debug("Found an existing unique key ({0}) for {1}"
                              .format(unique_obj.name(), obj.name()))
                    break

            if not found_unique_for_me:
                untagged_uniques_detected = True
                # Make this a new unique. Simply take the object's name
                # as AssetPath, but remove any trailing numbers for
                # convenience.
                npath = obj.shortName()
                npath = helper.remove_number_suffix(npath)
                obj.attr("AssetPath").set(npath)
                tagged_unique_dict[obj] = []
                untagged_list.remove(obj)
                _lg.debug("Assuming new untagged unique: " + obj.shortName())
                # We will automatically compare to all other untagged
                # to find members for our new unique in the next loop
                # iteration

        _lg.debug("Found {0} uniques (including untagged)."
                  .format(len(tagged_unique_dict)))

        # Create a string-based asset list for the UI and further
        # operations. This is not a dict because there may be tagged
        # discrepancies (dupl keys).
        asset_list = []
        for unique_obj, instance_objects in tagged_unique_dict.items():
            path = unique_obj.attr("AssetPath").get()
            # New entry for that AssetPath with first object.
            entry = AssetListEntry(path)
            entry.append(unique_obj.shortName(), unique_obj)
            # Append all other objects that match the geo.
            for instance in instance_objects:
                entry.append(instance.shortName(), instance)
            asset_list.append(entry)

        self.asset_list = asset_list
        self.untagged_uniques_detected = untagged_uniques_detected
        self.tagged_discrepancy_detected = tagged_discrepancy_detected
        # Note: At this point control is technically returned to the
        #   caller. All follow-up operations need to be initiated by the
        #   caller explicitly - this would normally be the UI.

    def _assign_data(self):
        """Assign the (probably edited) data back to the actual objects
        in the scene. Aka setting the AssetPath attribute on the meshes.
        """
        for asset_entry in self.asset_list:
            for obj in asset_entry.get_object_references_list():
                obj.attr("AssetPath").set(asset_entry.asset_path)

    def _export_to_files(self):
        """Export the meshes marked for export to the file system.
        """
        export_objects = []
        for asset_entry in self.asset_list:
            export_node = asset_entry.get_export_object()[1]
            export_objects.append(export_node)

        for obj in export_objects:
            export_object_as_asset(obj.name(),
                                   obj.attr("AssetPath").get())
            # TODO: what about self.do_overwrite or not?

    def _editor_import_assets(self):
        """Tell the editor to import all the uniques.
        """
        file_list = []
        for asset_entry in self.asset_list:
            path = asset_entry.asset_path
            lpath, ext = os.path.splitext(path)
            if ext != ".fbx":
                ext = ".fbx"
            path_with_ext = lpath + ext
            # NOTE: We assume fbx, but a user-set asset path may not
            #   have a .fbx ending. The file is definitely written as
            #   .fbx, but the editor may not be able to find the import
            #   file if the extension is missing, so make sure it is set
            file_list.append(path_with_ext)
        m2u.core.editor.import_assets_batch(file_list)

    def _editor_assemble_scene(self):
        """Tell the editor to assemble the level.
        """
        obj_info_list = []
        selected_meshes = []
        for asset_entry in self.asset_list:
            selected_meshes.extend(asset_entry.get_object_references_list())

        for obj in selected_meshes:
            obj_transforms = m2u.maya.objects.get_transformation_from_obj(obj)
            obj_info = ObjectInfo(name=obj.shortName(), type_internal="mesh",
                                  type_common="mesh")
            obj_info.pos = obj_transforms[0]
            obj_info.rot = obj_transforms[1]
            obj_info.scale = obj_transforms[2]
            path = obj.attr("AssetPath").get()
            obj_info.asset_path = path
            obj_info_list.append(obj_info)

        m2u.core.editor.add_actor_batch(obj_info_list)
        # TODO: add support for lights and so on


def export_object_as_asset(name, path):
    # TODO: move to maya-specific pipeline file
    """Export object `name` to FBX file specified by `path`.

    Args:
        name (str): The object's name (name of the tranfsorm node).
        path (str): File path with extension, RELATIVE to the content root.

    """
    content_root = m2u.core.pipeline.get_project_export_dir()
    lpath, ext = os.path.splitext(path)
    if ext != ".fbx":
        ext = ".fbx"
    path = lpath + ext
    fullpath = content_root + path
    export_object_centered(name, fullpath, center=True)


def export_object_centered(name, path, center=True):
    # TODO: move to maya-specific pipeline-file
    """Export object `name` to FBX file specified by `path`.

    Args:
        name (str): The object's name (name of the tranfsorm node).
        path (str): ABSOLUTE file path for the fbx file.
        center (bool): If True, the object transformation will be reset
            before export.

    """
    was_syncing = m2u.core.program.is_object_syncing()
    # Disable syncing, so the matrix reset  won't be reflected in Ed.
    m2u.core.program.set_object_syncing(False)

    identity = [1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0]

    pm.select(name, r=True)
    if center:
        # Backup the matrix and pivot so we can restore them later.
        mat = pm.xform(query=True, ws=True, m=True)
        piv = pm.xform(name, piv=True, q=True, ws=True)
        pm.xform(name, a=True, ws=True, m=identity)

    export_selected_to_fbx(path)

    if center:
        # Reset matrix and pivot to stored values.
        pm.xform(name, a=True, ws=True, m=mat)
        pm.xform(name, ws=True, piv=(piv[0], piv[1], piv[2]))

    # Restore syncing state.
    m2u.core.program.set_object_syncing(was_syncing)


def export_selected_to_fbx(path):
    # TODO: move to maya-specific pipeline-file
    """Export selection to file specified by `path`.

    Fbx settings will be loaded from preset file.
    """
    if os.path.exists(path):
        os.remove(path)

    # TODO: fbxExportPreset should be Editor-specific
    sfpath = m2u.core.pipeline.get_fbx_settings_file_path()
    _lg.debug("Loading FBX settings from '{0}'".format(sfpath))
    lsfcmd = ('FBXLoadExportPresetFile -f "{0}";'
              .format(sfpath.replace("\\", "/")))
    pm.mel.eval(lsfcmd)

    _lg.debug("Exporting File: " + path)
    # Maya's FBX command is not able to create directories, so we let
    # python do that.
    directory = os.path.dirname(path)
    m2u.core.pipeline.make_sure_path_exists(directory)
    expcmd = 'FBXExport -f "{0}" -s;'.format(path.replace("\\", "/"))
    pm.mel.eval(expcmd)
