# helper functions for mainly operating system stuff

import os
import time


def waitForFileToBecomeAvailable(path,maxWaitTime=10):
    """
    This function will wait till a specified file is available for further processing. This means it waits till the file comes into existence and no other application is using the file (as far as we can determine it). This function is important for stuff like telling UDK to export something and importing it into the 3d-application in the next step.
    The function will return True when the file is available, and False if the maxWaitTime has passed before the file is available.
    """
    waitedTime = 0
    # first step: make sure the file exists or wait for it to come into existence
#    while not os.path.exists(path):
#        time.sleep(0.01)
#        waitedTime += 0.01
#        if waitedTime > maxWaitTime:
#            print "# m2u: waited for too long for file a"
#            return False
#        print "waited a little for file: created"

    # this is a better approach than trying to open the file, because we could open it although it was in use. We now try to rename it. Windows will give us an exception if the file is not available and, when it is available, if the file is in use by another process. This is exactly what we want ;)

    # make sure there is nothing blocking our attempts from a failed previous attempt or so
    TOUCHED_STR = "touched"
    if os.path.exists(path+TOUCHED_STR):
        os.remove(path+TOUCHED_STR) 
    
    # now try to rename the file we are waiting for until we are able to do so
    while True:
        try:
            os.rename(path, path+TOUCHED_STR)
            os.rename(path+TOUCHED_STR, path)
            return True # file is available for us
        except OSError as e:
            #print e
            time.sleep(0.01)
            waitedTime += 0.01
            if waitedTime > maxWaitTime:
                print "# m2u: Waited for too long for file to become available: "+path
                return False
#
#    while True:
#        try:
        #     f = open(path,'w')
        #     f.close()
        #     print "closing file, returning"
        #     time.sleep(0.1)
        #     return True
        # except IOError as e:
        #     time.sleep(0.01)
        #     waitedTime += 0.01
        #     print "waited a little for file: available"
        #     if waitedTime > maxWaitTime:
        #         print "# m2u: waited for too long for file b"
        #         return False
        #     else:
        #         print "next loop"
        #         #continue
#        f.close()
#        print "closing file, returning"
#        time.sleep(0.02)
#        return True
    