import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import serial.tools.list_ports
import logging
from STservo import PortHandler, sts
from STservo.stservo_def import COMM_SUCCESS, STS_END

app = Flask(__name__)
socketio = SocketIO(app)

# Setup logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Global variables
port_handler = None
packet_handler = None
connected_port = None

# Address for the servo ID
SERVO_ID_ADDRESS = 5  # This is the correct address for the servo ID

def scan_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_to_port(port_name):
    global port_handler, packet_handler
    port_handler = PortHandler(port_name)
    packet_handler = sts(port_handler)

    if port_handler.openPort() and port_handler.setBaudRate(1000000):
        print(f"Connected to {port_name}")
        return True
    else:
        print(f"Failed to connect to {port_name}")
        return False

def get_all_servo_info():
    servo_info = []
    for servo_id in range(1, 10):  # Check IDs from 1 to 9 as an example range
        model_number, result, error = packet_handler.ping(servo_id)
        voltage = packet_handler.read1ByteTxRx(servo_id, 62)
        if result == COMM_SUCCESS:
            info = {
                "id": servo_id,
                "model_number": model_number
            }
            servo_info.append(info)
            print(f"Servo {servo_id} found: Model Number {model_number} Voltage: {voltage}")
        else:
            print(f"Servo {servo_id} not found. Error: {packet_handler.getTxRxResult(result)}")
    return servo_info

def log_message(message):
    logging.info(message)
    socketio.emit('log', {'message': message})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_ports', methods=['GET'])
def scan_ports_endpoint():
    ports = scan_ports()
    return jsonify(ports)

@app.route('/connect_port', methods=['POST'])
def connect_port():
    global connected_port
    port_name = request.json['port']
    if connect_to_port(port_name):
        connected_port = port_name
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/get_servo_info', methods=['GET'])
def get_servo_info_endpoint():
    if not connected_port:
        return jsonify([])
    servo_info = get_all_servo_info()
    return jsonify(servo_info)

@app.route('/change_servo_id', methods=['POST'])
def change_servo_id():
    old_id = int(request.json['old_id'])
    new_id = int(request.json['new_id'])

    # Check if the new ID is within the valid range
    if new_id < 1 or new_id > 252:  # Assuming valid IDs are between 1 and 252
        print(f"Failed to change ID: {new_id} is out of the valid range.")
        return jsonify(success=False, error="Invalid ID range")

    # Use the correct address (5) to change the servo ID
    result, error = packet_handler.write1ByteTxRx(old_id, SERVO_ID_ADDRESS, new_id)
    if result != COMM_SUCCESS:
        print(f"Failed to change Servo ID from {old_id} to {new_id}. Error: {packet_handler.getTxRxResult(result)}")
        return jsonify(success=False, error=packet_handler.getTxRxResult(result))
    
    if error != 0:
        print(f"Error occurred while changing Servo ID: {packet_handler.getRxPacketError(error)}")
        return jsonify(success=False, error=packet_handler.getRxPacketError(error))

    print(f"Successfully changed Servo ID from {old_id} to {new_id}")

    # Emit a SocketIO event to refresh the servo list
    socketio.emit('refresh_servo_list')

    return jsonify(success=True)

@app.route('/move_servo', methods=['POST'])
def move_servo():
    servo_id = int(request.json['servo_id'])
    step = int(request.json['angle'])
    print(f"[INFO] Moving Servo ID {servo_id} to {step} units...")
    for i in range(10):
        sts_comm_result, sts_error = packet_handler.WritePosEx(servo_id, step*i, 100, 20)
        if sts_comm_result != COMM_SUCCESS:
            print(f"[ERROR1] {packet_handler.getTxRxResult(sts_comm_result)}")
        if sts_error != 0:
            print(f"[ERROR] {packet_handler.getRxPacketError(sts_error)}")
        else:
            print(f"[INFO] Servo ID {servo_id} moved successfully to {step*i} units.")
        time.sleep(2)
    
    return jsonify(success=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)