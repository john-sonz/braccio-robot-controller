import sys
import time
import threading
sys.path.insert(0, "./modules")

from Braccio import Braccio
from Position import Position

stop = False

def read_input():
    global stop
    while True:
        inp = input("Enter q to exit: ")
        if inp == "q":
            stop = True
            print(stop)
            return


start = Position(0, 65, 70, 45, 90, 50)
safe = Position(90, 90, 90, 90, 90, 50)

robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else "COM1", safe)
robot.power_on()

robot.move_to_position(start, 30)

positions = [x * 20 for x in range(0, 10)] + [ 180 - (x * 20) for x in range(1, 9)]

stop = False

t = threading.Thread(target=read_input)
t.start()

while not stop:    
    for pos in positions:
        if stop: break
        if (pos // 20) % 2 == 0: robot.open_gripper()
        else: robot.close_gripper()
        robot.move_joint(0, pos, 20)

robot.move_to_position(safe, 40, delay = 3)
robot.power_off()
