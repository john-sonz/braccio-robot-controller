import copy

class Position:
    def __init__(self, base, shoulder, elbow, wrist, wrist_rotation, gripper):
        self.angles = [0, 0, 0, 0, 0, 0]
        self.angles[0] = base
        self.angles[1] = shoulder
        self.angles[2] = elbow
        self.angles[3] = wrist
        self.angles[4] = wrist_rotation
        self.angles[5] = gripper

    def set(self, joint_number, value):
        self.angles[joint_number] = min(max(value, 0), 180)
        return self

    def get(self, joint_number):
        return self.angles[joint_number]

    def add(self, joint_number, value):
        return self.set(joint_number, self.angles[joint_number] + value)

    def copy(self):
        return copy.deepcopy(self)

    def to_string(self):
        result = ""
        separator = ""
        for angle in self.angles:
            result = result + separator + str(angle)
            separator = ","
        return result