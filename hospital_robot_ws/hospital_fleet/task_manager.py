class TaskManager:

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_task(self):

        if len(self.tasks) > 0:
            return self.tasks.pop(0)

        return None
