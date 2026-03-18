class Robot:

    def __init__(self, name, robot_type, x, y):
        self.name = name
        self.robot_type = robot_type
        self.x = x
        self.y = y
        self.status = "idle"

    def assign_task(self, task):
        self.status = "busy"
        print(self.name, "assigned:", task)

    def complete_task(self):
        self.status = "idle"
        print(self.name, "completed task")
