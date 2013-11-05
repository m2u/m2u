# keeps all the required UI elements of the UEd and talks to them
# this file should be divided into several as it is getting untidy ;)

import ctypes #required for windows ui stuff

import os
import glob 
import time

import threading
import m2u

#from udkUIHelper import getIFileSaveDialogFromHwnd

# UI element window handles
gUDKThreadProcessID = None # the UI-thread of UDK
gMainWindow = None # the udk window
gCommandField = None # the udk command line text field

gMenuExportID = None # export selected menu entry
gMenuCutID = None # edit-cut menu entry
gMenuCopyID = None # edit-copy menu entry
gMenuPasteID = None # edit-paste menu entry
gMenuDuplicateID = None # edit-duplicate menu entry
gMenuDeleteID = None # edit-delete menu entry
gMenuSelectNoneID = None # edit-selectNone menu entry

gBtnHideSelectedID = None
gBtnShowAllID = None

# windows functions and constants
# stuff for finding and analyzing UI Elements
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

# stuff for interacting with UI Elements
GetFocus = ctypes.windll.user32.GetFocus
SetFocus = ctypes.windll.user32.SetFocus

PostMessage = ctypes.windll.user32.PostMessageA
SendMessage = ctypes.windll.user32.SendMessageA
SendMessageTimeout = ctypes.windll.user32.SendMessageTimeoutA
SMTO_NORMAL = 0x0000
SMTO_BLOCK = 0x0001
SMTO_ERRORONEXIT = 0x0020
SMTO_NOTIMEOUTIFNOTHUNG = 0x0008
SMTO_FLAGS = SMTO_NORMAL|SMTO_ERRORONEXIT
SMTO_TIMEOUT_MS = 1000 # 1 second

WM_SETTEXT = 0x000C
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102 # the alternative to WM_KEYDOWN
VK_RETURN  = 0x0D # Enter key
VK_F = 0x46 # the F-key (used for export dialog: fbx)
VK_SELECT = 0x29
VK_ESCAPE = 0x1B
VK_SHIFT = 0x10
#VK_SHIFT = 0xA0 # LSHIFT

IDOK = 1 # used for dialogs
IDCANCEL = 2 # used for dialogs
BM_CLICK = 0x00F5 # button clicked message

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
GetDlgItemText = ctypes.windll.user32.GetDlgItemTextW
GetDlgItem = ctypes.windll.user32.GetDlgItem
GetNextDlgTabItem = ctypes.windll.user32.GetNextDlgTabItem

# attaching is required for SendMessage and the like to actually work like it should
AttachThreadInput = ctypes.windll.user32.AttachThreadInput

def checkWinZeroReturn(value):
    if value==0:
        raise ctypes.WinError()

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
    """lParam object to get a name to and an object back from a windows
    enumerator function.

    .. seealso:: :func:`_getChildWindowByName`
    """
    _fields_=[
        ("name", ctypes.c_wchar_p),
        ("cls", ctypes.c_wchar_p),
        ("hwnd", ctypes.POINTER(ctypes.c_long)),
        ("enumPos", ctypes.c_int),
        ("_enum", ctypes.c_int) # keep track of current enum step
    ]


def _getThreadWndByTitle(hwnd, lParam):
    """callback function to be called by EnumThreadWindows

    :param hwnd: the window handle
    :param lParam: a :ref:`ctypes.byref` instance of :class:`ThreadWinLParam`

    :deprecated: use :func:`_getChildWindowByName` instead.
    
    """
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    if buff.value == param.name:
        #print "Found Wanted Thread Window"
        param.hwnd = hwnd
        return False #stop iteration
    return True

def _getChildWindowByName(hwnd, lParam):
    """callback function to be called by EnumChildWindows, see
    :func:`getChildWindowByName`

    :param hwnd: the window handle
    :param lParam: a :ref:`ctypes.byref` instance of :class:`ThreadWinLParam`
    
    if name is None, the cls name is taken,
    if cls is None, the name is taken,
    if both are None, all elements are printed
    if both have values, only the element matching both will fit
    
    """
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    param._enum += 1

    length = 255
    cbuff = ctypes.create_unicode_buffer(length + 1)
    GetClassName(hwnd, cbuff, length+1)
    if param.name == None and param.cls != None:
        #print "no name, but cls"
        if param.cls in cbuff.value:# == param.cls:
            param.hwnd = hwnd
            return False
    elif param.cls == None and param.name != None:
        #print "no cls, but name"
        if buff.value == param.name:
            param.hwnd = hwnd
            return False
    elif param.cls != None and param.name != None:
        #print "cls and name"
        if buff.value == param.name and param.cls in cbuff.value:# == param.cls:
            param.hwnd = hwnd
            return False
    else: #both values are None, print the current element
        print "wnd cls: "+cbuff.value+" name: "+buff.value+" enum: "+str(param._enum)
    return True

