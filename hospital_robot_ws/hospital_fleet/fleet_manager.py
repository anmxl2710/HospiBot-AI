class FleetManager:

    def __init__(self):
        self.robots = []

    def add_robot(self, robot):
        self.robots.append(robot)

    def assign_tasks(self, task_manager):

        for robot in self.robots:

            if robot.status == "idle":

                task = task_manager.get_task()

                if task:
                    robot.assign_task(task)
