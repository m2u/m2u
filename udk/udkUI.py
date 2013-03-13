# keeps all the required UI elements of the UEd and connects to them

import ctypes #required for windows ui stuff

# UI elements
gCommandField = None # the udk command line text field

# windows functions and constants
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool,
ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
EnumChildWindows = ctypes.windll.user32.EnumChildWindows

FindWindowEx = ctypes.windll.user32.FindWindowExW

GetClassName = ctypes.windll.user32.GetClassNameW
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

PostMessage = ctypes.windll.user32.PostMessageA
SendMessage = ctypes.windll.user32.SendMessageA
WM_SETTEXT = 0x000C
WM_KEYDOWN = 0x0100
VK_RETURN  = 0x0D
WM_CHAR = 0x0102


def getWindows(hwnd, lParam):
    """
    get the UEd Window (and fill the ui element vars)
    note: windows itself will call this function for every top-level window
    in an iterator function
    """
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        if "Unreal Development Kit" in buff.value:
            print "found UDK"
            child = 0
            # get the command line field
            child = FindWindowEx(hwnd, child, u"msctls_statusbar32", 0)
            child = FindWindowEx(child, 0, u"ComboBox", 0)
            global gCommandField
            gCommandField = FindWindowEx(child, 0, u"Edit", 0)

    return True

def connectToUEd():
    EnumWindows(EnumWindowsProc(getWindows), 0)

#import os
#from m2u.core import hub
def fireCommand(command):
    global gCommandField
    SendMessage(gCommandField, WM_SETTEXT, 0, str(command) )
    #if hub.program.getProgName() == "maya":
    #    print("program is maya")
    #    # a little hack required for maya
    #    folder = os.path.dirname(os.path.realpath(__file__))
    #    fcmd = (r"python "+folder+r"\udkMayaSendEnter.py " + str(gCommandField))
    #    print(fcmd)
    #    os.system(fcmd)
    #else:
    #    PostMessage(gCommandField, WM_KEYDOWN, VK_RETURN, 0)   
    PostMessage(gCommandField, WM_CHAR, VK_RETURN, 0)   
    # so... VK_RETURN with WM_KEYDOWN didn't work from within maya...
    # but WM_CHAR works, simply with the VK_RETURN value
    # strange stuff
    
