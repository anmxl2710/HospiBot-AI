from cleaner_robot import CleanerRobot
from sample_robot import SampleRobot
from hybrid_robot import HybridRobot

from fleet_manager import FleetManager
from task_manager import TaskManager


fleet = FleetManager()
tasks = TaskManager()

r1 = CleanerRobot("cleaner1",4,9)
r2 = CleanerRobot("cleaner2",2,3)

r3 = SampleRobot("sample1",1,5)
r4 = SampleRobot("sample2",7,2)

r5 = HybridRobot("hybrid1",6,6)

fleet.add_robot(r1)
fleet.add_robot(r2)
fleet.add_robot(r3)
fleet.add_robot(r4)
fleet.add_robot(r5)

tasks.add_task("Clean ICU")
tasks.add_task("Collect Blood Sample")
tasks.add_task("Clean Ward")

fleet.assign_tasks(tasks)
