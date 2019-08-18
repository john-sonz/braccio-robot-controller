import sys
import math
sys.path.insert(0, "./modules")

from Braccio import Braccio
from Position import Position

stop = False
start_pos = Position(90, 90, 90, 90, 90, 65)
point_pos_default = Position(90, 65, 70, 10, 90, 40)

def read_input():    
    global stop
    global robot

    while not stop:
        inp = input("> ")
        if inp == "exit" or inp == "quit":
            stop = True
            robot.reset(40, delay = 2)
            robot.power_off()
        elif inp.startswith("point "):
            robot.reset(40)

            [_ , x, y] = inp.split(" ")
            x, y = [int(x), int(y)]

            angle = math.degrees(math.atan(y/x))
            target_angle = int(180 - angle if angle > 0 else -angle)
            
            point_pos =  point_pos_default.copy().set(0, target_angle)
            robot.move_to_position(point_pos, 30)
        elif inp.startswith("reset"):
            robot.reset(40)

robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else "COM1", start_pos)

if __name__ == "__main__":
    robot.power_on()
    read_input()