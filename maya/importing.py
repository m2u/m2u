import pymel.core as pm

import m2u


# TODO: move this function to a program-specific pipeline module
# maybe it has to be split in one that is m2u specific and one that
# can be generalized (the importing itself, while still disabling m2u-syncing)
# on the other hand, if somebody provides his own pipeline for m2u, they
# should be able to do this from within those functions too.
def import_file(path):
    """ simply imports an FBX-file
    """
    # Disable object tracking, because importing FBX files will cause
    # a lot of renaming and we don't want that to produce warnings.
    was_syncing = m2u.core.program.is_object_syncing()
    m2u.core.program.set_object_syncing(False)

    cmd = 'FBXImport -f "{0}"'.format(path.replace("\\", "/"))
    pm.mel.eval(cmd)

    # Restore previous syncing state
    m2u.core.program.set_object_syncing(was_syncing)
