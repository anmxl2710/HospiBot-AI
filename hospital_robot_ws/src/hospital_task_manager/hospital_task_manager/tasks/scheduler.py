class Scheduler:

    def __init__(self, robot_manager, auction):
        self.robot_manager = robot_manager
        self.auction = auction

    def schedule(self, task):

        robots = self.robot_manager.get_idle_robots()

        if not robots:
            return None

        winner = self.auction.allocate(robots, task)

        if winner:
            self.robot_manager.assign_task(winner, task)

        return winner
