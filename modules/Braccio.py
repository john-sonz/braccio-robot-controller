import serial
import time
import copy
from Position import Position

class Braccio:
    def __init__(self, serial_port, position):
        self.port = serial.Serial(serial_port, 115200, timeout=5)
        self._position = position
        time.sleep(3)

    def write(self, string):        
        self.port.write(string.encode())
        self.port.readline()

    def power_off(self):
        self.write('0\n')

    def power_on(self):        
        self.write('1\n')
        self.move_to_position(self._position, 30)

    def get_position(self):
        return copy.deepcopy(self._position)

    def move_to_position(self, position, speed, delay = 0, cb = None):
        self.write('P' + position.to_string() + ',' + str(speed) + '\n')
        self._position = position
        if cb is not None: cb(position)
        time.sleep(delay)

    def move_joint(self, joint_number, value, speed, delay = 0, cb = None):
        self._position.set(joint_number, value)
        self.move_to_position(self._position, speed, delay, cb)
    
    def open_gripper(self, speed = 150, delay = 0 , cb = None):
        self.move_joint(5, 0, speed, delay, cb)
    
    def close_gripper(self, percent = 1, speed = 150, delay = 0 , cb = None):
        angle = int(percent * 70)
        self.move_joint(5, angle, speed, delay, cb)