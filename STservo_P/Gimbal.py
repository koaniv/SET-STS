import typing
from STservo import sts
from STservo import protocol_packet_handler
from STservo.port_handler import PortHandler
from STservo.stservo_def import COMM_SUCCESS

# rotation left right
MAX_RIGHT_POSITION = 180
MAX_LEFT_POSITION = -180

# servo precision = 4096 = [0, 4095]
STS_MIN_POSITION = 0
STS_MID_POSITION = 2047
STS_MAX_POSITION = 4095
STS_DEFAULT_SPEED = 2400
STS_DEFAULT_ACC = 50

# serial data link
BAUDRATE = 1000000  # STServo default baudrate : 1000000


class Gimbal:

    def __init__(self, port: str = 'COM5', horizontal_servo_id: int = 1, vertical_servo_id: int = 2):
        self.x_servo_id = horizontal_servo_id
        self.y_servo_id = vertical_servo_id
        self.port = PortHandler(port)
        self.port.setBaudRate(BAUDRATE)
        self.sts = sts(self.port)

    # def position_x(self):

    def start(self):
        if not self.port.openPort():
            raise Exception("Could not establish connection with Servo Driver Board")

    def shutdown(self):
        self.port.closePort()

    def calibrate(self, speed: float = 1, acc: float = 1):
        requested_speed = int((4095 * speed) / 360)
        requested_acc = 0 if acc == 0 else int((4095 * acc) / 360)

        self.sts.WritePosEx(self.x_servo_id, STS_MID_POSITION, requested_speed, requested_acc)
        self.sts.WritePosEx(self.y_servo_id, STS_MID_POSITION, requested_speed, requested_acc)


    def __move(self, servo_id: int, angle: float, speed: float = 1, acc: float = 1):
        current_position, result, error = self.sts.ReadPos(servo_id)
        if result != COMM_SUCCESS:
            raise Exception(self.sts.getTxRxResult(result))

        requested_position = current_position + int((4095 * angle) / 360)
        if requested_position < 0:
            requested_position = 0

        if requested_position > STS_MAX_POSITION:
            requested_position = STS_MAX_POSITION

        requested_speed = int((4095 * speed) / 360)
        requested_acc = 0 if acc == 0 else int((4095 * acc) / 360)

        self.sts.WritePosEx(servo_id, requested_position, requested_speed, requested_acc)

    def move_x(self, angle: float, speed: float = 1, acc: float = 1) -> None:
        """
        Horizontal move. Turns horizontal servo by specified angle.
        Default speed is 1 degree per second.
        Default acceleration is 1 degree per second.

        :param angle: [-180, 180]
        :param speed: angle speed / angle per second
        :param acc: angle acceleration per second
        :return:
        """
        self.__move(self.x_servo_id, angle, speed, acc)

    def move_y(self, angle: float, speed: float = 1, acc: float = 1) -> None:
        """
        Vertical move. Turns vertical servo by specified angle.
        Default speed is 1 degree per second.
        Default acceleration is 1 degree per second.


        :param angle: [-180, 180]
        :param speed: angle speed / angle per second
        :param acc: angle acceleration per second
        :return:
        """
        self.__move(self.y_servo_id, angle, speed, acc)

    def turn_on_wheel_mode(self):
        '''
        Be careful, there is no way to turn off wheel mode.
        Wheel mode can be removed by a re-boot only. (PowerOff / PowerOn).

        Transforms servo into a wheel. It will spin up wheel with a fixed speed.
        Speed is controlled via sts.WriteSpec function:

        self.sts.WriteSpec(self.x_servo_id, STS_DEFAULT_SPEED, STS_DEFAULT_ACC)
        self.sts.WriteSpec(self.y_servo_id, STS_DEFAULT_SPEED, STS_DEFAULT_ACC)

        :return:
        '''
        self.sts.WheelMode(self.x_servo_id)
        self.sts.WheelMode(self.y_servo_id)

    def __rotate(self, servo_id: int, speed: float = 1, acc: float = 1):
        requested_speed = int((4095 * speed) / 360)
        requested_acc = 0 if acc == 0 else int((4095 * acc) / 360)

        self.sts.WriteSpec(self.x_servo_id, requested_speed, requested_acc)


    def rotate_x(self, speed: float = 1, acc: float = 1):
        self.__rotate(self.x_servo_id, speed, acc)

    def rotate_y(self, speed: float = 1, acc: float = 1):
        self.__rotate(self.y_servo_id, speed, acc)