def getChildWindowByName(hwnd, name = None, cls = None):
    """find a window by its name or clsName, returns the window's hwnd
    
    :param hwnd: the parent window's hwnd
    :param name: the name/title to search for
    :param cls: the clsName to search for

    :return: the hwnd of the matching child window
    
    if name is None, the cls name is taken,
    if cls is None, the name is taken,
    if both are None, all elements are printed
    if both have values, only the element matching both will fit.
    
    .. seealso:: :func:`_getChildWindowByName`, :func:`getChildWindowByEnumPos`
    
    """
    param = ThreadWinLParm(name=name,cls=cls,_enum=-1)
    lParam = ctypes.byref(param)
    EnumChildWindows( hwnd, EnumWindowsProc(_getChildWindowByName),lParam)
    return param.hwnd

def _getChildWindowByEnumPos(hwnd, lParam):
    """ callback function, see :func:`getChildWindowByEnumPos` """
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    param._enum += 1
    if param._enum == param.enumPos:
        param.hwnd = hwnd
        return False
    return True

def getChildWindowByEnumPos(hwnd, pos):
    """get a child window by its enum pos, return its hwnd

    :param hwnd: the parent window's hwnd
    :param pos: the number to search for

    :return: the hwnd of the matching child window
    
    This function uses the creation order which is reflected in Windows Enumerate
    functions to get the handle to a certain window. This is useful when the
    name or cls of the desired window is not unique or not given.
    
    You can count the enum pos by printing all child windows of a window.
    .. seealso:: :func:`getChildWindowByName`
    
    """
    param = ThreadWinLParm(name = None, cls = None, enumPos = pos, _enum = -1)
    EnumChildWindows( hwnd, EnumWindowsProc(_getChildWindowByEnumPos), ctypes.byref(param))
    return param.hwnd

    
def attachThreads(hwnd):
    """tell Windows to attach the program and the udk threads.
    
    This will give us some benefits in control, for example SendMessage calls to
    the udk thread will only return when udk has processed the message, amazing!
    
    """
    thread = GetWindowThreadProcessId(hwnd, 0) #udk thread
    #thread = gUDKThreadProcessID
    global gUDKThreadProcessID
    gUDKThreadProcessID = thread
    thisThread = threading.current_thread().ident #program thread
    print "# m2u: Attaching threads",thread,"and",thisThread
    AttachThreadInput(thread, thisThread, True)
    
