import json
import math
import requests
import sys
import time
sys.path.insert(0, "./modules")

from Braccio import Braccio
from Position import Position

with open('config.json', 'r') as f:
    config = json.load(f)

instruction_url, error_url = config["instruction_url"], config["error_url"]
default_payload = config["default_payload"]
x_correction, y_correction = config["coords_correction"].values()
close_range, far_range = config["close_range"], config["far_range"]

start_pos = Position(90, 90, 90, 90, 90, 65)
grab_pos_close_start = Position(90, 100, 0, 15, 90, 0)
grab_pos_close_end = Position(90, 40, 60, 40, 90, 0)
grab_pos_far_start = Position(90, 30, 0, 160, 90, 0)
grab_pos_far_end = Position(90, 15, 47, 130, 90, 0)

speeds = {
    "vs": 20,  # very slow
    "s": 40,   # slow
    "m": 60,   # medium
    "f": 80,   # fast
    "vf": 100, # very fast
}

stop = False

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

def pos_from_coords(x, y):
    x, y = [int(x) + x_correction, int(y) + y_correction]
    distance = distance_from_origin(x,y) // 10
    target_angle = get_rotation_angle(x, y)
    pos = None
    if distance >= close_range[0] and distance < close_range[1]:
        p = (distance - close_range[0]) * 100/(close_range[1] - close_range[0])
        pos = calc_grab_pos(grab_pos_close_start.copy(), grab_pos_close_end.copy(), p)

    elif distance >= far_range[0] and distance <= far_range[1]:
        p = (distance - far_range[0]) * 100 / (far_range[1] - far_range[0])
        pos = calc_grab_pos(grab_pos_far_start.copy(), grab_pos_far_end.copy(), p)

    if pos is not None: pos.set(0, target_angle)
    return pos

def send_error_and_sleep(instr, sleep_time=3):
    requests.post(error_url, json={"msg": "Error during performing the instruction", "instruction": instr })
    time.sleep(sleep_time)

def fetch_instruction():
    global stop
    global robot
    r = None
    try:
        r = requests.post(instruction_url, json=default_payload, timeout=30)
    except Exception as e:
        robot.reset(speeds["vs"])
        print(e)
        time.sleep(3)
        return

    print(r.status_code, r.text)

    if r.status_code != 200:
        return
    instruction = r.json()

    action = instruction["type"]

    if action is None:
        return

    x, y, _ = instruction["coords"] if "coords" in instruction else [0, 0, 0]

    if action == "exit" or action == "quit":
        stop = True
        robot.reset(speeds["s"], delay = 2)
        robot.power_off()

    elif action == "point" or action == "move over":
        point_pos = pos_from_coords(x, y)
        if point_pos is None:
            send_error_and_sleep(instruction)
            return

        gripper_pos = robot.get_position().get(5)
        point_pos.add(1, 30).set(5, gripper_pos)
        robot.move_to_position(point_pos, speeds["s"])

    elif action == "grab":
        grab_pos = pos_from_coords(x, y)
        if grab_pos is None:
            send_error_and_sleep(instruction)
            return

        grab_pos.add(1, 20)
        robot.move_to_position(grab_pos, speeds["s"], delay=1.5)
        grab_pos.add(1, -20)
        robot.move_to_position(grab_pos, speeds["s"])
        robot.close_gripper(delay=2)
        grab_pos.add(1, 20).set(5, 72)
        robot.move_to_position(grab_pos, speeds["s"])

    elif action == "drop over":
        drop_pos = pos_from_coords(x, y)
        if drop_pos is None:
            send_error_and_sleep(instruction)
            time.sleep(3)
            return

        drop_pos.add(1, 30).set(5, 72)
        robot.move_to_position(drop_pos, speeds["vs"])
        robot.open_gripper(delay= 1)
        robot.reset(speeds["s"])

    elif action == "drop":
        robot.open_gripper(delay=1)
        robot.reset(speeds["s"])

    elif action == "reset":
        robot.reset(speeds["s"])

robot = Braccio(sys.argv[1] if len(sys.argv) > 1 else config["default_COM"], start_pos)

if __name__ == "__main__":
    robot.power_on()
    robot.reset(speeds["vs"])
    while not stop:
        fetch_instruction()