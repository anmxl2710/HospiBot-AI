import math

class AuctionAllocator:

    def allocate(self, robots, task):

        best_robot = None
        best_bid = float("inf")

        # First check specialist robots
        specialist_robots = []

        for robot in robots:
            if robot.status != "IDLE":
                continue

            if robot.capability == task.task_type:
                specialist_robots.append(robot)

        # If specialists exist, only use them
        candidate_robots = specialist_robots if specialist_robots else [
            r for r in robots if r.status == "IDLE" and r.capability == "hybrid"
        ]

        for robot in candidate_robots:

            bid = self.compute_bid(robot, task)

            print(robot.name, "bid:", bid)

            if bid < best_bid:
                best_bid = bid
                best_robot = robot

        return best_robot


    def compute_bid(self, robot, task):

        rx, ry = robot.location
        tx, ty = task.location

        distance = math.sqrt((rx - tx)**2 + (ry - ty)**2)

        battery_penalty = (100 - robot.battery) * 0.1

        bid = distance + battery_penalty

        return bid