def _getWindows(hwnd, lParam):
    """callback function, find the UEd Window (and fill the ui element vars)
    
    This is a callback function. Windows itself will call this function for
    every top-level window in EnumWindows iterator function.
    .. seealso:: :func:`connectToUEd`
    """
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        #if "Maya" in buff.value:
        #    thread = GetWindowThreadProcessId(hwnd, 0)
        #    print "maya thread:",thread
        if "Unreal Development Kit" in buff.value:
            print "# m2u: Found UDK"
            global gMainWindow, gUDKThreadProcessID
            gMainWindow = hwnd
            #thread = GetWindowThreadProcessId(hwnd, 0) #udk thread
            #gUDKThreadProcessID = thread
            attachThreads(gMainWindow)
            
            # get the command line field
            global gCommandField
            child = 0
            child = FindWindowEx(hwnd, child, u"msctls_statusbar32", 0)
            child = FindWindowEx(child, 0, u"ComboBox", 0)
            gCommandField = FindWindowEx(child, 0, u"Edit", 0)
            
            #get menus
            global gMenuExportID
            hMenu = GetMenu(gMainWindow)
            hFileMenu = GetSubMenu(hMenu,0) #File
            hExportMenu = GetSubMenu(hFileMenu, 13) #Export
            gMenuExportID = GetMenuItemID(hExportMenu, 1) #Selected Only
            
            global gMenuCutID, gMenuCopyID, gMenuPasteID
            global gMenuDuplicateID, gMenuDeleteID, gMenuSelectNoneID
            hEditMenu = GetSubMenu(hMenu,1) #Edit
            gMenuCutID = GetMenuItemID(hEditMenu, 7) #Cut
            gMenuCopyID = GetMenuItemID(hEditMenu, 8) #Copy
            gMenuPasteID = GetMenuItemID(hEditMenu, 9) #Paste
            gMenuDuplicateID = GetMenuItemID(hEditMenu, 10) #Duplicate
            gMenuDeleteID = GetMenuItemID(hEditMenu, 11) #Delete
            gMenuSelectNoneID = GetMenuItemID(hEditMenu, 13)
            
            #get buttons
            global gBtnShowAllID, gBtnHideSelectedID
            #child = FindWindowEx(gMainWindow, 0, u"Select", 0)
            child = getChildWindowByName(gMainWindow, name = "Select", cls = None)
            gBtnHideSelectedID = getChildWindowByEnumPos(child, 1)
            gBtnShowAllID = getChildWindowByEnumPos(child, 3)
            
            #get stuff from other windows
            #get Layers Menu Items
            layerWindow = getThreadWindowByName(gUDKThreadProcessID, name = "Layers")
            hMenu = GetMenu(layerWindow)
            hLayerMenu = GetSubMenu(hMenu, 0)
            #gMenuLayerNewID = GetMenuItemID(hLayerMenu, 0) # new layer (popup)
            #gMenuLayerRenameID = GetMenuItemID(hLayerMenu, 1) # rename layer (popup) 
            gMenuLayerDeleteID = GetMenuItemID(hLayerMenu, 2) # delete layer
            gMenuLayerAddActorsID = GetMenuItemID(hLayerMenu, 4) 
            gMenuLayerRemoveActorsID = GetMenuItemID(hLayerMenu, 5)
            
            
            
            return False # we found udk, no further iteration required
    return True

def connectToUEd():
    global gMainWindow
    EnumWindows(EnumWindowsProc(_getWindows), 0)
    if gMainWindow is None:
        print "# m2u: No UDK instance found."
    return (gMainWindow is not None)

def getThreadWindowByName(thread, name = None, cls = None):
    """find a window of a thread by its name/title, returns the window's hwnd
    
    :param thread: the ID of the UI-thread
    :param name: the name/title to search for
    :param cls: the clsName to search for

    :return: the hwnd of the matching window
    
    if name is None, the cls name is taken,
    if cls is None, the name is taken,
    if both are None, all windows are printed
    if both have values, only the window matching both will fit.
    
    .. seealso:: :func:`getChildWindowByName`
    
    """
    param = ThreadWinLParm(name=name,cls=cls,_enum=-1)
    #EnumThreadWindows(thread, EnumWindowsProc(_getThreadWndByTitle), ctypes.byref(param))
    lParam = ctypes.byref(param)
    EnumThreadWindows( thread, EnumWindowsProc(_getChildWindowByName),lParam)
    return param.hwnd

def fireCommand(command):
    """executes the command string in UdK (uses the command field)"""
    global gCommandField
    SendMessage(gCommandField, WM_SETTEXT, 0, str(command) )
    #PostMessage(gCommandField, WM_CHAR, VK_RETURN, 0)
    #time.sleep(0.1) #TODO fix this maybe?
    SendMessage(gCommandField, WM_CHAR, VK_RETURN, 0)
    #PostMessage(gCommandField, WM_KEYDOWN, VK_RETURN, 0)
    # VK_RETURN with WM_KEYDOWN didn't work from within maya, use WM_CHAR instead...

