import ctypes
from ctypes import wintypes
import time
import speech_recognition as sr
import win32gui, win32api, win32con


user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12
VK_A = 0x41
VK_W = 0x57
VK_D = 0x44
VK_S = 0x53
VK_SPACEBAR = 0x20
VK_F = 0x46
VK_1 = 0x31
VK_2 = 0x32
VK_3 = 0x33
VK_4 = 0x34
VK_5 = 0x35
VK_6 = 0x36
VK_7 = 0x37
VK_8 = 0x38
VK_9 = 0x39
VK_K = 0x4B
VK_L = 0x4C


# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class Mouse:
    """It simulates the mouse"""
    MOUSEEVENTF_MOVE = 0x0001 # mouse move 
    MOUSEEVENTF_LEFTDOWN = 0x0002 # left button down 
    MOUSEEVENTF_LEFTUP = 0x0004 # left button up 
    MOUSEEVENTF_RIGHTDOWN = 0x0008 # right button down 
    MOUSEEVENTF_RIGHTUP = 0x0010 # right button up 
    MOUSEEVENTF_MIDDLEDOWN = 0x0020 # middle button down 
    MOUSEEVENTF_MIDDLEUP = 0x0040 # middle button up 
    MOUSEEVENTF_WHEEL = 0x0800 # wheel button rolled 
    MOUSEEVENTF_ABSOLUTE = 0x8000 # absolute move 
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1

    def _do_event(self, flags, x_pos, y_pos, data, extra_info):
        """generate a mouse event"""
        x_calc = int(65536 * x_pos / ctypes.windll.user32.GetSystemMetrics(self.SM_CXSCREEN) + 1)
        y_calc = int(65536 * y_pos / ctypes.windll.user32.GetSystemMetrics(self.SM_CYSCREEN) + 1)
        return ctypes.windll.user32.mouse_event(flags, x_calc, y_calc, data, extra_info)

    def _get_button_value(self, button_name, button_up=False):
        """convert the name of the button into the corresponding value"""
        buttons = 0
        if button_name.find("right") >= 0:
            buttons = self.MOUSEEVENTF_RIGHTDOWN
        if button_name.find("left") >= 0:
            buttons = buttons + self.MOUSEEVENTF_LEFTDOWN
        if button_name.find("middle") >= 0:
            buttons = buttons + self.MOUSEEVENTF_MIDDLEDOWN
        if button_up:
            buttons = buttons << 1
        return buttons

    def move_mouse(self, pos):
        """move the mouse to the specified coordinates"""
        (x, y) = pos
        old_pos = self.get_position()
        x =  x if (x != -1) else old_pos[0]
        y =  y if (y != -1) else old_pos[1]    
        self._do_event(self.MOUSEEVENTF_MOVE + self.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)

    def press_button(self, pos=(-1, -1), button_name="left", button_up=False):
        """push a button of the mouse"""
        self.move_mouse(pos)
        self._do_event(self.get_button_value(button_name, button_up), 0, 0, 0, 0)

    def click(self, pos=(-1, -1), button_name= "left"):
        """Click at the specified placed"""
        self.move_mouse(pos)
        self._do_event(self._get_button_value(button_name, False)+self._get_button_value(button_name, True), 0, 0, 0, 0)

    def double_click (self, pos=(-1, -1), button_name="left"):
        """Double click at the specifed placed"""
        for i in xrange(2): 
            self.click(pos, button_name)

    def get_position(self):
        """get mouse position"""
        return win32api.GetCursorPos()

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def ReleaseAllKeys():
    ReleaseKey(VK_A)    
    ReleaseKey(VK_W)    
    ReleaseKey(VK_D)
    ReleaseKey(VK_S)
    ReleaseKey(VK_SPACEBAR)
    ReleaseKey(VK_F)
    ReleaseKey(VK_K)
    ReleaseKey(VK_L)


def PressAndReleaseNumberKey(spokenWord):
    ReleaseAllKeys() 

    if "first" in spokenWord:
        PressKey(VK_1)
    elif "second" in spokenWord:
        PressKey(VK_2)
    elif "third" in spokenWord:
        PressKey(VK_3)
    elif "fourth" in spokenWord:
        PressKey(VK_4)
    elif "fifth" in spokenWord:
        PressKey(VK_5)
    elif "sixth" in spokenWord:
        PressKey(VK_6)
    elif "seventh" in spokenWord:
        PressKey(VK_7)
    elif "eigth" in spokenWord:
        PressKey(VK_8)
    elif "ninth" in spokenWord:
        PressKey(VK_9)


def ProcessInput(spokenWord):
    print("--------------------------------")
    print("spokenWord : -", spokenWord,"-")
    
    if "stop" in spokenWord or "brake" in spokenWord or "stop everything" in spokenWord:
        ReleaseAllKeys() 
        PressKey(VK_SPACEBAR)
        time.sleep(0.7)
        ReleaseAllKeys()

    elif "straight left" in spokenWord :
        ReleaseAllKeys() 
        PressKey(VK_A)
        PressKey(VK_W)
        time.sleep(0.7)
        ReleaseKey(VK_A)
    
    elif "straight right" in spokenWord :
        ReleaseAllKeys() 
        PressKey(VK_D)
        PressKey(VK_W)
        time.sleep(1)
        ReleaseKey(VK_D)

    elif "go straight" in spokenWord :
        ReleaseAllKeys() 
        PressKey(VK_W)

    elif "turn left" in spokenWord or "go left" in spokenWord:
        ReleaseAllKeys() 
        PressKey(VK_W)
        PressKey(VK_A)
        time.sleep(2)
        ReleaseKey(VK_A)
        ReleaseKey(VK_W)

    elif "turn right" in spokenWord or "go right" in spokenWord:
        ReleaseAllKeys() 
        PressKey(VK_W)
        PressKey(VK_D)
        time.sleep(2)
        ReleaseKey(VK_D)
        ReleaseKey(VK_W)

    elif "reverse the car" in spokenWord  or  "reverse" in spokenWord or "go back" in spokenWord:
        ReleaseAllKeys() 
        PressKey(VK_S)
        time.sleep(2)
        ReleaseKey(VK_S)

    elif "get out" in spokenWord or "get in" in spokenWord:
        print("in get out/in ")
        ReleaseAllKeys()
        PressKey(VK_F)
        time.sleep(1)
        ReleaseAllKeys()

    elif "item" in spokenWord and "select" in spokenWord:
        PressAndReleaseNumberKey(spokenWord)
        ReleaseAllKeys() 

    elif "shoot" in spokenWord or "fire" in spokenWord:
        PressKey(VK_L)

    elif "point up" in spokenWord :
        mouse = Mouse()
        x,y = mouse.get_position()
        mouse.move_mouse((x, y+10))

    elif "point down" in spokenWord :
        mouse = Mouse()
        x,y = mouse.get_position()
        mouse.move_mouse((x, y-10))

    elif "point left" in spokenWord :
        mouse = Mouse()
        x,y = mouse.get_position()
        mouse.move_mouse((x-10, y))

    elif "point right" in spokenWord :
        mouse = Mouse()
        x,y = mouse.get_position()
        mouse.move_mouse((x+10, y))
        
    elif "focus" in spokenWord or "Focus" in spokenWord or "point" in spokenWord :
        ReleaseAllKeys() 
        PressKey(VK_K)
     
