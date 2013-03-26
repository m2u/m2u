# contains windows GUI helper functions for the "do stuff, using the UI" parts of the UDK communication

import ctypes



# === COM stuff ====================
# use the windows COM interface to access the FileDialogs
# Note: doesn't work ;(

"""
import comtypes.client
from comtypes.gen import shobjidl # some windows COM Interfaces

def getIFileSaveDialogFromHwnd(hDlg):
    IID_IUnknown =  comtypes.IUnknown._iid_
    Dlg_ptr = ctypes.POINTER(shobjidl.IFileSaveDialog)()
    #Dlg_ptr = ctypes.POINTER(ctypes.c_int)()
    print Dlg_ptr
    result = ctypes.oledll.oleacc.AccessibleObjectFromWindow(hDlg, 0, ctypes.byref(IID_IUnknown), ctypes.byref(Dlg_ptr))
    #DlgCom = shobjidl .IFileSaveDialog(DlgCom.contents)
    print "result:"+str(result)
    print "ptr "+Dlg_ptr
    print "value "+Dlg_ptr.value
    print Dlg_ptr.value.GetFolder()
    #DlgCom = ctypes.cast(Dlg_ptr, ctypes.POINTER(shobjidl.IFileSaveDialog))
    #DlgCom.SetFileName("ladidadi")

#def accessibleObjectFromWindow(hwnd):
# ptr = ctypes.POINTER(IAccessible)()
# res = oledll.oleacc.AccessibleObjectFromWindow(
#   hwnd,0,
#   byref(IAccessible._iid_),byref(ptr))
# return ptr
"""