def callExportSelected(filePath, withTextures):
    """
    calls the menu entry for export selected,
    enters the file path and answers the popup dialogs
    """
    #global gMainWindow
    #global gMenuExportID

    PostMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuExportID,0),0)
    time.sleep(0.1) #HACK (fix this maybe): we wait a little so all dlg elements are there before we try to access them.
    # SendMessage blocks execution, because it only returns when the modal gets closed
    # PostMessage returns before the modal is opened
    # so we will Post, and ask the thread so long for the export window, until it is there. that might not be the best way, but i really have no other idea anymore, on how to get to the modal dialog 
    thread = GetWindowThreadProcessId(gMainWindow, 0)
    print thread
    null_ptr = ctypes.POINTER(ctypes.c_int)()
    param = ThreadWinLParm(hwnd = null_ptr, name="Export",cls=None)
    #time.sleep(0.02) #give it some time to process, before bombing it with requests
    while not bool(param.hwnd): # while NULL
        #print "hwnd = "+ str(param.hwnd)
        EnumThreadWindows(thread, EnumWindowsProc(_getThreadWndByTitle), ctypes.byref(param))
    hDlg = param.hwnd
    #print "FUUUUU"
    
    # #b = ctypes.windll.user32.RedrawWindow(hDlg,0,0,0)
    # #b = ctypes.windll.user32.UpdateWindow(hDlg)
    # #time.sleep(0.01)
    # #and again, since i found no other way to somehow wait till all child elements of the dialog are created, we have to ask so long, until we finally find the element we want
    
    ctypes.windll.user32.SetFocus(hDlg)
    null_ptr = ctypes.POINTER(ctypes.c_int)()
    param = ThreadWinLParm(hwnd = null_ptr, name=None, cls="Edit")
    while not bool(param.hwnd): # while NULL
        #print "child = "+ str(param.hwnd)
        EnumChildWindows(hDlg, EnumWindowsProc(_getChildWindowByName), ctypes.byref(param))
    #print "found edit field"
    edit = param.hwnd
    #print "edit: "+ str(ctypes.addressof(edit))
    SendMessage(edit, WM_SETTEXT, 0, str(filePath))
    #dlg = getIFileSaveDialogFromHwnd(hDlg)

#    param = ThreadWinLParm(hwnd = null_ptr, name=None, cls="ListBox")
#    EnumChildWindows(hDlg, EnumWindowsProc(_getChildWindowByName),ctypes.byref(param))
#    listbox = param.hwnd
#    print "ListBox: "+ str(ctypes.addressof(listbox))
#    SendMessage(listbox, WM_KEYDOWN, VK_F,0)
    #focushwnd = GetFocus()
    #print "focus =",focushwnd
    #SendMessage(focushwnd, WM_SETTEXT,0,str("focused"))

    #SendMessage(hDlg, WM_SETTEXT,0, str("testidi"))
    #return
    
    #listAllChildren(hDlg)
    #time.sleep(0.1)
    address = GetNextDlgTabItem(hDlg, edit, False) #1 filetype combo box
    SetFocus(address)
    SendMessage(address, WM_CHAR, VK_F, 0) # send "F" to set to FBX
    
    # now positively answer the dialog (press the save-button)
    #SetFocus(edit)
    #PostMessage(edit, WM_CHAR, VK_RETURN, 0) # not working
    #SendMessage(edit, WM_KEYDOWN, VK_RETURN, 0) # not working
    SetFocus(hDlg)
    #SendMessage(hDlg, WM_KEYDOWN, VK_ESCAPE, 0) # not working
    #SendMessage(hDlg, WM_CHAR, VK_ESCAPE, 0) #not working
    #PostMessage(hDlg, WM_KEYDOWN, VK_ESCAPE, 0) # working
    #PostMessage(hDlg, WM_CHAR, VK_ESCAPE, 0) # not tested
    SendMessage(hDlg, WM_COMMAND, MAKEWPARAM(IDOK,0),0) # working

    # tried to get the address line because initially it didn't work to set the full path in the filename-field, but for some reason it works now...
    #GetDlgItem(hDlg,1)
    #address = GetNextDlgTabItem(hDlg, address, False) #2 "show folders" thingie
    #address = GetNextDlgTabItem(hDlg, address, False) #3 Save button
    #SetFocus(address)
    #SendMessage(address, WM_KEYDOWN, VK_RETURN, 0) # press the save button
    #address = GetNextDlgTabItem(hDlg, address, False) #4 Cancel button
    #address = GetNextDlgTabItem(hDlg, address, False) #5 Address bar
    #address = GetNextDlgTabItem(hDlg, address, False) #6
    #print "address: " + str(address)
    #SendMessage(address, WM_CHAR, VK_SELECT, 0)

    #listAllChildren(hDlg)
    #SendMessage(address, WM_SETTEXT, 0, str(filePath))
    #print "sent enter to address"
    """
    null_ptr = ctypes.POINTER(ctypes.c_int)()
    param = ThreadWinLParm(hwnd = null_ptr, name=None, cls=None, enumPos=35, _enum=-1)
    while not bool(param.hwnd): # while NULL
        print "child = "+ str(param.hwnd)
        EnumChildWindows(hDlg, EnumWindowsProc(_getChildWindowByEnumPos), ctypes.byref(param))
    print "found thingy field"
    print ctypes.addressof(param.hwnd)
    """
    """
    null_ptr = ctypes.POINTER(ctypes.c_int)()
    param = ThreadWinLParm(hwnd = null_ptr, name=None, cls="ToolbarWindow32")
    while not bool(param.hwnd): # while NULL
        print "child = "+ str(param.hwnd)
        EnumChildWindows(hDlg, EnumWindowsProc(_getChildWindowByName), ctypes.byref(param))
    print "found thingy field"
    """
    #SendMessage(param.hwnd, WM_SETTEXT, 0, str("Adresse: Z:\\Documents"))
