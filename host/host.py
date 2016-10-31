# https://pypi.python.org/pypi/PyBluez
import bluetooth
import time
import guitarMotionUtils

# Commands that can be sent to the server
COMMAND_NONE          = 0x00
COMMAND_JOLT_UP       = 0x01
COMMAND_JOLT_DOWN     = 0x02
COMMAND_NECK_UP       = 0x03
COMMAND_NECK_STRAIGHT = 0x04
COMMAND_NECK_DOWN     = 0x05
COMMANDS = 6

COMMAND_STRING = {
    COMMAND_NONE          : "COMMAND_NULL",
    COMMAND_JOLT_UP       : "COMMAND_JOLT_UP",
    COMMAND_JOLT_DOWN     : "COMMAND_JOLT_DOWN",
    COMMAND_NECK_UP       : "COMMAND_NECK_UP",
    COMMAND_NECK_STRAIGHT : "COMMAND_NECK_STRAIGHT",
    COMMAND_NECK_DOWN     : "COMMAND_NECK_DOWN"
}

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
        try:
            print ("HostBluetoothServer: Setting up bluetooth server")
            uuid = "5E66F20D-7079-472C-B8C3-97221B7C67F7"
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("",bluetooth.PORT_ANY))
            self.server_socket.listen(1)
            port = self.server_socket.getsockname()[1]

            bluetooth.advertise_service( self.server_socket, "GuitarMotionServer",
                                         service_id = uuid,
                                         service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],
                                         profiles = [ bluetooth.SERIAL_PORT_PROFILE ] 
                                       )
            print ("HostBluetoothServer: Waiting connection on RFCOMM channel {}".format(port))

            self.client_sock, client_info = self.server_socket.accept()

            print ("HostBluetoothServer: Accepted connection from {}".format(client_info))
        except:
            print ("Não foi possivel inicializar o servidor bluetooth")
        

    # Wait for a device to send a command and returns it
    def ReadCommand(self):
        data = self.client_sock.recv(1)
        if len(data) > 0:
            command = int(bytes(data)[len(data)-1])
        else:
            command = COMMAND_NONE
            
        return command
		
    def Close():
        self.serverSocket.close() 

# Each state in the FSM. Has a tone and the the transitions are COMMANDS
class RockSmithState(object):
    def __init__(self, name="Unknown", tone=TONE[0]):
        self.name = name
        self.tone = tone
        self.transitions = []
        # By default, no command will change the state
        for i in range (0, COMMANDS):
            self.transitions.append(self)
		
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
            guitarMotionUtils.PressKey(new_state.GetTone())
            print("RockSmithFSM: Changing from " + self.current_state.name + " to " + new_state.name)
            self.current_state = new_state
        print("Recived command: {}".format(COMMAND_STRING[command]))
            
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
        command = bt_server.ReadCommand()
        rocksmith_manager.Command(command)
    bt_server.Close()
	
