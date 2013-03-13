"""
as for some reason the PostMessage with VK_RETURN seems not to work when
called from mayas built-in python, this script will only do the job of sending
enter to the desired windows component

THIS FILE IS OBSOLETE
"""

import sys
import ctypes

PostMessage = ctypes.windll.user32.PostMessageA
WM_KEYDOWN = 0x0100
VK_RETURN  = 0x0D

SendMessage = ctypes.windll.user32.SendMessageA
WM_SETTEXT = 0x000C

ChangeWindowMessageFilterEx = ctypes.windll.user32.ChangeWindowMessageFilterEx

def main():
    print("enter script called with main")
    if (len(sys.argv)<2):
        print("no window handle in argv") #yes yes, throw and catch and stuff... later
    hwnd=int(sys.argv[1])
    print(hwnd)
    ChangeWindowMessageFilterEx(hwnd, WM_KEYDOWN, 1)
    PostMessage(hwnd, WM_KEYDOWN, VK_RETURN, 0)
    #SendMessage(hwnd, WM_SETTEXT, 0, "ladidadi" )
    PostMessage(hwnd, WM_CHAR, VK_RETURN, 0)
    

if __name__=="__main__":
    main()
else:
    print "you did not call this file as main!"
