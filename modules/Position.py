class Position:
    def __init__(self, base, shoulder, elbow, wrist, wrist_rotation, gripper):
        self.angels = [0, 0, 0, 0, 0, 0]
        self.angels[0] = base
        self.angels[1] = shoulder
        self.angels[2] = elbow
        self.angels[3] = wrist
        self.angels[4] = wrist_rotation
        self.angels[5] = gripper

    def set(self, joint_number, value):
        self.angels[joint_number] = min(max(value, 0), 180)

    def get(self, joint_number):
        return self.angels[joint_number]

    def add(self, joint_number, value):
        self.set(joint_number, self.angels[joint_number] + value)

    def to_string(self):
        result = ""
        separator = ""
        for angel in self.angels:
            result = result + separator + str(angel)
            separator = ","
        return result