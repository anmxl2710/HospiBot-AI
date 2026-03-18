from robot import Robot

class SampleRobot(Robot):

    def __init__(self, name, x, y):
        super().__init__(name, "sample", x, y)

    def collect_sample(self, location):
        print(self.name, "collecting sample from", location)
