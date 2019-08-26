import sys
import math
sys.path.insert(0, "./modules")

from Braccio import Braccio
from Position import Position

stop = False
start_pos = Position(90, 90, 90, 90, 90, 65)
point_pos_default = Position(90, 65, 70, 10, 90, 40)

speeds = {
    "vs": 20,  # very slow
    "s": 40,   # slow
    "m": 60,  # medium
    "f": 80,   # fast 
    "vf": 100, # very fast
}

def get_rotation_angle(x, y):
    if x == 0: return 90
    angle = math.degrees(math.atan(y/x))
    return int(180 - angle if angle > 0 else -angle)

def read_input():    
    global stop
    global robot

    while not stop:
        inp = input("> ")
        if inp == "exit" or inp == "quit":
            stop = True
            robot.reset(speeds["s"], delay = 2)
            robot.power_off()
        
        elif inp.startswith("point "):
            robot.reset(speeds["s"])
            [_ , x, y] = inp.split(" ")
            
            target_angle = get_rotation_angle(int(x), int(y))
            
            point_pos =  point_pos_default.copy().set(0, target_angle)
            robot.move_to_position(point_pos, speeds["m"])
        
        elif inp.startswith("reset"):
            robot.reset(speeds["s"])

robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else "COM1", start_pos)

if __name__ == "__main__":
    robot.power_on()
    read_input()