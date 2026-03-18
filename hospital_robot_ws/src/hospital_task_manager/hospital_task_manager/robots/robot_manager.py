import threading
import time

class RobotManager:

    def __init__(self, robots):
        self.robots = robots

    def get_idle_robots(self):
        return [r for r in self.robots if r.status == "IDLE"]

    def assign_task(self, robot, task):

        robot.status = "BUSY"
        robot.current_task = task

        print(robot.name, "started task:", task.task_type)

        # start task execution in background
        thread = threading.Thread(target=self.execute_task, args=(robot,))
        thread.start()

    def execute_task(self, robot):

        # simulate robot working
        time.sleep(5)

        print(robot.name, "finished task")

        robot.status = "IDLE"
        robot.current_task = None
