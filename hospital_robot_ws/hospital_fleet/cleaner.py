from robot import Robot

class CleanerRobot(Robot):

    def __init__(self, name, x, y):
        super().__init__(name, "cleaner", x, y)

    def clean(self, location):
        print(self.name, "cleaning", location)
