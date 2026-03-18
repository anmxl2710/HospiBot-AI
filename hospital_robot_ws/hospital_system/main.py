from robots.robot import Robot
from ui.dashboard import Dashboard

robots = [
    Robot("Robot1", 2),
    Robot("Robot2", 8),
    Robot("Robot3", 15)
]

Dashboard(robots)
