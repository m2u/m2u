"""
usage of the windows SendInput function is a little bit complicated because
new input struct objects have to be created for each input, but the advantage
of SendInput is that nothing can interfere with it.

The alternative functions are mouse_event and keybd_event, mostly can do
the same, or can't do the same, are deprecated, but are easier to use ;)

big parts copied from here: http://stackoverflow.com/questions/1823762/sendkeys-for-python-3-1-on-windows/2004267#2004267

also: http://msdn.microsoft.com/en-us/library/ms646310(v=vs.85).aspx

"""
# currently only used for the sendMouseClick function
# as the desired keybd input (disabling the shift key) did not work
# because you cannot override what "GetAsyncKeystate" win function returns


import ctypes as ct



class cls_KeyBdInput(ct.Structure):
    _fields_ = [
        ("wVk", ct.c_ushort),
        ("wScan", ct.c_ushort),
        ("dwFlags", ct.c_ulong),
        ("time", ct.c_ulong),
        ("dwExtraInfo", ct.POINTER(ct.c_ulong) )
    ]

class cls_HardwareInput(ct.Structure):
    _fields_ = [
        ("uMsg", ct.c_ulong),
        ("wParamL", ct.c_short),
        ("wParamH", ct.c_ushort)
    ]

class cls_MouseInput(ct.Structure):
    _fields_ = [
        ("dx", ct.c_long),
        ("dy", ct.c_long),
        ("mouseData", ct.c_ulong),
        ("dwFlags", ct.c_ulong),
        ("time", ct.c_ulong),
        ("dwExtraInfo", ct.POINTER(ct.c_ulong) )
    ]

class cls_Input_I(ct.Union):
    _fields_ = [
        ("ki", cls_KeyBdInput),
        ("mi", cls_MouseInput),
        ("hi", cls_HardwareInput)
    ]

class cls_Input(ct.Structure):
    _fields_ = [
        ("type", ct.c_ulong),
        ("ii", cls_Input_I)
    ]


def make_input_objects( l_keys ):
    
    p_ExtraInfo_0 = ct.pointer(ct.c_ulong(0))
    
    l_inputs = [ ]
    for n_key, n_updown in l_keys:
        ki = cls_KeyBdInput( n_key, 0, n_updown, 0, p_ExtraInfo_0 )
        ii = cls_Input_I()
        ii.ki = ki
        l_inputs.append( ii )
    
    n_inputs = len(l_inputs)
    
    l_inputs_2=[]
    for ndx in range( 0, n_inputs ):
        s2 = "(1, l_inputs[%s])" % ndx
        l_inputs_2.append(s2)
    s_inputs = ', '.join(l_inputs_2)
    
    
    cls_input_array = cls_Input * n_inputs
    o_input_array = eval( "cls_input_array( %s )" % s_inputs )
    
    p_input_array = ct.pointer( o_input_array )
    n_size_0 = ct.sizeof( o_input_array[0] )
    
    # these are the args for user32.SendInput()
    return ( n_inputs, p_input_array, n_size_0 )
    
    '''It is interesting that o_input_array has gone out of scope
    by the time p_input_array is used, but it works.'''


MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
def make_mouse_lclick_input_objects(x,y):
    
    p_ExtraInfo_0 = ct.pointer(ct.c_ulong(0))
    
    l_inputs = [ ]

    # mmove = cls_MouseInput( x, y, 0, MOUSEEVENTF_ABSOLUTE|MOUSEEVENTF_MOVE,
    #                         0, p_ExtraInfo_0 )
    # movInp = cls_Input_I()
    # movInp.mi = mmove
    
    lbtnDown = cls_MouseInput( x, y, 0, MOUSEEVENTF_ABSOLUTE|MOUSEEVENTF_LEFTDOWN,
                               0, p_ExtraInfo_0 )
    dwnInp = cls_Input_I()
    dwnInp.mi = lbtnDown

    lbtnUp  = cls_MouseInput( x, y, 0, MOUSEEVENTF_ABSOLUTE|MOUSEEVENTF_LEFTUP,
                               0, p_ExtraInfo_0 )
    upInp = cls_Input_I()
    upInp.mi = lbtnUp

    #l_inputs.append(movInp) # movement does not work?
    l_inputs.append(upInp) # make sure btn is down, so we create a new click
    l_inputs.append(dwnInp)
    l_inputs.append(upInp)
    
    n_inputs = len(l_inputs)
    
    l_inputs_2=[]
    for ndx in range( 0, n_inputs ):
        s2 = "(0, l_inputs[%s])" % ndx
        l_inputs_2.append(s2)
    s_inputs = ', '.join(l_inputs_2)
    
    
    cls_input_array = cls_Input * n_inputs
    o_input_array = eval( "cls_input_array( %s )" % s_inputs )
    
    p_input_array = ct.pointer( o_input_array )
    n_size_0 = ct.sizeof( o_input_array[0] )
    
    # these are the args for user32.SendInput()
    return ( n_inputs, p_input_array, n_size_0 )
    


def sendInput(keys):
    t_inputs = make_input_objects(keys)
    rv = ct.windll.user32.SendInput( *t_inputs )
    return rv

def sendMouseClick(x,y):
    ct.windll.user32.SetCursorPos(x,y)
    t_inputs = make_mouse_lclick_input_objects(x,y)
    rv = ct.windll.user32.SendInput(*t_inputs)
    return rv