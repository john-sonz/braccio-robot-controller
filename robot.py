import sys
import math
sys.path.insert(0, "./modules")

from Braccio import Braccio
from Position import Position

stop = False

start_pos = Position(90, 90, 90, 90, 90, 65)
point_pos_default = Position(90, 65, 70, 10, 90, 40)
grab_pos_close_start = Position(90, 80, 20, 0, 90, 0)
grab_pos_close_end = Position(90, 50, 40, 50, 90, 0)
grab_pos_far_start = Position(90, 40, 0, 150, 90, 0)
grab_pos_far_end = Position(90, 15, 50, 130, 90, 0)

close_range = (5, 25)
far_range = (25, 35)

speeds = {
    "vs": 20,  # very slow
    "s": 40,   # slow
    "m": 60,   # medium
    "f": 80,   # fast 
    "vf": 100, # very fast
}

def get_rotation_angle(x, y):
    if x == 0: return 90
    angle = math.degrees(math.atan(y/x))
    return int(180 - angle if angle > 0 else -angle)

def distance_from_origin(x,y):
    return (x**2 + y**2)**(1/2)

def calc_grab_pos(p1, p2, percent):        
    differences = [int((a - b) * percent // 100) for (a, b) in zip(p1.angles, p2.angles)]
    new_angles = [ a - b for (a, b) in zip(p1.angles, differences)]
    return Position(*new_angles)

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
        
        elif inp.startswith("grab "):
            [_ , x, y] = inp.split(" ")
            robot.reset(speeds["s"])
            x, y = [int(x), int(y)]
            distance = distance_from_origin(x,y) // 10
            target_angle = get_rotation_angle(x, y)
            pos = None
            if distance >= close_range[0] and distance < close_range[1]:
                p = (distance - close_range[0]) * 100/(close_range[1] - close_range[0])
                pos = calc_grab_pos(grab_pos_close_start.copy(), grab_pos_close_end.copy(), p)
                

            elif distance >= far_range[0] and distance <= far_range[1]:
                p = (distance - far_range[0]) * 100 / (far_range[1] - far_range[0])
                pos = calc_grab_pos(grab_pos_far_start.copy(), grab_pos_far_end.copy(), p)                

            pos.add(1, 20).set(0, target_angle)
            robot.move_to_position(pos, speeds["s"], delay=1.5)
            pos.add(1, -20)
            robot.move_to_position(pos, speeds["s"])
            robot.close_gripper(delay=1)
            robot.reset(speeds["vs"])

        elif inp.startswith("reset"):
            robot.reset(speeds["s"])

robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else "COM1", start_pos)

if __name__ == "__main__":
    robot.power_on()
    read_input()