""" Commands for tracking and manipulating the maya viewport cameras. """

import sys

import pymel.core as pm

import m2u
from m2u.maya import objects

this = sys.modules[__name__]

# Module reference assigned to this, because script-jobs will access it.
this.objects = objects

this._is_camera_syncing = False
this._camera_script_job = None


def set_camera_syncing(sync):
    this._is_camera_syncing = sync
    if sync:
        _create_camera_tracker()
    else:
        _delete_camera_tracker()


def is_camera_syncing():
    return this._is_camera_syncing


def set_fov(degrees):
    cam = pm.nodetypes.Camera('perspShape', query=True)
    cam.setHorizontalFieldOfView(degrees)


def setup_cameras_for_large_scale_scenes():
    """Set position, clip planes and fov of default cameras to work
    better with the bigger size of UnrealEngine scenes.
    """
    cam = pm.nodetypes.Camera('perspShape', query=True)
    cam.setFarClipPlane(65536.0)
    cam.setNearClipPlane(10.0)
    cam.setHorizontalFieldOfView(90.0)
    cam = pm.nodetypes.Camera('topShape', query=True)
    cam.setFarClipPlane(100000.0)
    cam.setNearClipPlane(10.0)
    pm.setAttr('top.ty', 50000.0)
    cam = pm.nodetypes.Camera('frontShape', query=True)
    cam.setFarClipPlane(100000.0)
    cam.setNearClipPlane(10.0)
    pm.setAttr('front.tz', 50000.0)
    cam = pm.nodetypes.Camera('sideShape', query=True)
    cam.setFarClipPlane(100000.0)
    cam.setNearClipPlane(10.0)
    pm.setAttr('side.tx', 50000.0)


def _on_persp_changed_scriptjob():
    """The scriptjob function for transferring the perspective camera
    transformation to the editor.
    """
    cam_name = 'persp'
    t, r, s = this.objects.get_transformation_from_obj(cam_name)
    rx, ry, rz = pm.xform(cam_name, query=True, ws=True, ro=True)
    # Transform rotation to match UE->fbx z-up format
    # TODO: This should be handled in editor-specific functions
    r = (rx-90, -rz-90, ry)
    m2u.core.editor.transform_camera(t[0], t[1], t[2], r[0], r[1], r[2])


def _create_camera_tracker():
    """Create a scriptjob for transferring the camera transformation,
    that is executed each time the camera transform is changed.
    """
    # First make sure there is no old script-job lying aroung.
    _delete_camera_tracker()
    this._camera_script_job = pm.scriptJob(
        attributeChange=['persp.inverseMatrix', _on_persp_changed_scriptjob])


def _delete_camera_tracker():
    """Delete the camera tracking script-job."""
    scriptjob_exists = (this._camera_script_job is not None and
                        pm.scriptJob(exists=this._camera_script_job))
    if scriptjob_exists:
        pm.scriptJob(kill=this._camera_script_job, force=True)
        this._camera_script_job = None
