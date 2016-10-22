# https://pypi.python.org/pypi/PyBluez
import bluetooth
import time # Tempo for demo
# Key press simulation
# http://stackoverflow.com/questions/13564851/generate-keyboard-events
import ctypes
from ctypes import wintypes
import time
import random

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_KEYBOARD = 1

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

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
    ReleaseKey(hexKeyCode) # Not sure if this is needed

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
	

#### End of copied code #####


# Commands that can be sent to the server
COMMAND_NULL          = 0x0000
COMMAND_JOLT_UP       = 0x0001
COMMAND_JOLT_DOWN     = 0x0002
COMMAND_NECK_UP       = 0x0003
COMMAND_NECK_STRAIGHT = 0x0004
COMMAND_NECK_DOWN     = 0x0005
COMMANDS = 5
# The key bindings that change the tone in-game.
# Should be mapped to hexadecimal using this table: https://msdn.microsoft.com/en-us/library/dd375731
TONE = []
TONE.append(0x31)
TONE.append(0x32)
TONE.append(0x33)
TONE.append(0x34)

# The blueprint host, will read commands from the devices
class HostBluetoothServer(object):
    def __init__(self):
        '''
        print ("HostBluetoothServer: Setting up bluetooth server")
        self.name = "rocksmith_server"
        # A random uuid, generated by https://www.famkruithof.net/uuid/uuidgen
        # The same uuid should be used in the device's bt options
        self.uuid = "5E66F20D-7079-472C-B8C3-97221B7C67F7"
        self.serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = bluetooth.PORT_ANY
        self.serverSocket.bind(("",port))
        '''

    # Wait for a device to send a command and returns it
    def WaitForNewCommand(self):
        '''
        print ("HostBluetoothServer: Listening for connections on port: ", port)
        serverSocket.listen(1)
        port=serverSocket.getsockname()[1]
    
        bluetooth.advertise_service( serverSocket, "SampleServer",
                           service_id = self.uuid,
                           service_classes = [ self.uuid, bluetooth.SERIAL_PORT_CLASS ],
                           profiles = [ bluetooth.SERIAL_PORT_PROFILE ] 
                           )
    
        inputSocket, address=serverSocket.accept()
        print ("HostBluetoothServer: Got connection with" , address)
        data = inputSocket.recv(1024)
        print ("HostBluetoothServer: received [%s] \n " % data)
        inputSocket.close()
        '''
        time.sleep(3)
        return COMMAND_JOLT_UP # TEMP!!!!
		
    def Close():
        self.serverSocket.close() 

# Each state in the FSM. Has a tone and the the transitions are COMMANDS
class RockSmithState(object):
    def __init__(self, name="Unknown", tone=TONE[0]):
        self.name = name
        self.tone = tone
        self.transitions = {}
        # By default, no command will change the state
        for i in range (0, COMMANDS + 1):
            self.transitions[i] = self
		
    # Set the transaction for this state
    def SetStateOnCommand(self, state, command):
        self.transitions[command] = state
		
    # Given a command, returns the next state
    def GetStateOnCommand(self, command):	
        return self.transitions[command]
    
    # Which tone is being used in this state
    def SetTone(self, tone):
        self.tone = tone

    # Which tone is being used in this state
    def GetTone(self):
        return self.tone
    
# FSM that controls the tones
class RockSmithFSM(object):
    def __init__(self):
        self.current_state = None
        self.states = []
        for i in range(0,4):
            self.states.append(RockSmithState())
        
        # TODO: Make non-hardcoded
        # Simple using COMMAND_JOLT_UP to toggle between Clean and Overdrive
        self.states[0] = RockSmithState("Clean", TONE[0])
        self.states[1] = RockSmithState("Overdrive", TONE[1])
        self.states[0].SetStateOnCommand(self.states[1], COMMAND_JOLT_UP)
        self.states[1].SetStateOnCommand(self.states[0], COMMAND_JOLT_UP)
        self.current_state = self.states[0]

    def Command(self, command):
        new_state = self.current_state.GetStateOnCommand(command)
        if new_state != self.current_state:
            print("RockSmithFSM: Changing from " + self.current_state.name + " to " + new_state.name)
            self.current_state = new_state
            PressKey(self.current_state.GetTone())

            
class RockSmithManager(object):
    def __init__(self):
        self.fsm = RockSmithFSM()
		
    def IsGameRunning(self):
        # TODO: Detect if the game is running
        return True

    def Command(self, command):
        self.fsm.Command(command)
		

if __name__ == "__main__":
    bt_server = HostBluetoothServer()
    rocksmith_manager = RockSmithManager()
    while (rocksmith_manager.IsGameRunning()):
        command = bt_server.WaitForNewCommand()
        rocksmith_manager.Command(command)
    bt_server.Close()
	