#    filenameField = getChildWindowByName(hDlg,name=None,cls='Edit')
#    SendMessage(filenameField, WM_SETTEXT, 0, str(filePath))
#    PostMessage(filenameField, WM_CHAR, VK_RETURN, 0)
    #PostMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(IDC_OK,BN_CLICKED),
    #GetDlgItem(IDC_OK)) #maybe alternative to sending VK_RETURN

def listAllChildren(hwnd):
    """convenience function, print all children of a hwnd"""
    getChildWindowByName(hwnd,name=None,cls=None)

    
#connectToUEd()
#callExportSelected("Z:/Documents",1)
#listAllChildren(gMainWindow)

def isKeyDown(key):
    pressed = ctypes.windll.user32.GetAsyncKeyState(key)
    #print "pressed",pressed
    highBit = pressed & 0x8000 #check high order bit
    #highBit = pressed & 0xff #check high order bit
    #print "high bit",highBit
    return bool(highBit) 
    # more info: http://stackoverflow.com/questions/5302456/how-do-i-get-the-high-and-low-order-bits-of-a-short

import sys
def isShiftDown():
    return isKeyDown(VK_SHIFT)
    
_gShiftWasDown = 0
def killModifierKeys():
    """ this function will disable modifier keys that interfere with UDK operations. currently this is only the Shift-key, which creates popup dialogs when used in combination with Cut, Copy and Paste
    don't forget to restore the previous key state with restoreModifierKeyState() so the user won't notice. """
    global _gShiftWasDown
    print "getting shift state"
    sys.stdout.flush()
    _gShiftWasDown = isShiftDown()
    if _gShiftWasDown:
        print "shift is down, upping"
        sys.stdout.flush()
        #focushwnd = GetFocus()
        SendMessage(gMainWindow, WM_KEYUP, VK_SHIFT, 0)
        #time.sleep(0.1)
    # HACK: for some reason it takes a while for the call to WM_KEYUP to take effect
    # that is why we wait a little after that here, of course that is not desired
    # TODO: check alternatives like keybd_event, SendInput and SetKeyboardState

def restoreModifierKeyState():
    shiftis = isShiftDown()
    print "shift is now down?",shiftis
    sys.stdout.flush()
    if _gShiftWasDown:
        print "shift was down, downing"
        sys.stdout.flush()
        #focushwnd = GetFocus()
        SendMessage(gMainWindow, WM_KEYDOWN, VK_SHIFT, 0)
        #time.sleep(0.1)
        # HACK: see killModifierKeys, same reason
        shiftis = isShiftDown()
        print "shift downed successfull?",shiftis
        sys.stdout.flush()

import udkWinInput
def sendEditCut():
    print "sending edit cut"
    SetFocus(gMainWindow)
    print "have set focus"
    t_unshift_ctrl_x = (
        #(VK_SHIFT, 2), #release shift
        (0x11, 0), #ctrl
        (0x58, 0), #x
        (0x11, 2),
        (0x58, 2),
    ) 
    udkWinInput.sendInput(t_unshift_ctrl_x)
    print "done sending edit cut"

def sendEditPaste():
    print "sending edit paste"
    SetFocus(gMainWindow)
    t_unshift_ctrl_v = (
        (VK_SHIFT, 2), #release shift
        (0x11, 0), #ctrl
        (0x56, 0), #v
        (0x11, 2),
        (0x56, 2),
    ) 
    udkWinInput.sendInput(t_unshift_ctrl_v)
    
def callEditCut():
    secureWaitForShiftRelease()
    #SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuCutID,0),0)
    v = SendMessageTimeout(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuCutID,0), 0, SMTO_FLAGS, SMTO_TIMEOUT_MS)
    #checkWinZeroReturn(v)

