# keeps all the required UI elements of the UEd and talks to them

import ctypes #required for windows ui stuff

import os
import glob 
import time

import threading

#from udkUIHelper import getIFileSaveDialogFromHwnd

# UI element window handles
gCommandField = None # the udk command line text field
gMainWindow = None # the udk window
gMenuExportID = None # export selected menu entry

gMenuCutID = None # edit-cut menu entry
gMenuCopyID = None # edit-copy menu entry
gMenuPasteID = None # edit-paste menu entry
gMenuDuplicateID = None # edit-duplicate menu entry
gMenuDeleteID = None # edit-delete menu entry
gMenuSelectNoneID = None # edit-selectNone menu entry

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

GetFocus = ctypes.windll.user32.GetFocus
SetFocus = ctypes.windll.user32.SetFocus

PostMessage = ctypes.windll.user32.PostMessageA
SendMessage = ctypes.windll.user32.SendMessageA
WM_SETTEXT = 0x000C
WM_KEYDOWN = 0x0100
VK_RETURN  = 0x0D
WM_CHAR = 0x0102
VK_F = 0x46
VK_SELECT = 0x29
VK_ESCAPE = 0x1B
IDOK = 1
IDCANCEL = 2

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

AttachThreadInput = ctypes.windll.user32.AttachThreadInput

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
        ("cls", ctypes.c_wchar_p),
        ("hwnd", ctypes.POINTER(ctypes.c_long)),
        ("enumPos", ctypes.c_int),
        ("_enum", ctypes.c_int) # keep track of current enum step
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
        print "Found Wanted Thread Window"
        param.hwnd = hwnd
        return False #stop iteration
    return True

def _getChildWindowByName(hwnd, lParam):
    """
    callback function to be called by EnumChildWindows

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
    else: #bot values are None, print the current element
        print "wnd cls: "+cbuff.value+" name: "+buff.value+" enum: "+str(param._enum)
    return True

def getChildWindowByName(hwnd, name = '', cls = ''):
    """
    convenience function, see _getChildWindowByName
    """
    param = ThreadWinLParm(name=name,cls=cls,_enum=-1)
    lParam = ctypes.byref(param)
    EnumChildWindows( hwnd, EnumWindowsProc(_getChildWindowByName),lParam)
    return param.hwnd

def _getChildWindowByEnumPos(hwnd, lParam):
    """ callback function """
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    param._enum += 1
    if param._enum == param.enumPos:
        param.hwnd = hwnd
        return False
    return True

def getChildWindowByEnumPos(hwnd, pos):
    """
    uses the creation order which is reflected in Enumerate functions to get the handle to a certain window. this is useful when the name or cls is not unique
    you can count the enum pos by printing all child windows of a window
    """
    param = ThreadWinLParm(name = None, cls = None, enumPos = pos, _enum = -1)
    EnumChildWindows( hwnd, EnumWindowsProc(_getChildWindowByEnumPos), ctypes.byref(param))
    return param.hwnd


def attachThreads(hwnd):
    """
    this will tell windows to attach the program and the udk threads
    this will give us some benefits in control, for example SendMessage calls to the udk thread will only return when udk has processed the message, amazing!
    """
    thread = GetWindowThreadProcessId(hwnd, 0) #udk thread
    thisThread = threading.current_thread().ident #program thread
    print "# m2u: Attaching threads",thread,"and",thisThread
    AttachThreadInput(thread, thisThread, True)
    
def _getWindows(hwnd, lParam):
    """
    get the UEd Window (and fill the ui element vars)
    note: this is a callback function. windows itself will call this function for every top-level window in EnumWindows iterator function
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
            global gMainWindow
            gMainWindow = hwnd
            
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
            
            return False # we found udk, no further iteration required
    return True

def connectToUEd():
    global gMainWindow
    EnumWindows(EnumWindowsProc(_getWindows), 0)
    if gMainWindow is None:
        print "# m2u: No UDK instance found."
    return (gMainWindow is not None)


def fireCommand(command):
    """
    executes the command string in UdK (uses the command field)
    """
    global gCommandField
    SendMessage(gCommandField, WM_SETTEXT, 0, str(command) )
    #PostMessage(gCommandField, WM_CHAR, VK_RETURN, 0)
    #time.sleep(0.1) #TODO fix this maybe?
    SendMessage(gCommandField, WM_CHAR, VK_RETURN, 0)
    #PostMessage(gCommandField, WM_KEYDOWN, VK_RETURN, 0)
    # VK_RETURN with WM_KEYDOWN didn't work from within maya, use WM_CHAR instead...

def callExportSelected(filePath, withTextures):
    """
    calls the menu entry for export selected
    enters the file path and answers the popup dialogs
    """
    #global gMainWindow
    #global gMenuExportID

    PostMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuExportID,0),0)
    time.sleep(0.1) #TODO fix this maybe, we wait a little so all dlg elements are there before we try to access them.
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
    print "FUUUUU"
    
    """
    #b = ctypes.windll.user32.RedrawWindow(hDlg,0,0,0)
    #b = ctypes.windll.user32.UpdateWindow(hDlg)
    #time.sleep(0.01)
    #and again, since i found no other way to somehow wait till all child elements of the dialog are created, we have to ask so long, until we finally find the element we want
    """
    
    ctypes.windll.user32.SetFocus(hDlg)
    null_ptr = ctypes.POINTER(ctypes.c_int)()
    param = ThreadWinLParm(hwnd = null_ptr, name=None, cls="Edit")
    while not bool(param.hwnd): # while NULL
        print "child = "+ str(param.hwnd)
        EnumChildWindows(hDlg, EnumWindowsProc(_getChildWindowByName), ctypes.byref(param))
    print "found edit field"
    edit = param.hwnd
    print "edit: "+ str(ctypes.addressof(edit))
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


def callEditCut():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuCutID,0),0)

def callEditCopy():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuCopyID,0),0)

def callEditPaste():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuPasteID,0),0)

def callEditDuplicate():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuDuplicateID,0),0)

def callEditDelete():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuDeleteID,0),0)

def callSelectNone():
    SendMessage(gMainWindow, WM_COMMAND, MAKEWPARAM(gMenuSelectNoneID,0),0)


