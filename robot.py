import sys
import math
import requests
import time
sys.path.insert(0, "./modules")

from Braccio import Braccio
from Position import Position

instruction_url = "http://localhost:3000/"
defualt_payload = ["robot"]

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

def fetch_instruction():    
    global stop
    global robot
    r = None
    try:
        r = requests.post(instruction_url, json=defualt_payload, timeout=15)
    except Exception as e:
        print(e)
        time.sleep(5)
        return
    
    if r.status_code != 200:
        return
    instruction = r.json()
        
    action = instruction["type"]
    
    if action is None:
        return

    x, y, cam_dist = instruction["coords"]

    if action == "exit" or action == "quit":
        stop = True
        robot.reset(speeds["s"], delay = 2)
        robot.power_off()
    
    elif action.startswith("point"):
        robot.reset(speeds["s"])            
        
        target_angle = get_rotation_angle(int(x), int(y))            
        point_pos =  point_pos_default.copy().set(0, target_angle)
        robot.move_to_position(point_pos, speeds["m"])
    
    elif action.startswith("grab"):            
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
        else:
            resp = requests.post(instruction_url + "error", json={"msg": "Error during performing the instruction", "instruction": instruction })            
            time.sleep(3)
            return

        pos.add(1, 20).set(0, target_angle)
        robot.move_to_position(pos, speeds["s"], delay=1.5)
        pos.add(1, -20)
        robot.move_to_position(pos, speeds["s"])
        robot.close_gripper(delay=1)
        robot.reset(speeds["vs"])

    elif action.startswith("reset"):
        robot.reset(speeds["s"])

robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else "COM1", start_pos)

if __name__ == "__main__":
    robot.power_on()
    while not stop:
        fetch_instruction()