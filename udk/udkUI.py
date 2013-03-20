# keeps all the required UI elements of the UEd and talks to them

import ctypes #required for windows ui stuff

# UI element window handles
gCommandField = None # the udk command line text field
gMainWindow = None # the udk window
gMenuExport = None # export selected menu entry

# windows functions and constants
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
FindWindowEx = ctypes.windll.user32.FindWindowExW

GetClassName = ctypes.windll.user32.GetClassNameW
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindow = ctypes.windll.user32.GetWindow
GW_ENABLEDPOPUP = 6
GW_CHILD = 5

PostMessage = ctypes.windll.user32.PostMessageA
SendMessage = ctypes.windll.user32.SendMessageA
WM_SETTEXT = 0x000C
WM_KEYDOWN = 0x0100
VK_RETURN  = 0x0D
WM_CHAR = 0x0102

# menu stuff
GetMenuItemID = ctypes.windll.user32.GetMenuItemID
GetMenu = ctypes.windll.user32.GetMenu
GetSubMenu = ctypes.windll.user32.GetSubMenu
SC_KEYMENU = 0xF100
WM_COMMAND = 0x0111

# windows param macro, needed for sending keys and clicking buttons n stuff
def MAKELONG(l,h):
    return (l & 0xFFFF) | ((h & 0xFFFF) << 16) 
  
MAKELPARAM = MAKELONG
MAKEWPARAM = MAKELONG

# required for modal dialog stuff
# (thanks to http://www.speechcomputing.com/node/2809)
GetGUIThreadInfo = ctypes.windll.user32.GetGUIThreadInfo
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
EnumThreadWindows = ctypes.windll.user32.EnumThreadWindows

class RECT(ctypes.Structure):
 _fields_ = [
     ("left", ctypes.c_ulong),
     ("top", ctypes.c_ulong),
     ("right", ctypes.c_ulong),
     ("bottom", ctypes.c_ulong)
 ]

class GUITHREADINFO(ctypes.Structure):
 _fields_ = [
     ("cbSize", ctypes.c_ulong),
     ("flags", ctypes.c_ulong),
     ("hwndActive", ctypes.c_ulong),
     ("hwndFocus", ctypes.c_ulong),
     ("hwndCapture", ctypes.c_ulong),
     ("hwndMenuOwner", ctypes.c_ulong),
     ("hwndMoveSize", ctypes.c_ulong),
     ("hwndCaret", ctypes.c_ulong),
     ("rcCaret", RECT)
 ]
 
#def getModalDialog(thread):
#    """
#    get the hwnd of the modal dialog that is currently blocking in the thread
#    """
#    gti = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
#    print "gti" + str(gti)
#    #result = GetGUIThreadInfo(thread, ctypes.byref(gti)) #always fails Oo
#    #print "result " + str(result)
#    print gti.hwndActive
#    print gti.hwndFocus
#    print gti.hwndCapture
#    return gti.hwndFocus

class ThreadWinLParm(ctypes.Structure):
    """
    a lParam object to get a name to and an object back
    from the a windows enumerator Proc function
    """
    _fields_=[
        ("name", ctypes.c_wchar_p),
        ("hwnd", ctypes.POINTER(ctypes.c_long))
    ]


def _getThreadWndByTitle(hwnd, lParam):
    """
    this is a callback function called by EnumThreadWindows
    lParam has to be a ctypes byref instance of ThreadWinLParam
    """
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    if buff.value == param.name:
        param.hwnd = hwnd
        return False #stop iteration
    return True

def _getChildWindowByName(hwnd, lParam):
    """
    performs a recursive hierarchical search (not like FindWindowEx)
    TODO aarg, childWindow geht nicht wirklich durch alle fenster durch,
    oder der windowText ist nichts was zum identifizieren taugt...
    findWindowEx muss ja leider der string fuer bekannt sein
    """
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents

    length = 255
    cbuff = ctypes.create_unicode_buffer(length + 1)
    GetClassName(hwnd, cbuff, length+1)
    print "wnd "+cbuff.value+" "+buff.value
    if buff.value == param.name:
        param.hwnd = hwnd
        return False
    #else:
    #    EnumWindows(hwnd, EnumWindowsProc(_getChildWindowByName),lParam)
    return True

    
def _getWindows(hwnd, lParam):
    """
    get the UEd Window (and fill the ui element vars)
    note: this is a callback function. windows itself will call this function for every top-level window in EnumWindows iterator function
    """
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        if "Unreal Development Kit" in buff.value:
            print "found UDK"
            global gMainWindow
            gMainWindow = hwnd
            
            # get the command line field
            global gCommandField
            child = 0
            child = FindWindowEx(hwnd, child, u"msctls_statusbar32", 0)
            child = FindWindowEx(child, 0, u"ComboBox", 0)
            gCommandField = FindWindowEx(child, 0, u"Edit", 0)
            
            #get menus
            global gMenuExport
            hMenu = GetMenu(gMainWindow)
            hFileMenu = GetSubMenu(hMenu,0)
            hExportMenu = GetSubMenu(hFileMenu, 13)
            gMenuExport = GetMenuItemID(hExportMenu, 1)

            return False # we foun udk, no further iteration required
    return True

def connectToUEd():
    EnumWindows(EnumWindowsProc(_getWindows), 0)


def fireCommand(command):
    """
    executes the command string in UdK (uses the command field)
    """
    global gCommandField
    SendMessage(gCommandField, WM_SETTEXT, 0, str(command) )
    #PostMessage(gCommandField, WM_KEYDOWN, VK_RETURN, 0)   
    PostMessage(gCommandField, WM_CHAR, VK_RETURN, 0)   
    # so... VK_RETURN with WM_KEYDOWN didn't work from within maya...
    # but WM_CHAR works, simply with the VK_RETURN value
    
def callExportSelected(filePath, withTextures):
    """
    calls the menu entry for export selected
    enters the file path and answers the popup dialogs
    """
    global gMainWindow
    global gMenuExport
    thread = GetWindowThreadProcessId(gMainWindow, 0)
    
    param = ThreadWinLParm(name="Export")
    lParam = ctypes.byref(param) #ctypes.cast(param,ctypes.pointer)
    EnumThreadWindows(thread, EnumWindowsProc(_getThreadWndByTitle), lParam)
    hDlg = param.hwnd
    
    SendMessage(hDlg, WM_SETTEXT, 0, str(filePath))
    listAllChildren(hDlg)
    #length = GetWindowTextLength(hDlg)
    #buff = ctypes.create_unicode_buffer(length + 1)
    #GetWindowText(hDlg, buff, length + 1)
    #print buff.value
    #PostMessage(hDlg, WM_CHAR, VK_RETURN, 0)
    #PostMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(IDC_OK,BN_CLICKED),
    #GetDlgItem(IDC_OK)) #maybe alternative to sending VK_RETURN

def listAllChildren(hwnd):
    """
    """
    param = ThreadWinLParm(name="Export")
    lParam = ctypes.byref(param)
    EnumChildWindows( hwnd, EnumWindowsProc(_getChildWindowByName),lParam)
    

connectToUEd()
#callExportSelected(1,1)
#listAllChildren(gMainWindow)