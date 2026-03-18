import math

class Robot:

    def __init__(self, name, capability, battery, location):

        self.name = name
        self.capability = capability
        self.battery = battery
        self.location = location

        self.status = "IDLE"
        self.current_task = None

    def distance_to(self, location):

        x1, y1 = self.position
        x2, y2 = location

        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def compute_bid(self, task):

        cost = 0

        # Capability check
        if task.task_type != self.robot_type and self.robot_type != "hybrid":
            cost += 100

        # Distance cost
        cost += self.distance_to(task.location)

        # Battery cost
        cost += (100 - self.battery) * 0.1

        return cost

    def __str__(self):
        return f"{self.name} ({self.robot_type})"
