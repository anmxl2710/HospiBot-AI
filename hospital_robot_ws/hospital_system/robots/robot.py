class Robot:
    def __init__(self, robot_id, location):
        self.robot_id = robot_id
        self.location = location
        self.status = "idle"

    def bid_for_task(self, task_location):
        distance = abs(self.location - task_location)
        return distance

    def assign_task(self, task):
        self.status = "busy"
        print(f"{self.robot_id} assigned to {task}")
