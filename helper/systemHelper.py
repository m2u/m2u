"""Helper functions for mainly operating system stuff """

import os
import time
import logging

_lg = logging.getLogger(__name__)


def wait_for_file_to_become_available(path, timeout_seconds=10):
    """
    Wait till a specified file is available for further processing.

    This means it waits till the file comes into existence and no other
    application is using the file (as far as we can determine it). This
    function is important for stuff like telling UDK to export something
    and importing it into the 3d-application in the next step.

    The function will return True when the file is available, and False
    if the timeout_seconds have passed before the file is available.

    """

    # To determine if the file is still in use, we try to rename it.
    # Windows will give us an exception if the file is not available
    # and, when it is available, if the file is in use by another
    # process.

    # Make sure there is nothing blocking from a failed previous attempt.
    TOUCHED_STR = "touched"
    renamed_file_path = path + TOUCHED_STR
    if os.path.exists(renamed_file_path):
        os.remove(renamed_file_path)

    waited_time = 0
    while True:
        try:
            os.rename(path, renamed_file_path)
            os.rename(renamed_file_path, path)
            return True  # File is available for us
        except OSError:
            time.sleep(0.01)
            waited_time += 0.01
            if waited_time > timeout_seconds:
                _lg.error("Waited for too long for file to become available: "
                          "{0}".format(path))
                return False
