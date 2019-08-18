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
        inp = input("Enter quit or exit to stop: ")
        if inp == "quit" or inp == "exit":
            stop = True
            return



if __name__ == "__main__":

    start_pos = Position(0, 65, 70, 45, 90, 50)
    positions = [x * 20 for x in range(0, 10)] + [ 180 - (x * 20) for x in range(1, 9)]

    t = threading.Thread(target=read_input)
    t.start()

    robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else "COM1", start_pos)
    robot.power_on()    
    
    while not stop:    
        for pos in positions:
            if stop: break
            if (pos // 20) % 2 == 0: robot.open_gripper()
            else: robot.close_gripper()
            robot.move_joint(0, pos, 20)

    robot.reset(40, delay = 2)
    robot.power_off()