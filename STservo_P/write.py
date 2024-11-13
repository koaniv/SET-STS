import os
import sys

# Cross-platform getch function for keyboard input
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# Import STServo SDK
from STservo import *  # Replace with the correct path if necessary

# Default settings
STS_ID = 2  # Servo ID to control
BAUDRATE = 1000000  # STServo default baudrate
DEVICENAME = 'COM8'  # Port to use
STS_MINIMUM_POSITION_VALUE = 0  # Minimum position value
STS_MAXIMUM_POSITION_VALUE = 4095  # Maximum position value
STS_MOVING_SPEED = 2400  # Servo moving speed
STS_MOVING_ACC = 50  # Servo moving acceleration

# Angle to move to (20 units)
angle_to_move = 20

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = sts(portHandler)

# Open port
if portHandler.openPort():
    print("[INFO] Succeeded to open the port")
else:
    print("[ERROR] Failed to open the port. Exiting...")
    sys.exit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("[INFO] Succeeded to change the baudrate")
else:
    print("[ERROR] Failed to change the baudrate. Exiting...")
    sys.exit()

# Move servo to the specified angle
print(f"[INFO] Moving Servo ID {STS_ID} to {angle_to_move} units...")
sts_comm_result, sts_error = packetHandler.WritePosEx(STS_ID, angle_to_move, STS_MOVING_SPEED, STS_MOVING_ACC)
if sts_comm_result != COMM_SUCCESS:
    print(f"[ERROR] {packetHandler.getTxRxResult(sts_comm_result)}")
if sts_error != 0:
    print(f"[ERROR] {packetHandler.getRxPacketError(sts_error)}")
else:
    print(f"[INFO] Servo ID {STS_ID} moved successfully to {angle_to_move} units.")

# Close port
portHandler.closePort()
print("[INFO] Port closed successfully.")