def callEditCopy():
    secureWaitForShiftRelease()
    #SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuCopyID,0),0)
    v = SendMessageTimeout(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuCopyID,0), 0, SMTO_FLAGS, SMTO_TIMEOUT_MS)
    #checkWinZeroReturn(v)


def callEditPaste():
    secureWaitForShiftRelease()
    #SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuPasteID,0),0)
    v = SendMessageTimeout(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuPasteID,0), 0, SMTO_FLAGS, SMTO_TIMEOUT_MS)
    #checkWinZeroReturn(v)

def callEditDuplicate():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuDuplicateID,0),0)

def callEditDelete():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuDeleteID,0),0)

def callSelectNone():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuSelectNoneID,0),0)

def callHideSelected():
    SendMessage(gBtnHideSelectedID, BM_CLICK, 0, 0)

def callShowAll():
    SendMessage(gBtnShowAllID, BM_CLICK, 0, 0)


def testUnshiftKeyboard():
    buffType = ctypes.c_ubyte*256 #256 byte array
    buff = buffType() #create one
    status = ctypes.windll.user32.GetKeyboardState(ctypes.byref(buff))
    if not status:
        print "getting KeyboardState failed"
        return
    shiftIsDown = (buff[VK_SHIFT]&128) == 128 # high bit is 1 = key is down
    print "shift is down",shiftIsDown
    print "going to toggle shift"
    #if shiftIsDown:
    buff[VK_SHIFT] = 0 # key is not down, previous state (low bit) is unimportant
    #else:
    #    buff[VK_SHIFT] = 128 # key is down, previous state (low bit) is unimportant
    status = ctypes.windll.user32.SetKeyboardState(ctypes.byref(buff))
    if not status:
        "setting keyboardState failed"
    print "checking if shift is now down"
    status = ctypes.windll.user32.GetKeyboardState(ctypes.byref(buff))
    shiftIsDown = (buff[VK_SHIFT]&128) == 128 # high bit is 1 = key is down
    print "shift is down",shiftIsDown


def killOrRestoreShift(bKill):
    global _gShiftWasDown
    buffType = ctypes.c_ubyte*256 #256 byte array
    buff = buffType() #create one
    status = ctypes.windll.user32.GetKeyboardState(ctypes.byref(buff))
    if not status:
        print "# m2u: getting KeyboardState failed"
        return
    shiftIsDown = (buff[VK_SHIFT]&128) == 128 # high bit is 1 = key is down
    print "shift is down",shiftIsDown
    print "going to unshift"
    _gShiftWasDown = shiftIsDown
    #if shiftIsDown and bKill:
    buff[VK_SHIFT] = 0 # key is not down, previous state (low bit) is unimportant
    #elif _gShiftWasDown and not shiftIsDown and not bKill:
    #    buff[VK_SHIFT] = 128 # key is down, previous state (low bit) is unimportant
    status = ctypes.windll.user32.SetKeyboardState(ctypes.byref(buff))
    if not status:
        print "# m2u: setting KeyboardState failed"



class POINT(ctypes.Structure):
 _field_ = [
     ("x", ctypes.c_long),
     ("y", ctypes.c_long)
 ]
 
class MSG(ctypes.Structure):
 _fields_ = [
     ("hwnd", ctypes.POINTER(ctypes.c_long)),
     ("message", ctypes.c_ulong),
     ("wParam", ctypes.POINTER(ctypes.c_uint)),
     ("lParam", ctypes.POINTER(ctypes.c_uint)),
     ("time", ctypes.c_uint),
     ("pt", POINT)
 ]

def killAllMessages():
    msg = MSG()
    c = 1
    while c:
        print "removing message"
        c = ctypes.windll.user32.PeekMessageA(ctypes.byref(msg), gMainWindow, 0,0, 0x0001)

def secureWaitForShiftRelease():
    """will block execution until the user releases the shift key."""
    if not isShiftDown():
        return
    #TODO: add warning that displays directly from the m2u GUI, so the user won't miss it. maya warnings aren't displayed while a move command is issued
    #m2u.core.getProgram().printWarning("# m2u: Please release the SHIFT KEY for Thread-Lock reasons")
    sys.stdout.flush()
    while True:
        time.sleep(0.01)
        if not isShiftDown():
            return
