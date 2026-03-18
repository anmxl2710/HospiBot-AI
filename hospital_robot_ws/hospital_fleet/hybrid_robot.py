from robot import Robot

class HybridRobot(Robot):

    def __init__(self, name, x, y):
        super().__init__(name, "hybrid", x, y)

    def clean(self, location):
        print(self.name, "cleaning", location)

    def collect_sample(self, location):
        print(self.name, "collecting sample from", location)
